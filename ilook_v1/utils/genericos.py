from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed, PermissionDenied, ValidationError, NotFound
from rest_framework import status
from django.http import Http404
from utils.logging import registrar_log, AUDIT_ACCION, AUDIT_CANAL, AUDIT_NIVEL

def respuesta_json(detalle, codigo=status.HTTP_200_OK, datos=None):
  """
  Respuestas genericas de la aplicación.

  args:
    detalle (str): Mensaje detallando el error o finalizacion del proceso.
    codigo (str): Codigo HTTP de respuesta.
    datos (str): Datos adicionales del error

  returns:
    Response
  """
  return Response({
    'codigo': codigo,
    'detalle': detalle,
    'datos': datos
  }, status=codigo)


def custom_exception_handler(exc, context):
  """
  Manejo estandar de la aplicacion para los errores.
  - Si una vista API lanza AuthenticationFailed, PermissionDenied, etc. 
    → se captura por custom_exception_handler.
  - Si un usuario accede a una ruta inexistente como /api/xyz 
    → se captura por handler404 = 'ws.views.custom_404_view'.
  - Si ocurre un error interno no capturado en una vista tradicional 
    → entra custom_500_view.

  args:

  returns:
    respuesta_json()
  """
  request = context.get('request')

  # Usuario no está autenticado.
  if isinstance(exc, NotAuthenticated):
    return respuesta_json('Error en el token.', status.HTTP_401_UNAUTHORIZED)
  
  # Fallo la autenticación.
  if isinstance(exc, AuthenticationFailed):
    registrar_log(mensaje='Sesion no autenticada.', request=request, modulo='auth', accion=AUDIT_ACCION.acceso, nivel=AUDIT_NIVEL.warning, canal=AUDIT_CANAL.autorizacion)
    return respuesta_json('Sesion no autenticada.', status.HTTP_401_UNAUTHORIZED)

  # Sin permisos CRUD.
  if isinstance(exc, PermissionDenied):
    return respuesta_json('Usuario no autorizado a la acción.', status.HTTP_403_FORBIDDEN)
  
  # No existe
  if isinstance(exc, Http404):
    return respuesta_json('El recurso solicitado no es valido.', status.HTTP_404_NOT_FOUND)

  # Errores de Validation Error
  if isinstance(exc, ValidationError) or isinstance(exc, NotFound):
    return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=exc.detail if hasattr(exc, "detail") else str(exc))

  # Errores no monitorizados.
  registrar_log(mensaje=f'Error inesperado en {request.path} del servidor. [{exc.detail if hasattr(exc, "detail") else str(exc)}]', request=request, modulo='sistema', accion='global', nivel='error')
  return respuesta_json(f'Error inesperado en {request.path} del servidor.', status.HTTP_500_INTERNAL_SERVER_ERROR)


def manejar_error(request, mensaje_usuario, codigo, exception=None):
  """
  Helper: Manejo generico de HTTP error handlers.
  Genera registro en Loggers.

  parms:
    - mensaje_usuario - str : El mensaje que queremos enviar al logger.
    - codigo - int : Codigo de error HTTP.

  returns:
    - None

  """
  try:
    return respuesta_json(mensaje_usuario, codigo=codigo)
  except Exception as e:
    registrar_log(
      mensaje = f'Error en handler {codigo} - {str(exception)} - {str(e)}',
      usuario = getattr(request.user, 'username', 'anonimo'),
      ip = request.META.get('REMOTE_ADDR'),
      ua = request.headers.get('User-Agent', ''),
      nivel = 'error',
      canal = 'app'
    )