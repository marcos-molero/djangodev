from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from sesion.utils import respuesta_json
from core.models import TokenConVencimiento
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
    
    print(request)

    # Verificamos que la aplicacion sea correcta.
    if request.content_type != 'application/json':
      return respuesta_json('El tipo de contenido debe ser application/json.', status.HTTP_400_BAD_REQUEST)

    # Recuperamos los campos del POST.
    try:
      lc_username = request.data.get('username')
      lc_password = request.data.get('password')
    except Exception:
      return respuesta_json('Error en la estructura del cuerpo JSON.', status.HTTP_400_BAD_REQUEST)

    if not lc_username or not lc_password:
      return respuesta_json('Los campos usuario y contraseña son necesarios.', status.HTTP_400_BAD_REQUEST)
    
    # Validar contra la BD Django
    lc_user = authenticate(username=lc_username, password=lc_password)
    if lc_user is None:
      return respuesta_json('La combinación usuario y contraseña es inválida.', status.HTTP_400_BAD_REQUEST)
    
    # Creamos el token
    TokenConVencimiento.objects.filter(user=lc_user).delete()
    token = TokenConVencimiento.objects.create(user=lc_user, key=secrets.token_hex(20))

    # Devolver mensaje.
    return respuesta_json('Conectado', datos={'usuario': lc_user.username, 'token': token.key})
  

class LogoutView(APIView):
  """
  Desconectarse del sistema.
  """
  def post(self, request):
    lc_token = request.auth
    if not lc_token:
      return respuesta_json('Error en el token.', status.HTTP_401_UNAUTHORIZED)
    
    lc_token.delete()
    return respuesta_json('Desconectado')