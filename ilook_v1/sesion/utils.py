from django.http import Http404
from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed, PermissionDenied
from rest_framework import status


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

  args:

  returns:
    respuesta_json()
  """
  # Usuario no está autenticado.
  if isinstance(exc, NotAuthenticated):
    return respuesta_json('Error en el token.', status.HTTP_401_UNAUTHORIZED)
  
  # Fallo la autenticación.
  if isinstance(exc, AuthenticationFailed):
    return respuesta_json('Error en la sesión.', status.HTTP_401_UNAUTHORIZED)

  # Sin permisos CRUD.
  if isinstance(exc, PermissionDenied):
    return respuesta_json('Usuario no autorizacion a la acción.', status.HTTP_403_FORBIDDEN)
  
  # No existe
  if isinstance(exc, Http404):
    return respuesta_json('La ruta solicitada no es válida.', status.HTTP_404_NOT_FOUND)

  # Errores no monitorizados.
  #return respuesta_json('Error inesperado.', status.HTTP_500_INTERNAL_SERVER_ERROR)

