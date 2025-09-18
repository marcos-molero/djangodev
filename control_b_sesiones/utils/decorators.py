from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from sesion.models import SessionToken
from .respuesta_json import respuesta_json

def token_valido(token_str):
  try:
    token = SessionToken.objects.get(token=token_str)
    if token.is_expired():
      return None, 'Token Expirado'
    return token.user, None
  except SessionToken.DoesNotExist:
    return None, 'Token Inválido'


def accion_autorizada(user, accion, modelo):
  accion = accion.lower()
  permiso_codificado = f'{modelo._meta.app_label}.{accion}_{modelo._meta.model_name}'
  return user.has_perm(permiso_codificado)


def validar_token_y_permiso(accion, modelo):
  
  def decorator(view_func):
  
    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
      auth_token = request.headers.get('Authorization')
      if not auth_token or not auth_token.startswith('Bearer '):
        return respuesta_json(detalle='Encabezado Authorization inválido.', codigo=401)
      # Extraer solo el UUID del token
      auth_token = auth_token.split(' ')[1].strip()

      user, error = token_valido(auth_token)
      if error:
        return respuesta_json(
          detalle = error,
          codigo = status.HTTP_401_UNAUTHORIZED
        )
      if not accion_autorizada(user, accion, modelo):
        return respuesta_json(
          detalle = 'Usuario no autorizado a la acción.',
          codigo = status.HTTP_405_METHOD_NOT_ALLOWED
        )
      
      request.user = user
      return view_func(self, request, *args, **kwargs)
    
    return _wrapped_view
  
  return decorator