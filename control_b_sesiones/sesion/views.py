from django.conf import settings
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework import status
from datetime import timedelta
from .models import SessionToken
from utils.respuesta_json import respuesta_json
import logging

class LoginView(APIView):

  def post(self, request):

    lc_username = request.data.get('username')
    lc_password = request.data.get('password')
    lc_user = authenticate(
      username = lc_username,
      password = lc_password
    )

    if lc_user:
      # Eliminamos los tokens anteriores, por si acaso.
      SessionToken.objects.filter(user=lc_user).delete()
      # Nuevo token.
      lc_token = SessionToken.objects.create(
        user = lc_user,
        expires_at = timezone.now() + timedelta(seconds=settings.TOKEN_EXPIRATION_TIME_IN_SECONDS)
      )
      # Registrar en logger.
      logger = logging.getLogger(__name__)
      logger.info(f"Usuario {lc_user.username} inició sesión.")
      # Respuesta
      return respuesta_json(
        detalle='Inicio de sesión exitoso.',
        codigo=status.HTTP_200_OK,
        datos={'token': str(lc_token.token)}
      )
    
    return respuesta_json(
        detalle='Credenciales inválidas.',
        codigo=status.HTTP_401_UNAUTHORIZED
    )
  

class LogoutView(APIView):

  def post(self, request):

    auth_token = request.headers.get('Authorization')
    if not auth_token or not auth_token.startswith('Bearer '):
      return respuesta_json(detalle='Encabezado Authorization inválido.', codigo=401)
    # Extraer solo el UUID del token
    auth_token = auth_token.split(' ')[1].strip()

    try:
      token = SessionToken.objects.get(token=auth_token)
      token.delete()
      return respuesta_json(
        detalle='Sesion cerrada.',
        codigo=status.HTTP_200_OK
      )
    except SessionToken.DoesNotExist:
      return respuesta_json(
        detalle='Token no válido.',
        codigo=status.HTTP_400_BAD_REQUEST
      )
