from django.conf import settings
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework import status
from datetime import timedelta
from .models import SessionToken
from utils import respuesta_json

class LoginView(APIView):

  def post(self, request):

    lc_username = request.data.get('username')
    lc_password = request.data.get('password')
    lc_user = authenticate(
      username = lc_username,
      password = lc_password
    )

    if lc_user:
      lc_token = SessionToken.objects.create(
        user = lc_user,
        expires_at = timezone.now() + timedelta(seconds=settings.TOKEN_EXPIRATION_TIME_IN_SECONDS)
      )
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

    token_str = request.data.get('token')

    try:
      token = SessionToken.objects.get(token=token_str)
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
