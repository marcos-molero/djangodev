from concurrent.futures import ThreadPoolExecutor
import threading
import tempfile
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from core.models import Tmp_transaccion_LK1
from utils.genericos import respuesta_json
from utils.logging import registrar_log, AUDIT_ACCION, AUDIT_CANAL, AUDIT_NIVEL
from .serializers import LoteLK1ResumenSerializer
from .services.cargar_archivo_iso import cargar_archivo_iso
from .services.validar_transacciones_iso import validar_transacciones_iso
from .services.cargar_archivo_lk1 import cargar_archivo_lk1
from .services.validar_transacciones_lk1 import validar_transacciones_lk1


class CargarTransaccionesISOView(APIView):
  """
  Carga el archivo en un temporal para poder someter varias tareas simultaneas
  """  
  def post(self, request):

    # Validar si usuario esta autenticado
    if not request.user.is_authenticated:
      registrar_log(
        mensaje = 'Usuario no autenticado. Acceso denegado.',
        request = request,
        modulo = 'validar.views.CargarTransaccionesISOView',
        accion = AUDIT_ACCION.acceso,
        nivel = AUDIT_NIVEL.error,
        canal = AUDIT_CANAL.autorizacion
      )
      return respuesta_json('Usuario no autenticado. Acceso denegado.', status.HTTP_403_FORBIDDEN)

    # Validar si el usuario esta autorizado a adicionar.
    if not request.user.has_perm('core.cargar_archivo_iso'):
      registrar_log(
        mensaje = 'Usuario sin permiso para cargar archivo ISO.',
        request = request,
        modulo = 'validar.views.CargarTransaccionesISOView',
        accion = AUDIT_ACCION.acceso,
        nivel = AUDIT_NIVEL.warning,
        canal = AUDIT_CANAL.autorizacion
      )
      return respuesta_json('No tiene permiso para cargar archivos ISO.', status.HTTP_403_FORBIDDEN)

    # Registro de petición.
    registrar_log(
      mensaje = 'Inicio de proceso de carga de archivo.',
      request = request,
      modulo = 'validar.views.CargarTransaccionesISOView',
      accion = AUDIT_ACCION.proceso,
      nivel = AUDIT_NIVEL.info,
      canal = AUDIT_CANAL.aplicacion
    )

    lc_archivo = request.FILES.get('archivo')
    if not lc_archivo:
      registrar_log(
        mensaje = 'Debe enviar un archivo adjunto en la petición.',
        request = request,
        modulo = 'validar.views.CargarTransaccionesISOView',
        accion = AUDIT_ACCION.proceso,
        nivel = AUDIT_NIVEL.warning,
        canal = AUDIT_CANAL.aplicacion
      )
      return respuesta_json('Debe enviar un archivo adjunto en la petición.', status.HTTP_400_BAD_REQUEST)
    
    # Guardar el archivo en disco temporal.
    registrar_log(
      mensaje = 'Cargando archivo desde la petición a archivo temporal.',
      request = request,
      modulo = 'validar.views.CargarTransaccionesISOView',
      accion = AUDIT_ACCION.proceso,
      nivel = AUDIT_NIVEL.info,
      canal = AUDIT_CANAL.aplicacion
    )
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
      for chunk in lc_archivo.chunks():
        tmp.write(chunk)
      tmp_path = tmp.name

    # Lanzar la tarea en segundo plano. (sbmjob)
    registrar_log(
      mensaje = 'Lanzando procesos para carga de información.',
      request = request,
      modulo = 'validar.views.CargarTransaccionesISOView',
      accion = AUDIT_ACCION.proceso,
      nivel = AUDIT_NIVEL.info,
      canal = AUDIT_CANAL.aplicacion
    )
    hilo = threading.Thread(target=cargar_archivo_iso, args=(request, tmp_path, request.user.username))
    hilo.start()

    registrar_log(
      mensaje = 'Proceso de carga de archivo sometido.',
      request = request,
      modulo = 'validar.views.CargarTransaccionesISOView',
      accion = AUDIT_ACCION.proceso,
      nivel = AUDIT_NIVEL.info,
      canal = AUDIT_CANAL.aplicacion
    )
    return respuesta_json('Proceso de carga de archivo sometido.')

class EjecutarValidacionesISOView(APIView):
  """
  Ejecuta validaciones en paralelo para procesos del 1 al 10.
  Cada proceso valida sus propias transacciones según el campo 'proceso'.
  Si un proceso falla, se registra el error y los demás continúan.
  """
  def post(self, request):

    # Validar si usuario esta autenticado
    if not request.user.is_authenticated:
      registrar_log(
        mensaje = 'Usuario no autenticado. Acceso denegado.',
        request = request,
        modulo = 'validar.views.CargarTransaccionesISOView',
        accion = AUDIT_ACCION.acceso,
        nivel = AUDIT_NIVEL.error,
        canal = AUDIT_CANAL.autorizacion
      )
      return respuesta_json('Usuario no autenticado. Acceso denegado.', status.HTTP_403_FORBIDDEN)
    
    # Validar si el usuario esta autorizado a adicionar.
    if not request.user.has_perm('core.ejecutar_validaciones_iso'):
      registrar_log(
        mensaje = 'Usuario sin permiso para validar transacciones ISO.',
        request = request,
        modulo = 'validar.views.EjecutarValidacionesView',
        accion = AUDIT_ACCION.acceso,
        nivel = AUDIT_NIVEL.warning,
        canal = AUDIT_CANAL.autorizacion
      )
      return respuesta_json('Usuario sin permiso para validar transacciones.', status.HTTP_403_FORBIDDEN)

    registrar_log(
      mensaje = 'Proceso de validación de archivo sometido.',
      request = request,
      modulo = 'validar.views.EjecutarValidacionesView',
      accion = AUDIT_ACCION.proceso,
      nivel = AUDIT_NIVEL.info,
      canal = AUDIT_CANAL.aplicacion
    )

    proceso = request.data.get('proceso')
    usuario = request.user.username
    resultados_globales = []

    if not proceso:
      registrar_log(
        mensaje = 'No indico un proceso a validar.',
        request = request,
        modulo = 'validar.views.EjecutarValidacionesView',
        accion = AUDIT_ACCION.proceso,
        nivel = AUDIT_NIVEL.info,
        canal = AUDIT_CANAL.aplicacion
      )
      return respuesta_json('No indico un proceso a validar.', status.HTTP_400_BAD_REQUEST)

    with ThreadPoolExecutor(max_workers=settings.GL_PROCESOS_VALIDACION) as executor:
      resultados_globales = list(
        executor.map(lambda i: validar_transacciones_iso(request, i, usuario, proceso), range(1, settings.GL_PROCESOS_VALIDACION + 1))
      )

    registrar_log(
      mensaje = f'Validaciones sometidas para procesos 1 al {settings.GL_PROCESOS_VALIDACION}',
      request = request,
      modulo = 'validar.views.EjecutarValidacionesView',
      accion = AUDIT_ACCION.proceso,
      nivel = AUDIT_NIVEL.info,
      canal = AUDIT_CANAL.aplicacion
    )
    return respuesta_json(
      f'Validaciones sometidas para procesos 1 al {settings.GL_PROCESOS_VALIDACION}', 
      status.HTTP_200_OK,
      {
        'resumen': resultados_globales
      })


class CargarTransaccionesLK1View(APIView):
  """
  Carga el archivo en un temporal para poder someter varias tareas simultaneas

  Archivo fuente: LK1
  """  
  def post(self, request):

    # Validar si usuario esta autenticado
    if not request.user.is_authenticated:
      registrar_log(
        mensaje = 'Usuario no autenticado. Acceso denegado.',
        request = request,
        modulo = 'validar.views.CargarTransaccionesLK1View',
        accion = AUDIT_ACCION.acceso,
        nivel = AUDIT_NIVEL.error,
        canal = AUDIT_CANAL.autorizacion
      )
      return respuesta_json('Usuario no autenticado. Acceso denegado.', status.HTTP_403_FORBIDDEN)

    # Validar si el usuario esta autorizado a adicionar.
    if not request.user.has_perm('core.cargar_archivo_lk1'):
      registrar_log(
        mensaje = 'Usuario sin permiso para cargar archivo LK1.',
        request = request,
        modulo = 'validar.views.CargarTransaccionesLK1View',
        accion = AUDIT_ACCION.acceso,
        nivel = AUDIT_NIVEL.warning,
        canal = AUDIT_CANAL.autorizacion
      )
      return respuesta_json('No tiene permiso para cargar archivos LK1.', status.HTTP_403_FORBIDDEN)

    # Registro de petición.
    registrar_log(
      mensaje = 'Inicio de proceso de carga de archivo LK1.',
      request = request,
      modulo = 'validar.views.CargarTransaccionesLK1View',
      accion = AUDIT_ACCION.proceso,
      nivel = AUDIT_NIVEL.info,
      canal = AUDIT_CANAL.aplicacion
    )

    lc_archivo = request.FILES.get('archivo')
    if not lc_archivo:
      registrar_log(
        mensaje = 'Debe enviar un archivo adjunto en la petición.',
        request = request,
        modulo = 'validar.views.CargarTransaccionesLK1View',
        accion = AUDIT_ACCION.proceso,
        nivel = AUDIT_NIVEL.warning,
        canal = AUDIT_CANAL.aplicacion
      )
      return respuesta_json('Debe enviar un archivo adjunto en la petición.', status.HTTP_400_BAD_REQUEST)
    
    # Guardar el archivo en disco temporal.
    registrar_log(
      mensaje = 'Cargando archivo desde la petición a archivo temporal LK1.',
      request = request,
      modulo = 'validar.views.CargarTransaccionesLK1View',
      accion = AUDIT_ACCION.proceso,
      nivel = AUDIT_NIVEL.info,
      canal = AUDIT_CANAL.aplicacion
    )
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
      for chunk in lc_archivo.chunks():
        tmp.write(chunk)
      tmp_path = tmp.name

    # Cerrar el archivo?
    tmp.close()

    # Lanzar la tarea en segundo plano. (sbmjob)
    registrar_log(
      mensaje = 'Lanzando procesos para carga de información LK1.',
      request = request,
      modulo = 'validar.views.CargarTransaccionesLK1View',
      accion = AUDIT_ACCION.proceso,
      nivel = AUDIT_NIVEL.info,
      canal = AUDIT_CANAL.aplicacion
    )
    hilo = threading.Thread(target=cargar_archivo_lk1, args=(request, tmp_path, request.user.username))
    hilo.start()

    registrar_log(
      mensaje = 'Proceso de carga de archivo LK1 sometido.',
      request = request,
      modulo = 'validar.views.CargarTransaccionesLK1View',
      accion = AUDIT_ACCION.proceso,
      nivel = AUDIT_NIVEL.info,
      canal = AUDIT_CANAL.aplicacion
    )
    return respuesta_json('Proceso de carga de archivo LK1 sometido.')

    # Enviar un correo?

class EjecutarValidacionesLK1View(APIView):
  """
  Ejecuta validaciones en paralelo para procesos del 1 al 10.
  Cada proceso valida sus propias transacciones según el campo 'proceso'.
  Si un proceso falla, se registra el error y los demás continúan.
  """
  permission_classes = [IsAuthenticated]

  @method_decorator(csrf_exempt)
  def post(self, request, format=None):    
    # Validar si el usuario esta autorizado a adicionar.
    if not request.user.has_perm('core.validar_archivo_lk1'):
      registrar_log(
        mensaje = 'Usuario sin permiso para validar transacciones LK1.',
        request = request,
        modulo = 'validar.views.EjecutarValidacionesLK1View',
        accion = AUDIT_ACCION.acceso,
        nivel = AUDIT_NIVEL.warning,
        canal = AUDIT_CANAL.autorizacion
      )
      return respuesta_json('Usuario sin permiso para validar transacciones.', status.HTTP_403_FORBIDDEN)

    try:
      validar_transacciones_lk1(request)
    except Exception as e:
      registrar_log(
        mensaje = f'Ocurrio un error al someter el servicio LK1. {str(e)}',
        request = request,
        modulo = 'validar.views.EjecutarValidacionesLK1View',
        accion = AUDIT_ACCION.proceso,
        nivel = AUDIT_NIVEL.info,
        canal = AUDIT_CANAL.aplicacion
      )
      return respuesta_json(f'Ocurrio un error al someter el servicio LK1. {str(e)}', status.HTTP_500_INTERNAL_SERVER_ERROR)

    return respuesta_json('Proceso de validación de archivo LK1 sometido.', status.HTTP_200_OK)


class LoteLK1ResumenView(APIView):
  """
  Vista personalizada 
  Detalle de lotes 
  Permite ver los lotes, filtrando, paginando y buscando.
  Se debe hacer separada de la clase "CargarTransaccionesLK1View" porque se integraria
  al mismo endpoint GET "/lk1/cargar/" que no tiene sentido para el usuario.
  Ahora quedaria GET "/lk1/lotes/".
  """
  def get(self, request):
    if not request.user.is_authenticated:
      return respuesta_json('Usuario No autenticado', status=status.HTTP_403_FORBIDDEN)

    qs = Tmp_transaccion_LK1.objects.annotate(fecha=TruncDate('lk1fec'))

    # Filtros
    usuario = request.GET.get('usuario')
    fecha = request.GET.get('fecha')
    proceso = request.GET.get('proceso')
    estatus = request.GET.get('estatus')
    search = request.GET.get('search')

    if usuario:
        qs = qs.filter(lk1usu=usuario)
    if fecha:
        qs = qs.filter(lk1fec__date=fecha)
    if proceso:
        qs = qs.filter(lk1pro=proceso)
    if estatus:
        qs = qs.filter(lk1est=estatus)
    if search:
        qs = qs.filter(lk1usu__icontains=search)

    # Agrupación
    resumen = (
        qs.values('lk1usu', 'fecha', 'lk1fid', 'lk1est')
        .annotate(cantidad=Count('lk1seq'))
        .order_by('-fecha', 'lk1usu', 'lk1fid', 'lk1est')
    )

    # Paginación DRF-style
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    paginator = Paginator(resumen, page_size)
    pagina = paginator.get_page(page)

    serializer = LoteLK1ResumenSerializer(pagina, many=True)
    return respuesta_json(
      'Consulta de lotes cargados',
      status.HTTP_200_OK,
      {
      'total': paginator.count,
      'paginas': paginator.num_pages,
      'pagina_actual': pagina.number,
      'resultados': serializer.data
      }
    )
