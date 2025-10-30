from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from utils.genericos import respuesta_json
from .models import TokenConVencimiento
from utils.logging import registrar_log, AUDIT_ACCION, AUDIT_CANAL, AUDIT_NIVEL
import secrets

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
  """
  Conexión, token para sesiónes de ahora en adelante.
  """  
  # Limpiamos las clases
  authentication_classes = []
  permission_classes = []

  # Metodo POST
  def post(self, request):

    # Verificamos que la aplicacion sea correcta.
    if request.content_type != 'application/json':
      registrar_log(mensaje='El tipo de contenido debe ser application/json.', request=request, modulo='auth', accion=AUDIT_ACCION.conectarse, nivel=AUDIT_NIVEL.error, canal=AUDIT_CANAL.autorizacion)
      return respuesta_json('El tipo de contenido debe ser application/json.', status.HTTP_400_BAD_REQUEST)

    # Recuperamos los campos del POST.
    try:
      lc_username = request.data.get('username')
      lc_password = request.data.get('password')
    except Exception:
      registrar_log(mensaje='Error en la estructura del cuerpo JSON.', request=request, modulo='auth', accion=AUDIT_ACCION.conectarse, nivel=AUDIT_NIVEL.error, canal=AUDIT_CANAL.autorizacion)
      return respuesta_json('Error en la estructura del cuerpo JSON.', status.HTTP_400_BAD_REQUEST)

    if not lc_username or not lc_password:
      registrar_log(mensaje='Los campos usuario y contraseña son necesarios.', request=request, modulo='auth', accion=AUDIT_ACCION.conectarse, nivel=AUDIT_NIVEL.error, canal=AUDIT_CANAL.autorizacion)
      return respuesta_json('Los campos usuario y contraseña son necesarios.', status.HTTP_400_BAD_REQUEST)
    
    # Validar contra la BD Django
    lc_user = authenticate(username=lc_username, password=lc_password)
    if lc_user is None:
      registrar_log(mensaje='La combinación usuario y contraseña es inválida.', request=request, modulo='auth', accion=AUDIT_ACCION.conectarse, nivel=AUDIT_NIVEL.error, canal=AUDIT_CANAL.autorizacion)
      return respuesta_json('La combinación usuario y contraseña es inválida.', status.HTTP_400_BAD_REQUEST)
    
    # Eliminamos los token del usuario.
    TokenConVencimiento.objects.filter(user=lc_user).delete()

    # Creamos un token unico.
    lc_token = ''
    while True:
      lc_token = secrets.token_hex(20)
      if not TokenConVencimiento.objects.filter(key=lc_token):
        break

    ip = request.META.get('REMOTE_ADDR')
    ua = request.META.get('HTTP_USER_AGENT', '')

    token = TokenConVencimiento.objects.create(user=lc_user, key=lc_token, current_ip=ip, user_agent=ua)

    # Devolver mensaje.
    registrar_log(mensaje='Conectado.', request=request, modulo='auth', accion=AUDIT_ACCION.conectarse, nivel=AUDIT_NIVEL.info, canal=AUDIT_CANAL.autorizacion)
    return respuesta_json('Conectado', datos={'usuario': lc_user.username, 'token': token.key})
  

class LogoutView(APIView):
  """
  Desconectarse del sistema.
  """
  def post(self, request):

    lc_token = request.auth

    if not lc_token:
      registrar_log(mensaje=f'Error en el token. Usuario={request.user.username}, Token={lc_token}', request=request, modulo='auth', accion=AUDIT_ACCION.desconectarse, nivel=AUDIT_NIVEL.error, canal=AUDIT_CANAL.autorizacion)
      return respuesta_json('Error en el token.', status.HTTP_401_UNAUTHORIZED)
    
    if not isinstance(lc_token, TokenConVencimiento):
      registrar_log(mensaje=f'Token inválido en logout para {request.user}', request=request, modulo='auth', accion=AUDIT_ACCION.desconectarse, nivel=AUDIT_NIVEL.error, canal=AUDIT_CANAL.autorizacion)
      return respuesta_json('Token inválido.', status.HTTP_401_UNAUTHORIZED)

    lc_token.delete()
    registrar_log(mensaje=f'Logout exitoso.', request=request, modulo='auth', accion=AUDIT_ACCION.desconectarse, nivel=AUDIT_NIVEL.info, canal=AUDIT_CANAL.autorizacion)
    return respuesta_json('Desconectado')