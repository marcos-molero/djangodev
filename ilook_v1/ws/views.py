from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from django.db.models import Subquery, OuterRef
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from concurrent.futures import ThreadPoolExecutor
from core.models import (
  Ilm002, Ilm003, Ilm004, Ilm006, Ilm027, Ilm016,
  Ilr001, 
  Ilr002
)
from core.filters import (
  Ilr001Filter
)
from ws.serializers import (
  Ilm002Serializer, Ilm003Serializer, Ilm004Serializer, Ilm006Serializer, Ilm027Serializer,
  Ilm016Serializer,
  Ilr001Serializer, Ilr001ListSerializer,
  Ilr002Serializer
)
from sesion.auth import TokenConVencimientoAutenticacion
from utils.genericos import respuesta_json, manejar_error
from utils.logging import registrar_log, AUDIT_ACCION, AUDIT_CANAL, AUDIT_NIVEL
import pandas as pd


def custom_400_view(request, exception=None):
  return manejar_error(request, 'Ocurrio un error.', status.HTTP_400_BAD_REQUEST, exception)

def custom_403_view(request, exception=None):
  return manejar_error(request, 'Usuario no autorizado.', status.HTTP_403_FORBIDDEN, exception)

def custom_404_view(request, exception=None):
  return manejar_error(request, 'Recurso solicitado no encontrado.', status.HTTP_404_NOT_FOUND, exception)

def custom_500_view(request, exception=None):
  return manejar_error(request, 'Ocurrio un error inesperado.', status.HTTP_500_INTERNAL_SERVER_ERROR, exception)


class Ilr001ViewSet(viewsets.ModelViewSet):
  """
  Tablas Generales
  Este mantenimiento de tabla es para una clave compuesta de dos campos.

  FK:
  """
  queryset = Ilr001.objects.all()
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]
  filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
  filterset_class = Ilr001Filter
  search_fields = ['r001003']
  ordering_fields = ['r001001', 'r001002', 'r001003']
  ordering = ['r001001', 'r001002']
  lookup_field = 'r001002'
  lookup_url_kwarg = 'item_id'

  def get_queryset(self):
    qs = super().get_queryset()
    if self.action == 'list':
      return qs.filter(r001002=' ', r001004 = '0')
    return qs

  def get_serializer_class(self):
    return Ilr001ListSerializer if self.action == 'list' else Ilr001Serializer

  def get_permissions(self):
    user = self.request.user
    accion = self.action

    permisos = {
      'list': 'core.view_ilr001',
      'retrieve': 'core.view_ilr001',
      'create': 'core.add_ilr001',
      'update': 'core.change_ilr001',
      'partial_update': 'core.change_ilr001',
      'destroy': 'core.delete_ilr001',
      'dict': 'core.view_ilr001',
    }

    permiso_requerido = permisos.get(accion)
    if permiso_requerido and not user.has_perm(permiso_requerido):
      registrar_log(
        mensaje='No autorizado a la acción.',
        request=self.request,
        modulo='TablasGenerales',
        accion=getattr(AUDIT_ACCION, accion, accion),
        canal=AUDIT_CANAL.autorizacion,
        nivel=AUDIT_NIVEL.error
      )
      raise PermissionDenied()

    return super().get_permissions()

  def perform_create(self, serializer):
    data = serializer.validated_data
    tabla_id = data.get('r001001')
    item_id = data.get('r001002')

    if Ilr001.objects.filter(r001001=tabla_id, r001002=item_id).exists():
      registrar_log(
        mensaje=f'Registro {item_id} ya existe en la tabla: {tabla_id}.',
        request=self.request,
        modulo='TablasGenerales',
        accion=AUDIT_ACCION.crear,
        nivel=AUDIT_NIVEL.warning,
        canal=AUDIT_CANAL.datos
      )
      raise ValidationError('Registro ya existe.')

    serializer.save(r001007=self.request.user.username, r001008=timezone.now())
    registrar_log(
      mensaje=f'Registro {item_id} creado en la tabla: {tabla_id}.',
      request=self.request,
      modulo='TablasGenerales',
      accion=AUDIT_ACCION.crear,
      nivel=AUDIT_NIVEL.info,
      canal=AUDIT_CANAL.datos
    )

  @action(detail=False, methods=['get'], url_path='det/(?P<tabla_id>[^/.]+)/(?P<item_id>[^/.]+)', permission_classes=[IsAuthenticated])
  def detalle(self, request, tabla_id=None, item_id=None):
    user = request.user
    if not user.has_perm('core.view_ilr001'):
      registrar_log(
        mensaje='No autorizado a la acción [detalle].',
        request=request,
        modulo='TablasGenerales',
        accion=AUDIT_ACCION.leer,
        canal=AUDIT_CANAL.autorizacion,
        nivel=AUDIT_NIVEL.error
      )
      raise PermissionDenied()

    try:
      instancia = get_object_or_404(Ilr001, r001001=tabla_id, r001002=item_id)
      serializer = self.get_serializer(instancia)
      registrar_log(
        mensaje=f'Consulta de la tabla {tabla_id} al registro {item_id}.',
        request=request,
        modulo='TablasGenerales',
        accion=AUDIT_ACCION.leer,
        nivel=AUDIT_NIVEL.info,
        canal=AUDIT_CANAL.datos
      )
      return respuesta_json('Detalle del registro', status.HTTP_200_OK, datos=serializer.data)
    except Http404:
      registrar_log(
        mensaje=f'El registro [{tabla_id}-{item_id}] no existe.',
        request=request,
        modulo='TablasGenerales',
        accion=AUDIT_ACCION.actualizar,
        nivel=AUDIT_NIVEL.error,
        canal=AUDIT_CANAL.datos
      )
      return respuesta_json('Registro no existe.', status.HTTP_404_NOT_FOUND)
    except Exception as e:
      registrar_log(
        mensaje=f'Error al leer el registro [{tabla_id}-{item_id}]: {str(e)}',
        request=request,
        modulo='TablasGenerales',
        accion=AUDIT_ACCION.leer,
        nivel=AUDIT_NIVEL.error,
        canal=AUDIT_CANAL.datos
      )
      return respuesta_json('Error al leer el registro', status.HTTP_500_INTERNAL_SERVER_ERROR)

  @action(detail=False, methods=['put'], url_path='upd/(?P<tabla_id>[^/.]+)/(?P<item_id>[^/.]+)', permission_classes=[IsAuthenticated])
  def actualizar(self, request, tabla_id=None, item_id=None):
    user = request.user
    if not user.has_perm('core.change_ilr001'):
      registrar_log(
        mensaje='No autorizado a la acción [actualizar].',
        request=request,
        modulo='TablasGenerales',
        accion=AUDIT_ACCION.actualizar,
        canal=AUDIT_CANAL.autorizacion,
        nivel=AUDIT_NIVEL.error
      )
      raise PermissionDenied()

    try:
      instancia = get_object_or_404(Ilr001, r001001=tabla_id, r001002=item_id)
      data = request.data.copy()

      # Eliminar claves primarias del payload
      data.pop('r001001', None)
      data.pop('r001002', None)

      # Campos automáticos
      data['r001007'] = user.username
      data['r001008'] = timezone.now()

      serializer = self.get_serializer(instancia, data=data, partial=True)
      if serializer.is_valid():
        actualizado = serializer.save()
        registrar_log(
          mensaje=f'Registro {item_id} de la tabla {tabla_id} actualizado.',
          request=request,
          modulo='TablasGenerales',
          accion=AUDIT_ACCION.actualizar,
          nivel=AUDIT_NIVEL.info,
          canal=AUDIT_CANAL.datos
        )
        return respuesta_json('Registro actualizado correctamente.', status.HTTP_200_OK, datos=Ilr001Serializer(actualizado).data)

      registrar_log(
        mensaje=f'Error de validación al actualizar [{tabla_id}-{item_id}]: {serializer.errors}',
        request=request,
        modulo='TablasGenerales',
        accion=AUDIT_ACCION.actualizar,
        nivel=AUDIT_NIVEL.warning,
        canal=AUDIT_CANAL.datos
      )
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=serializer.errors)

    except Http404:
      registrar_log(
        mensaje=f'El registro [{tabla_id}-{item_id}] no existe.',
        request=request,
        modulo='TablasGenerales',
        accion=AUDIT_ACCION.actualizar,
        nivel=AUDIT_NIVEL.error,
        canal=AUDIT_CANAL.datos
      )
      return respuesta_json('Registro no existe.', status.HTTP_404_NOT_FOUND)
    except Exception as e:
      registrar_log(
        mensaje=f'Error al actualizar el registro [{tabla_id}-{item_id}]: {str(e)}',
        request=request,
        modulo='TablasGenerales',
        accion=AUDIT_ACCION.actualizar,
        nivel=AUDIT_NIVEL.error,
        canal=AUDIT_CANAL.datos
      )
      return respuesta_json('Error al actualizar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)
    
  @action(detail=False, methods=['delete'], url_path='del/(?P<tabla_id>[^/.]+)/(?P<item_id>[^/.]+)', permission_classes=[IsAuthenticated])
  def eliminar(self, request, tabla_id=None, item_id=None):
    user = request.user
    if not user.has_perm('core.delete_ilr001'):
      registrar_log(
        mensaje='No autorizado a la acción [eliminar].',
        request=request,
        modulo='TablasGenerales',
        accion=AUDIT_ACCION.eliminar,
        canal=AUDIT_CANAL.autorizacion,
        nivel=AUDIT_NIVEL.error
      )
      raise PermissionDenied()

    try:
      instancia = get_object_or_404(Ilr001, r001001=tabla_id, r001002=item_id)
      instancia.delete()
      registrar_log(
        mensaje=f'Registro {item_id} de la tabla {tabla_id} eliminado.',
        request=request,
        modulo='TablasGenerales',
        accion=AUDIT_ACCION.eliminar,
        nivel=AUDIT_NIVEL.info,
        canal=AUDIT_CANAL.datos
      )
      return respuesta_json('Registro eliminado correctamente.', status.HTTP_200_OK)
    except Http404:
      registrar_log(
        mensaje=f'Registro [{tabla_id}-{item_id}] no existe.',
        request=request,
        modulo='TablasGenerales',
        accion=AUDIT_ACCION.eliminar,
        nivel=AUDIT_NIVEL.error,
        canal=AUDIT_CANAL.datos
      )
      return respuesta_json('Registro no existe.', status.HTTP_404_NOT_FOUND)
    except Exception as e:
      registrar_log(
        mensaje=f'Error al eliminar el registro [{tabla_id}-{item_id}]: {str(e)}',
        request=request,
        modulo='TablasGenerales',
        accion=AUDIT_ACCION.eliminar,
        nivel=AUDIT_NIVEL.error,
        canal=AUDIT_CANAL.datos
      )
      return respuesta_json('Error al eliminar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)

  @action(detail=False, methods=['get'], url_path='dict/(?P<tabla_id>[^/.]+)', permission_classes=[IsAuthenticated])
  def dict(self, request, tabla_id=None):
    try:
      tabla_id = int(tabla_id)
    except (TypeError, ValueError):
      registrar_log(
        mensaje='Parámetro [tabla] inválido.',
        request=request,
        modulo='TablasGenerales',
        accion=AUDIT_ACCION.diccionario,
        nivel=AUDIT_NIVEL.warning,
        canal=AUDIT_CANAL.datos
      )
      raise ValidationError('[dict] Parámetro [tabla] inválido.')

    try:
      cabecera = Ilr001.objects.get(r001001=tabla_id, r001002='', r001004='0')
      descripcion_tabla = cabecera.r001003.strip()
    except Ilr001.DoesNotExist:
      registrar_log(
        mensaje=f'La tabla {tabla_id} no existe o falta cabecera.',
        request=request,
        modulo='TablasGenerales',
        accion=AUDIT_ACCION.diccionario,
        nivel=AUDIT_NIVEL.warning,
        canal=AUDIT_CANAL.datos
      )
      raise ValidationError(f'[dict] Tabla {tabla_id} inválida.')

    registros = Ilr001.objects.filter(r001001=tabla_id, r001004='0').exclude(r001002='')
    if not registros.exists():
      registrar_log(
        mensaje=f'Tabla {tabla_id} sin registros de detalle.',
        request=request,
        modulo='TablasGenerales',
        accion=AUDIT_ACCION.diccionario,
        nivel=AUDIT_NIVEL.warning,
        canal=AUDIT_CANAL.datos
      )
      raise ValidationError(f'[dict] Tabla {tabla_id} sin detalle.')

    resultado = {r.r001002.strip(): r.r001003.strip() for r in registros}
    lc_datos = {
      'tabla': tabla_id,
      'descripcion': descripcion_tabla,
      'total_reg': len(resultado),
      'registros': resultado
    }

    registrar_log(
      mensaje=f'Consulta de diccionario para tabla [{tabla_id}].',
      request=request,
      modulo='TablasGenerales',
      accion=AUDIT_ACCION.diccionario,
      nivel=AUDIT_NIVEL.info,
      canal=AUDIT_CANAL.datos
    )
    return respuesta_json(detalle='Tablas Generales dict', codigo=200, datos=lc_datos)


"""
Estos views estan deprecados.
Se dejan como referencia de como hacer lo mismo que en la clase anterior "Ilr001ViewSet".
Pero como Funciones sueltas. Queda como caso de desarrollo.
"""
class Ilr001ListView(generics.ListAPIView):
  queryset = Ilr001.objects.all()
  serializer_class = Ilr001ListSerializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  # Filtros, ordenar y pagineo 
  filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
  filterset_class = Ilr001Filter

  # Busqueda
  search_fields = ['r001003'] # [descripcion]

  # Ordenamiento
  ordering_fields = ['r001001', 'r001002', 'r001003'] # [tabla, item, descripcion]
  ordering = ['r001001', 'r001002']

  def get_queryset(self):
    user = self.request.user
    if not user.has_perm("core.view_ilr001"):
      registrar_log(mensaje='No autorizado a la accion.', request=self.request, modulo='TablasGenerales', accion=AUDIT_ACCION.lista, canal=AUDIT_CANAL.datos, nivel=AUDIT_NIVEL.error)
      raise PermissionDenied()

    registrar_log(mensaje='Acceso autorizado', request=self.request, modulo='TablasGenerales', accion=AUDIT_ACCION.lista, canal=AUDIT_CANAL.datos, nivel=AUDIT_NIVEL.info)
    return super().get_queryset()

class Ilr001DictView(APIView):
  """
  Devuelve los items de una tabla como un objeto dict.

  args:
    r001001 : Codigo de la tabla

  returns:
    dict(r001002, r001003)
  """
  permission_classes = [IsAuthenticated]

  def get(self, request, tabla_id):
    if not request.user.has_perm('core.view_ilr001'):
      registrar_log(mensaje='No autorizado a la accion.', request=request, modulo='TablasGenerales', accion=AUDIT_ACCION.diccionario, nivel=AUDIT_NIVEL.error, canal=AUDIT_CANAL.datos)
      raise PermissionDenied()
    if not isinstance(tabla_id, int):
      registrar_log(mensaje='Parametro [tabla] invalido.', request=request, modulo='TablasGenerales', accion=AUDIT_ACCION.diccionario, nivel=AUDIT_NIVEL.warning, canal=AUDIT_CANAL.datos)
      raise ValidationError('[dict] Parametro [tabla] invalido.')
    
    # Buscar la descripcion de la tabla.
    # el strip aca es porque la tabla esta con CHAR, en vez de VARCHAR.
    try:
      cabecera = Ilr001.objects.get(r001001=tabla_id, r001002='', r001004='0')
      descripcion_tabla = cabecera.r001003.strip()
    except Ilr001.DoesNotExist:
      registrar_log(mensaje=f'La tabla {tabla_id} no existe. Verifique si el registro de cabecera esta bien configurado.', request=request, modulo='TablasGenerales', accion=AUDIT_ACCION.diccionario, nivel=AUDIT_NIVEL.warning, canal=AUDIT_CANAL.datos)
      raise ValidationError(f'[dict] Tabla {tabla_id} invalido.')

    # Cargamos todos los registros de la tabla.
    registros = Ilr001.objects.filter(r001001=tabla_id, r001004='0').exclude(r001002='')
    # no hay datos.
    if len(registros) == 0:
      registrar_log(mensaje=f'[dict] La tabla {tabla_id} no existe. Verifique si el registro de cabecera y detalle esta bien configurado.', request=request, modulo='TablasGenerales', accion=AUDIT_ACCION.diccionario, nivel=AUDIT_NIVEL.warning, canal=AUDIT_CANAL.datos)
      raise ValidationError(f'[dict] Tabla {tabla_id} sin detalle.')

    # Generar dict.
    resultado = {r.r001002.strip(): r.r001003.strip() for r in registros}
    lc_datos = {
      'tabla': tabla_id,
      'descripcion': descripcion_tabla,
      'total_reg': len(resultado),
      'registros': resultado
    }

    registrar_log(mensaje=f'Consulta la tabla [{tabla_id}]', request=request, modulo='TablasGenerales', accion=AUDIT_ACCION.diccionario, nivel=AUDIT_NIVEL.info, canal=AUDIT_CANAL.datos)
    return respuesta_json(detalle='Tablas Generales dict', codigo=200, datos=lc_datos)

class Ilr001CreateView(generics.CreateAPIView):
  queryset = Ilr001.objects.all()
  serializer_class = Ilr001Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def create(self, request, *args, **kwargs):
    try:
      # Validar usuario autorizado.
      lc_user = request.user
      if not lc_user:
        registrar_log(mensaje=f'No autorizado a insertar.', request=request, modulo='TablasGenerales', accion=AUDIT_ACCION.crear, nivel=AUDIT_NIVEL.error, canal=AUDIT_CANAL.datos)
        raise PermissionDenied()
      
      # Copiar la data e incluir campos "automáticos".
      lc_data = request.data.copy()
      lc_data['r001007'] = lc_user.username
      lc_data['r001008'] = timezone.now()

      # Validar existencia
      lc_tabla_id = lc_data.get('r001001')
      lc_item_id = lc_data.get('r001002')
      if Ilr001.objects.filter(r001001=lc_tabla_id, r001002=lc_item_id).exists():
        registrar_log(mensaje=f'Registro {lc_item_id} ya existe en la tabla: {lc_tabla_id}.', request=request, modulo='TablasGenerales', accion=AUDIT_ACCION.crear, nivel=AUDIT_NIVEL.warning, canal=AUDIT_CANAL.datos)
        return respuesta_json('Registro ya existe.', status.HTTP_400_BAD_REQUEST)

      # Actualizar el modelo.
      lc_serializer = self.get_serializer(data=lc_data)
      if lc_serializer.is_valid():
        lc_instancia = lc_serializer.save()
        registrar_log(mensaje=f'Registro {lc_item_id} creado en la tabla: {lc_tabla_id}.', request=request, modulo='TablasGenerales', accion=AUDIT_ACCION.crear, nivel=AUDIT_NIVEL.info, canal=AUDIT_CANAL.datos)
        return respuesta_json('Registro creado correctamente.', status.HTTP_201_CREATED, datos=lc_serializer.data)

      registrar_log(mensaje=f'Error al validar tabla [TablasGenerales]: [{lc_serializer.errors}].', request=request, modulo='TablasGenerales', accion=AUDIT_ACCION.crear, nivel=AUDIT_NIVEL.warning, canal=AUDIT_CANAL.datos)
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)
    except Exception as e:
      registrar_log(mensaje=f'Ocurrio un error al insertar el registro. [{str(e)}]', request=request, modulo='TablasGenerales', accion=AUDIT_ACCION.crear, nivel=AUDIT_NIVEL.error, canal=AUDIT_CANAL.datos)
      return respuesta_json('Ocurrio un error al insertar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)

class Ilr001DetailView(generics.RetrieveAPIView):
  queryset = Ilr001.objects.all()
  serializer_class = Ilr001Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_tabla_id = self.kwargs.get('tabla_id')
    lc_item_id = self.kwargs.get('item_id')
    return get_object_or_404(Ilr001, r001001=lc_tabla_id, r001002=lc_item_id)
  
  def retrieve(self, request, *args, **kwargs):
    user = self.request.user
    if not user.has_perm("core.view_ilr001"):
      registrar_log(mensaje='No autorizado a la opcion.', request=request, modulo='TablasGenerales', accion=AUDIT_ACCION.leer, nivel=AUDIT_NIVEL.warning, canal=AUDIT_CANAL.datos)
      return respuesta_json('Usuario no autorizado a la opcion.', status.HTTP_403_FORBIDDEN)

    lc_tabla_id = self.kwargs.get('tabla_id')
    lc_item_id = self.kwargs.get('item_id')
    try:
      lc_instancia = self.get_object()
      lc_serializer = self.get_serializer(lc_instancia)
      registrar_log(mensaje=f'Consulta de la tabla {lc_tabla_id} al registro {lc_item_id}.', request=request, modulo='TablasGenerales', accion=AUDIT_ACCION.leer, nivel=AUDIT_NIVEL.info, canal=AUDIT_CANAL.datos)
      return respuesta_json('Detalle del registro', status.HTTP_200_OK, datos=lc_serializer.data)
    except Http404:
      registrar_log(mensaje=f'El registro {lc_tabla_id} en la tabla {lc_item_id} no existe.', request=request, modulo='TablasGenerales', accion=AUDIT_ACCION.leer, nivel=AUDIT_NIVEL.warning, canal=AUDIT_CANAL.datos)
      return respuesta_json('Registro no existe', status.HTTP_404_NOT_FOUND)
    except Exception as e:
      registrar_log(mensaje=f'Error al leer el registro. [{str(e)}]', request=request, modulo='TablasGenerales', accion=AUDIT_ACCION.leer, nivel=AUDIT_NIVEL.error, canal=AUDIT_CANAL.datos)
      return respuesta_json('Error al leer el registro', status.HTTP_500_INTERNAL_SERVER_ERROR)

class Ilr001UpdateView(generics.UpdateAPIView):
  queryset = Ilr001.objects.all()
  serializer_class = Ilr001Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_tabla_id = self.kwargs.get('tabla_id')
    lc_item_id = self.kwargs.get('item_id')
    return get_object_or_404(Ilr001, r001001=lc_tabla_id, r001002=lc_item_id)
  
  def update(self, request, *args, **kwargs):
    lc_tabla_id = self.kwargs.get('tabla_id')
    lc_item_id = self.kwargs.get('item_id')

    lc_user = getattr(self.request.user, 'username', 'anonimo')
    if not lc_user:
      registrar_log(mensaje='Usuario no autorizado.', request=request, modulo='TablasGenerales', accion=AUDIT_ACCION.actualizar, nivel=AUDIT_NIVEL.error, canal=AUDIT_CANAL.datos)
      return respuesta_json('Usuario no autorizado.', status.HTTP_403_FORBIDDEN)

    try:
      lc_instancia = self.get_object()
      lc_data = request.data.copy()

      # Eliminar los campos claves.
      lc_data.pop('r001001', None)
      lc_data.pop('r001002', None)

      # ACtualizar campos "automaticos".
      lc_data['r001007'] = request.user.username
      lc_data['r001008'] = timezone.now()

      lc_serializer = self.get_serializer(lc_instancia, data=lc_data, partial=True)
      if lc_serializer.is_valid():
        lc_grabar = lc_serializer.save()
        registrar_log(mensaje='Registro {lc_item_id} de la tabla {lc_tabla_id} actualizado.', request=request, modulo='TablasGenerales', accion=AUDIT_ACCION.actualizar, nivel=AUDIT_NIVEL.info, canal=AUDIT_CANAL.datos)
        return respuesta_json('Registro actualizado correctamente.', status.HTTP_200_OK, datos=Ilr001Serializer(lc_grabar).data)
      registrar_log(mensaje=f'Error de validación. [{lc_serializer.errors}]', request=request, modulo='TablasGenerales', accion=AUDIT_ACCION.actualizar, nivel=AUDIT_NIVEL.warning, canal=AUDIT_CANAL.datos)
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)

    except Http404:
      registrar_log(mensaje=f'Registro [{lc_tabla_id}-{lc_item_id}] no existe.', request=request, modulo='TablasGenerales', accion=AUDIT_ACCION.actualizar, nivel=AUDIT_NIVEL.warning, canal=AUDIT_CANAL.datos)
      return respuesta_json('Registro no existe.', status.HTTP_404_NOT_FOUND)

    except Exception as e:
      registrar_log(mensaje=f'Error al actualizar el registro {lc_item_id} de la tabla {lc_tabla_id}.', request=request, modulo='TablasGenerales', accion=AUDIT_ACCION.actualizar, nivel=AUDIT_NIVEL.warning, canal=AUDIT_CANAL.datos)
      return respuesta_json('Error al actualizar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)

class Ilr001DeleteView(generics.DestroyAPIView):
  queryset = Ilr001.objects.all()
  serializer_class = Ilr001Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_tabla_id = self.kwargs.get('tabla_id')
    lc_item_id = self.kwargs.get('item_id')
    return get_object_or_404(Ilr001, r001001=lc_tabla_id, r001002=lc_item_id)
  
  def destroy(self, request, *args, **kwargs):
    lc_tabla_id = self.kwargs.get('tabla_id')
    lc_item_id = self.kwargs.get('item_id')

    lc_user = getattr(self.request.user, 'username', 'anonimo')
    if not lc_user:
      registrar_log(mensaje='Usuario no autorizado.', request=request, modulo='TablasGenerales', accion=AUDIT_ACCION.eliminar, nivel=AUDIT_NIVEL.info, canal=AUDIT_CANAL.datos)
      return respuesta_json('Usuario no autorizado.', status.HTTP_403_FORBIDDEN)

    try:
      lc_instancia = self.get_object()
      lc_instancia.delete()
      registrar_log(mensaje=f'Registro {lc_item_id} de la tabla {lc_tabla_id} eliminado.', request=request, modulo='TablasGenerales', accion=AUDIT_ACCION.eliminar, nivel=AUDIT_NIVEL.info, canal=AUDIT_CANAL.datos)
      return respuesta_json('Registro eliminado correctamente.', status.HTTP_200_OK)
    except Http404:
      registrar_log(mensaje=f'Registro {lc_item_id} de la tabla {lc_tabla_id} no existe.', request=request, modulo='TablasGenerales', accion=AUDIT_ACCION.eliminar, nivel=AUDIT_NIVEL.warning, canal=AUDIT_CANAL.datos)
      return respuesta_json('Registro no existe.', status.HTTP_404_NOT_FOUND)
    except Exception as e:
      registrar_log(mensaje=f'Error al eliminar el registro {lc_item_id} de la tabla {lc_tabla_id}. [{str(e)}]', request=request, modulo='TablasGenerales', accion=AUDIT_ACCION.eliminar, nivel=AUDIT_NIVEL.error, canal=AUDIT_CANAL.datos)
      return respuesta_json('Error al eliminar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


"""
Monedas
FK: Ilr001
"""
class Ilm002ListView(generics.ListAPIView):
  queryset = Ilm002.objects.all()
  serializer_class = Ilm002Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  # Filtros, ordenar y pagineo 
  filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
  filter_set_fields = ['m002001', 'm002003']

  # Busqueda
  search_fields = ['m002002']

  # Ordenamiento
  ordering_fields = ['m002001', 'm002003', 'm002003']
  ordering = ['m002001']

  def get_queryset(self):
    user = self.request.user
    if not user.has_perm('core.view_ilm002'):
      raise PermissionDenied()
    return super().get_queryset()

class Ilm002CreateView(generics.CreateAPIView):
  queryset = Ilm002.objects.all()
  serializer_class = Ilm002Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  # sobrescribimos el create
  def create(self, request, *args, **kwargs):
    try:
      lc_user = request.user
      if not lc_user.has_perm('core.add_ilm002'):
        raise PermissionDenied()
      
      lc_data = request.data.copy()

      # Campos "automaticos"
      lc_data['m002012'] = lc_user.username
      lc_data['m002013'] = timezone.now()

      if Ilm002.objects.filter(m002001=lc_data.get('m002001')).exists():
        return respuesta_json('Registro ya existe.', status.HTTP_400_BAD_REQUEST)
      
      lc_serializer = self.get_serializer(data=lc_data)
      if lc_serializer.is_valid():
        lc_instancia = lc_serializer.save()
        return respuesta_json('Registro creado satisfactoriamente.', status.HTTP_201_CREATED, datos=Ilm002Serializer(lc_instancia).data)
      
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)
    
    except Exception as e:
      print('Error en Ilm002CreateView: ', str(e))
      return respuesta_json('Ocurrio un error al insertar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)

class Ilm002DetailView(generics.RetrieveAPIView):
  queryset = Ilm002.objects.all()
  serializer_class = Ilm002Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    user = self.request.user
    if not user.has_perm("core.view_ilm002"):
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilm002, m002001=lc_codigo)
  
  def retrieve(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_serializer = self.get_serializer(lc_instancia)
      return respuesta_json('Detalle del registro.', status.HTTP_200_OK, datos=lc_serializer.data)
    except Http404:
      return respuesta_json('No existe el registro.', status.HTTP_404_NOT_FOUND)
    except Exception as e:
      print("Error en Ilm002DetailView: ", str(e))
      return respuesta_json('Error al leer el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)

class Ilm002UpdateView(generics.UpdateAPIView):
  queryset = Ilm002.objects.all()
  serializer_class = Ilm002Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_user = self.request.user
    if not lc_user:
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilm002, m002001=lc_codigo)
  
  def update(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_data = request.data.copy()
      lc_user = request.user

      # Eliminar campos clave
      lc_data.pop('m002001', None)

      # Campos "automaticos"
      lc_data['m002012'] = lc_user.username
      lc_data['m002013'] = timezone.now()

      lc_serializer = self.get_serializer(lc_instancia, data=lc_data, partial=True)
      if lc_serializer.is_valid():
        lc_grabar = lc_serializer.save()
        return respuesta_json('Registro actualizado correctamente.', status.HTTP_200_OK, datos=Ilm002Serializer(lc_grabar).data)
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)

    except Http404:
      return respuesta_json('No existe el registro.', status.HTTP_404_NOT_FOUND)
    except Exception as e:
      print ('Error en Ilm002UpdateView: ', str(e))
      return respuesta_json('Error al actualizar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)

class Ilm002DeleteView(generics.DestroyAPIView):
  queryset = Ilm002.objects.all()
  serializer_class = Ilm002Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_user = self.request.user
    if not lc_user:
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilm002, m002001=lc_codigo)
  
  def destroy(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_instancia.delete()
      return respuesta_json('Registro eliminado correctamente.', status.HTTP_200_OK)
    except Http404:
      return respuesta_json('No existe el registro.', status.HTTP_404_NOT_FOUND)
    except Exception as e:
      print('Error en Ilr002DeleteView: ', str(e))
      return respuesta_json('Error al eliminar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


"""
Paises
FK: Ilr001, Ilm002
"""
class Ilm003ListView(generics.ListAPIView):
  queryset = Ilm003.objects.all()
  serializer_class = Ilm003Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  # Filtros, ordenar y pagineo 
  filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
  filter_set_fields = ['m003001', 'm003003']

  # Busqueda
  search_fields = ['m003002']

  # Ordenamiento
  ordering_fields = ['m003001', 'm003003', 'm003003']
  ordering = ['m003001']

  def get_queryset(self):
    user = self.request.user
    if not user.has_perm('core.view_ilm003'):
      raise PermissionDenied()
    return super().get_queryset()

class Ilm003CreateView(generics.CreateAPIView):
  queryset = Ilm003.objects.all()
  serializer_class = Ilm003Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  # sobrescribimos el create
  def create(self, request, *args, **kwargs):
    try:
      lc_user = request.user
      if not lc_user.has_perm('core.add_ilm003'):
        raise PermissionDenied()
      
      lc_data = request.data.copy()

      # Campos "automaticos"
      lc_data['m003006'] = lc_user.username
      lc_data['m003007'] = timezone.now()

      if Ilm003.objects.filter(m003001=lc_data.get('m003001')).exists():
        return respuesta_json('Registro ya existe.', status.HTTP_400_BAD_REQUEST)
      
      lc_serializer = self.get_serializer(data=lc_data)
      if lc_serializer.is_valid():
        lc_instancia = lc_serializer.save()
        return respuesta_json('Registro creado satisfactoriamente.', status.HTTP_201_CREATED, datos=Ilm003Serializer(lc_instancia).data)
      
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)
    
    except Exception as e:
      print('Error en Ilm003CreateView: ', str(e))
      return respuesta_json('Ocurrio un error al insertar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)

class Ilm003DetailView(generics.RetrieveAPIView):
  queryset = Ilm003.objects.all()
  serializer_class = Ilm003Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    user = self.request.user
    if not user.has_perm("core.view_ilm003"):
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilm003, m003001=lc_codigo)
  
  def retrieve(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_serializer = self.get_serializer(lc_instancia)
      return respuesta_json('Detalle del registro.', status.HTTP_200_OK, datos=lc_serializer.data)
    except Http404:
      return respuesta_json('No existe el registro.', status.HTTP_404_NOT_FOUND)
    except Exception as e:
      print("Error en Ilm003DetailView: ", str(e))
      return respuesta_json('Error al leer el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)

class Ilm003UpdateView(generics.UpdateAPIView):
  queryset = Ilm003.objects.all()
  serializer_class = Ilm003Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_user = self.request.user
    if not lc_user:
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilm003, m003001=lc_codigo)
  
  def update(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_data = request.data.copy()
      lc_user = request.user
      print('datos: ', lc_data)

      # Eliminar campos clave
      lc_data.pop('m003001', None)

      # Campos "automaticos"
      lc_data['m003006'] = lc_user.username
      lc_data['m003007'] = timezone.now()

      lc_serializer = self.get_serializer(lc_instancia, data=lc_data, partial=True)
      if lc_serializer.is_valid():
        lc_grabar = lc_serializer.save()
        return respuesta_json('Registro actualizado correctamente.', status.HTTP_200_OK, datos=Ilm003Serializer(lc_grabar).data)
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)

    except Http404:
      return respuesta_json('No existe el registro.', status.HTTP_404_NOT_FOUND)
    except Exception as e:
      print ('Error en Ilm003UpdateView: ', str(e))
      return respuesta_json('Error al actualizar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)

class Ilm003DeleteView(generics.DestroyAPIView):
  queryset = Ilm003.objects.all()
  serializer_class = Ilm003Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_user = self.request.user
    if not lc_user:
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilm003, m003001=lc_codigo)
  
  def destroy(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_instancia.delete()
      return respuesta_json('Registro eliminado correctamente.', status.HTTP_200_OK)
    except Http404:
      return respuesta_json('No existe el registro.', status.HTTP_404_NOT_FOUND)
    except Exception as e:
      print('Error en Ilr003DeleteView: ', str(e))
      return respuesta_json('Error al eliminar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


"""
Alerta
FK: Ilr001
"""
class Ilm004ListView(generics.ListAPIView):
  queryset = Ilm004.objects.all()
  serializer_class = Ilm004Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  # Filtros, ordenar y pagineo 
  filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
  filterset_fields = ['m004001', 'm004003', 'm004004', 'm004006']

  # Busqueda
  search_fields = ['m004002']

  # Ordenamiento
  ordering_fields = ['m004001', 'm004003']
  ordering = ['m004001']

  def get_queryset(self):
    user = self.request.user
    if not user.has_perm('core.view_ilm004'):
      registrar_log(mensaje='Acceso denegado', request=self.request, modulo='Alertas', accion=AUDIT_ACCION.lista, nivel=AUDIT_NIVEL.error, canal=AUDIT_CANAL.autorizacion)
      raise PermissionDenied()
    return super().get_queryset()

class Ilm004CreateView(generics.CreateAPIView):
  queryset = Ilm004.objects.all()
  serializer_class = Ilm004Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  # sobrescribimos el create
  def create(self, request, *args, **kwargs):
    try:
      lc_user = request.user
      if not lc_user.has_perm('core.add_ilm004'):
        logger_auth.error(f'[create] Usuario {lc_user.username} no autorizado a insertar en [Alertas]')
        raise PermissionDenied()
      
      lc_data = request.data.copy()
      lc_alerta_id = lc_data['m004001']

      # Campos "automaticos"
      lc_data['m004007'] = lc_user.username
      lc_data['m004008'] = timezone.now()
      ip = request.META.get('REMOTE_ADDR')
      ua = request.META.get('HOST_USER_AGENT', '')
      lc_alerta_id = lc_data['m004001']

      if Ilm004.objects.filter(m004001=lc_data.get('m004001')).exists():
        logger_data.error(f'[create] Registro {lc_alerta_id} ya existe en la tabla Alertas. {lc_user.username}/{ip}/{ua}.')
        return respuesta_json('Registro ya existe.', status.HTTP_400_BAD_REQUEST)
      
      lc_serializer = self.get_serializer(data=lc_data)
      if lc_serializer.is_valid():
        lc_instancia = lc_serializer.save()
        logger_data.info(f'[create] Registro {lc_alerta_id} creado en la tabla: [Alertas]. {lc_user.username}/{ip}/{ua}.')
        return respuesta_json('Registro creado satisfactoriamente.', status.HTTP_201_CREATED, datos=Ilm004Serializer(lc_instancia).data)
      
      logger_data.error(f'[create] Error al validar tabla [Alertas]: [{str(lc_serializer.errors)}]. Usuario {lc_user.username}, IP {ip}, UA {ua}')
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)
    
    except Exception as e:
      logger_data.error(f'[create] Error al insertar en la tabla [Alertas]: {str(e)}. Usuario {lc_user.username}, IP {ip}, UA {ua}')
      return respuesta_json('Ocurrio un error al insertar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)

class Ilm004DetailView(generics.RetrieveAPIView):
  queryset = Ilm004.objects.all()
  serializer_class = Ilm004Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    user = self.request.user
    if not user.has_perm("core.view_ilm004"):
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilm004, m004001=lc_codigo)
  
  def retrieve(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_serializer = self.get_serializer(lc_instancia)
      return respuesta_json('Detalle del registro.', status.HTTP_200_OK, datos=lc_serializer.data)
    except Http404:
      return respuesta_json('No existe el registro.', status.HTTP_404_NOT_FOUND)
    except Exception as e:
      print("Error en Ilm003DetailView: ", str(e))
      return respuesta_json('Error al leer el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)

class Ilm004UpdateView(generics.UpdateAPIView):
  queryset = Ilm004.objects.all()
  serializer_class = Ilm004Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_user = self.request.user
    if not lc_user:
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilm004, m004001=lc_codigo)
  
  def update(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_data = request.data.copy()
      lc_user = request.user

      # Eliminar campos clave
      lc_data.pop('m004001', None)

      # Campos "automaticos"
      lc_data['m004007'] = lc_user.username
      lc_data['m004008'] = timezone.now()

      lc_serializer = self.get_serializer(lc_instancia, data=lc_data, partial=True)
      if lc_serializer.is_valid():
        lc_grabar = lc_serializer.save()
        return respuesta_json('Registro actualizado correctamente.', status.HTTP_200_OK, datos=Ilm004Serializer(lc_grabar).data)
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)

    except Http404:
      return respuesta_json('No existe el registro.', status.HTTP_404_NOT_FOUND)
    except Exception as e:
      print ('Error en Ilm004UpdateView: ', str(e))
      return respuesta_json('Error al actualizar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)

class Ilm004DeleteView(generics.DestroyAPIView):
  queryset = Ilm004.objects.all()
  serializer_class = Ilm004Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_user = self.request.user
    if not lc_user:
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilm004, m004001=lc_codigo)
  
  def destroy(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_instancia.delete()
      return respuesta_json('Registro eliminado correctamente.', status.HTTP_200_OK)
    except Http404:
      return respuesta_json('No existe el registro.', status.HTTP_404_NOT_FOUND)
    except Exception as e:
      print('Error en Ilr003DeleteView: ', str(e))
      return respuesta_json('Error al eliminar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)

class TestUpLoadView(APIView):
  parser_classes = [MultiPartParser]
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]
  queryset = Ilm004.objects.all()

  def post(self, request, format=None):
    try:
      lc_user = request.user
      if not lc_user.has_perm('core.add_ilm004'):
        return respuesta_json('Usuario no autorizado.', status.HTTP_403_FORBIDDEN)
        
      lc_archivo = request.FILES.get('archivo')
      if not lc_archivo:
        return respuesta_json('No se recibió ningún archivo.', status.HTTP_400_BAD_REQUEST)
        
      # Detectar que tipo de archivo es
      lc_extension = lc_archivo.name.split('.')[-1].lower()
      if lc_extension == 'csv':
        df = pd.read_csv(lc_archivo, dtype=str)
      elif lc_extension in ['xls', 'xlsx']:
        df = pd.read_excel(lc_archivo, dtype=str)
      else:
        return respuesta_json('Formato de archivo no soportado.', status.HTTP_406_NOT_ACCEPTABLE)
        
      resultados = {
        'procesados': 0,
        'exitosos': 0,
        'errores': []
      }

      def procesar_fila(fila):
        lc_datos = fila.to_dict()
        lc_datos['m004007'] = lc_user.username
        lc_serializer = Ilm004Serializer(data = lc_datos)
        if lc_serializer.is_valid():
          lc_serializer.save()
          resultados['exitosos'] += 1
        else:
          resultados['errores'].append({'fila': lc_datos, 'errores': lc_serializer.errors})

      with ThreadPoolExecutor(max_workers=settings.GL_PROCESOS_VALIDACION) as ejecutor:
        for _, fila in df.iterrows():
          resultados['procesados'] += 1
          ejecutor.submit(procesar_fila, fila)

      return respuesta_json('Carga por lotes finalizada.', status.HTTP_200_OK, datos=resultados)
      
    except Exception as e:
      print ('Error en Ilm004BatchUploadView: ', str(e))
      return respuesta_json('Error interno al procesar el archivo.', status.HTTP_500_INTERNAL_SERVER_ERROR)


"""
Reglas.
FK: Ilr001, Ilm004, Ilm006
"""
class Ilm006ListView(generics.ListAPIView):
  queryset = Ilm006.objects.all()
  serializer_class = Ilm006Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  # Filtros, ordenar y pagineo 
  filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
  filter_set_fields = ['m006001', 'm006004', 'm006031', 'm006039', 'm006043']

  # Busqueda
  search_fields = ['m006002']

  # Ordenamiento
  ordering_fields = ['m006001', 'm006004']
  ordering = ['m006001']

  def get_queryset(self):
    user = self.request.user
    if not user.has_perm('core.view_ilm006'):
      raise PermissionDenied()
    return super().get_queryset()

class Ilm006CreateView(generics.CreateAPIView):
  queryset = Ilm006.objects.all()
  serializer_class = Ilm006Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  # sobrescribimos el create
  def create(self, request, *args, **kwargs):
    try:
      lc_user = request.user
      if not lc_user.has_perm('core.add_ilm006'):
        raise PermissionDenied()
      
      lc_data = request.data.copy()

      # Campos "automáticos"
      lc_data['m006041'] = lc_user.username
      lc_data['m006042'] = timezone.now()

      if Ilm006.objects.filter(m006001=lc_data.get('m006001')).exists():
        return respuesta_json('Registro ya existe.', status.HTTP_400_BAD_REQUEST)
      
      lc_serializer = self.get_serializer(data=lc_data)
      if lc_serializer.is_valid():
        lc_instancia = lc_serializer.save()
        return respuesta_json('Registro creado satisfactoriamente.', status.HTTP_201_CREATED, datos=Ilm006Serializer(lc_instancia).data)
      
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)
    
    except Exception as e:
      print('Error en Ilm006CreateView: ', str(e))
      return respuesta_json('Ocurrio un error al insertar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)

class Ilm006DetailView(generics.RetrieveAPIView):
  queryset = Ilm006.objects.all()
  serializer_class = Ilm006Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    user = self.request.user
    if not user.has_perm("core.view_ilm006"):
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilm006, m006001=lc_codigo)
  
  def retrieve(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_serializer = self.get_serializer(lc_instancia)
      return respuesta_json('Detalle del registro', status.HTTP_200_OK, datos=lc_serializer.data)
    except Exception as e:
      print("Error en Ilm006DetailView: ", str(e))
      return respuesta_json('Error al leer el registro', status.HTTP_500_INTERNAL_SERVER_ERROR)

class Ilm006UpdateView(generics.UpdateAPIView):
  queryset = Ilm006.objects.all()
  serializer_class = Ilm006Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_user = self.request.user
    if not lc_user:
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilm006, m006001=lc_codigo)
  
  def update(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_data = request.data.copy()

      # no permitir el campo "codigo"
      lc_data.pop('m006001', None)

      # Campos "automaticos"
      lc_data['m006041'] = request.user.username
      lc_data['m006042'] = timezone.now()

      lc_serializer = self.get_serializer(lc_instancia, data=lc_data, partial=True)
      if lc_serializer.is_valid():
        lc_grabar = lc_serializer.save()
        return respuesta_json('Registro actualizador correctamente.', status.HTTP_200_OK, datos=Ilm006Serializer(lc_grabar).data)
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)

    except Exception as e:
      print ('Error en Ilm006UpdateView: ', str(e))
      return respuesta_json('Error al actualizar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)

class Ilm006DeleteView(generics.DestroyAPIView):
  queryset = Ilm006.objects.all()
  serializer_class = Ilm006Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_user = self.request.user
    if not lc_user:
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilm006, m006001=lc_codigo)
  
  def destroy(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_instancia.delete()
      return respuesta_json('Registro eliminado correctamente.', status.HTTP_200_OK)
    except Exception as e:
      print('Error en Ilr002DeleteView: ', str(e))
      return respuesta_json('Error al eliminar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


"""
Horarios laborales.
FK: Ilr001
"""
class Ilr002ListView(generics.ListAPIView):
  queryset = Ilr002.objects.all()
  serializer_class = Ilr002Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  # Filtros, ordenar y pagineo 
  filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
  filter_set_fields = ['r002001']

  # Busqueda
  search_fields = ['r002002']

  # Ordenamiento
  ordering_fields = ['r002001', 'r002002']
  ordering = ['r002001']

  def get_queryset(self):
    user = self.request.user
    if not user.has_perm('core.view_ilr002'):
      raise PermissionDenied()
    return super().get_queryset()

class Ilr002CreateView(generics.CreateAPIView):
  queryset = Ilr002.objects.all()
  serializer_class = Ilr002Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  # sobrescribimos el create
  def create(self, request, *args, **kwargs):
    try:
      lc_user = request.user
      if not lc_user.has_perm('core.add_ilr002'):
        raise PermissionDenied()
      
      lc_data = request.data.copy()

      if Ilr002.objects.filter(r002001=lc_data.get('r002001')).exists():
        return respuesta_json('Registro ya existe.', status.HTTP_400_BAD_REQUEST)
      
      lc_serializer = self.get_serializer(data=lc_data)
      if lc_serializer.is_valid():
        lc_instancia = lc_serializer.save()
        return respuesta_json('Registro creado satisfactoriamente.', status.HTTP_201_CREATED, datos=ILR002Serializer(lc_instancia).data)
      
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)
    
    except Exception as e:
      print('Error en Ilr002CreateView: ', str(e))
      return respuesta_json('Ocurrio un error al insertar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)

class Ilr002DetailView(generics.RetrieveAPIView):
  queryset = Ilr002.objects.all()
  serializer_class = Ilr002Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    user = self.request.user
    if not user.has_perm("core.view_ilr002"):
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilr002, r002001=lc_codigo)
  
  def retrieve(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_serializer = self.get_serializer(lc_instancia)
      return respuesta_json('Detalle del registro', status.HTTP_200_OK, datos=lc_serializer.data)
    except Exception as e:
      print("Error en Ilr002DetailView: ", str(e))
      return respuesta_json('Error al leer el registro', status.HTTP_500_INTERNAL_SERVER_ERROR)

class Ilr002UpdateView(generics.UpdateAPIView):
  queryset = Ilr002.objects.all()
  serializer_class = Ilr002Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_user = self.request.user
    if not lc_user:
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilr002, r002001=lc_codigo)
  
  def update(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_data = request.data.copy()

      lc_serializer = self.get_serializer(lc_instancia, data=lc_data, partial=True)
      if lc_serializer.is_valid():
        lc_grabar = lc_serializer.save()
        return respuesta_json('Registro actualizador correctamente.', status.HTTP_200_OK, datos=Ilr002Serializer(lc_grabar).data)
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)

    except Exception as e:
      print ('Error en Ilr002UpdateView: ', str(e))
      return respuesta_json('Error al actualizar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)

class Ilr002DeleteView(generics.DestroyAPIView):
  queryset = Ilr002.objects.all()
  serializer_class = Ilr002Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_user = self.request.user
    if not lc_user:
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilr002, r002001=lc_codigo)
  
  def destroy(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_instancia.delete()
      return respuesta_json('Registro eliminado correctamente.', status.HTTP_200_OK)
    except Exception as e:
      print('Error en Ilr002DeleteView: ', str(e))
      return respuesta_json('Error al eliminar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


"""
Transacciones con sensibilidad de riesgo
Este mantenimiento de tabla es para una clave compuesta de dos campos.
FK: Ilr001(8)
"""
class Ilm027ListView(generics.ListAPIView):
  queryset = Ilm027.objects.all()
  serializer_class = Ilm027Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  # Filtros, ordenar y pagineo 
  filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
  filterset_fields = ['m027001', 'm027002'] # [Codigo, Secuencia]

  # Busqueda
  search_fields = ['m027003'] # [descripcion]

  # Ordenamiento
  ordering_fiels = ['m027001', 'm027002', 'm027003', 'm027004', 'm027005', 'm027006'] # [Codigo, Secuencia, Descripcion, Sensibilidad, Aprobado_Rech]
  ordering = ['m027001', 'm027002']

  def get_queryset(self):
    user = self.request.user
    if not user.has_perm("core.view_ilm027"):
        raise PermissionDenied()
    return super().get_queryset()

class Ilm027CreateView(generics.CreateAPIView):
  queryset = Ilm027.objects.all()
  serializer_class = Ilm027Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def create(self, request, *args, **kwargs):
    try:
      # Validar usuario autorizado.
      lc_user = request.user
      if not lc_user:
        raise PermissionDenied()
      
      # Copiar la data e incluir campos "automáticos".
      lc_data = request.data.copy()
      lc_data['m027007'] = lc_user.username
      lc_data['m027008'] = timezone.now()

      # Validar existencia
      lc_tabla_id = lc_data.get('m027001')
      lc_item_id = lc_data.get('m027002')
      if Ilm027.objects.filter(m027001=lc_tabla_id, m027002=lc_item_id).exists():
        return respuesta_json('Registro ya existe.', status.HTTP_400_BAD_REQUEST)

      # Actualizar el modelo.
      lc_serializer = self.get_serializer(data=lc_data)
      if lc_serializer.is_valid():
        lc_instancia = lc_serializer.save()
        return respuesta_json('Registros creado correctamente.', status.HTTP_201_CREATED, datos=Ilm027Serializer(lc_instancia).data)
      
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)
    except Exception as e:
      print ('Error en Ilm027CreateView:', str(e))
      return respuesta_json('Ocurrio un error al insertar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)

class Ilm027DetailView(generics.RetrieveAPIView):
  queryset = Ilm027.objects.all()
  serializer_class = Ilm027Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    user = self.request.user
    if not user.has_perm("core.view_ilm027"):
      raise PermissionDenied("Usuario no autorizado.")
    lc_codigo = self.kwargs.get('codigo_id')
    lc_secuencia = self.kwargs.get('secuencia_id')
    if not lc_secuencia:
      lc_secuencia = 0
    return get_object_or_404(Ilm027, m027001=lc_codigo, m027002=lc_secuencia)
  
  def retrieve(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_serializer = self.get_serializer(lc_instancia)
      return respuesta_json('Detalle del registro', status.HTTP_200_OK, datos=lc_serializer.data)
    except Http404:
      return respuesta_json('No existe el registro', status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
      print("Error en Ilm027DetailView: ", str(e))
      return respuesta_json('Error al leer el registro', status.HTTP_500_INTERNAL_SERVER_ERROR)

class Ilm027UpdateView(generics.UpdateAPIView):
  queryset = Ilm027.objects.all()
  serializer_class = Ilm027Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_user = self.request.user
    if not lc_user:
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo_id')
    lc_secuencia = self.kwargs.get('secuencia_id')
    return get_object_or_404(Ilm027, m027001=lc_codigo, m027002=lc_secuencia)
  
  def update(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_data = request.data.copy()

      # Eliminar los campos claves.
      lc_data.pop('m027001', None)
      lc_data.pop('m027002', None)

      # ACtualizar campos "automaticos".
      lc_data['m027007'] = request.user.username
      lc_data['m027008'] = timezone.now()

      lc_serializer = self.get_serializer(lc_instancia, data=lc_data, partial=True)
      if lc_serializer.is_valid():
        lc_grabar = lc_serializer.save()
        return respuesta_json('Registro actualizado correctamente.', status.HTTP_200_OK, datos=Ilm027Serializer(lc_grabar).data)
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)

    except Http404:
      return respuesta_json('No existe el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
      print ('Error en Ilm027UpdateView: ', str(e))
      return respuesta_json('Error al actualizar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)

class Ilm027DeleteView(generics.DestroyAPIView):
  queryset = Ilm027.objects.all()
  serializer_class = Ilm027Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_user = self.request.user
    if not lc_user:
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo_id')
    lc_secuencia = self.kwargs.get('secuencia_id')
    return get_object_or_404(Ilm027, m027001=lc_codigo, m027002=lc_secuencia)
  
  def destroy(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_instancia.delete()
      return respuesta_json('Registro eliminado correctamente.', status.HTTP_200_OK)
    except Http404:
      return respuesta_json('No existe el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
      print('Error en Ilr001DeleteView: ', str(e))
      return respuesta_json('Error al eliminar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


class Ilm016ViewSet(viewsets.ModelViewSet):
  """
  Mantenimiento de tabla de países para validación de reglas.
  FK lógicos: Ilr001 (catálogo de países), Ilm006 (reglas definidas)
  
  FK:
  """
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]
  filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
  serializer_class = Ilm016Serializer
  search_fields = ['pais_display']
  ordering_fields = ['m016001', 'pais_display', 'm016003']
  ordering = ['m016001', 'm016003']

  def get_queryset(self):
    pais_sq = Ilr001.objects.filter(
      r001001 = 3,
      r001004 = '0',
      r001002 = OuterRef('m016003')
    ).values('r001003')[:1]

    return Ilm016.objects.annotate(
      pais_display = Subquery(pais_sq)
    )

  def get_object(self):
    regla = self.kwargs.get('regla_id')
    pais = self.kwargs.get('pais_id')
    return get_object_or_404(Ilm016, m016001=regla, m016003=pais)

  def retrieve(self, request, *args, **kwargs):
    obj = self.get_object()
    serializer = self.get_serializer(obj)
    return respuesta_json('Registro recuperado correctamente.', status.HTTP_200_OK, serializer.data)

  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(
        m016005=request.user.username,
        m016006=timezone.now()
    )
    return respuesta_json("Registro creado correctamente.", status.HTTP_201_CREATED, serializer.data)

  def update(self, request, *args, **kwargs):
    obj = self.get_object()
    datos_actualizables = request.data.copy()
    datos_actualizables.pop('m016001', None)
    datos_actualizables.pop('m016003', None)

    serializer = self.get_serializer(obj, data=datos_actualizables, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save(
        m016005=request.user.username,
        m016006=timezone.now()
    )
    return respuesta_json("Registro modificado correctamente.", status.HTTP_200_OK, serializer.data)

  def destroy(self, request, *args, **kwargs):
    obj = self.get_object()
    obj.delete()
    return respuesta_json("Registro eliminado correctamente.", status.HTTP_204_NO_CONTENT)

