from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from .models import TokenConVencimiento
from utils.logging import registrar_log, AUDIT_ACCION, AUDIT_CANAL, AUDIT_NIVEL

class TokenConVencimientoAutenticacion(TokenAuthentication):
	model = TokenConVencimiento

	def authenticate(self, request):
		"""
		Acceso directo al request para validar IP y User-Agent.
		Logging enriquecido para trazabilidad de sesiones.
		Posibilidad de extender lógica: rechazar si IP/UA no coinciden, registrar actividad, etc.

		parms:
			- request 

		returns:
			- user
			- token

		"""
		if getattr(request._request, '_auth_logged', False) or getattr(request._request, '_auth_failed_logged', False):
			return super().authenticate(request)
		
		auth = get_authorization_header(request).split()
		
		if not auth or auth[0].lower() != b'token':
			return None
		
		if len(auth) == 1:
			raise AuthenticationFailed('Token no proporcionado.')

		if len(auth) > 2:
			raise AuthenticationFailed('Token no proporcionado.')
		
		try:
			key = auth[1].decode()
		except UnicodeError:
			raise AuthenticationFailed('Token con caracteres inválidos.')

		try:
			user, token = self.authenticate_credentials(key, request)
			return (user, token)
		except AuthenticationFailed as e:
			raise 


	def refresh_token_expires_at(self, token):
		"""
		Actualizar expiración del token
		"""
		token.expires_at = timezone.now() + timedelta(seconds=settings.TOKEN_TIMEOUT_SECONDS)
		token.save(update_fields=['expires_at'])
		return (token.user, token)


	def authenticate_credentials(self, key, request):
		"""
		Este método sobrescribe authenticate_credentials() de DRF, pero ello el nombre en ingles.
		"""
		ip = request.META.get('REMOTE_ADDR')
		ua = request.META.get('HTTP_USER_AGENT', '')

		try:
			token = TokenConVencimiento.objects.get(key=key)
		except TokenConVencimiento.DoesNotExist:
			raise AuthenticationFailed('Error en el token.')

		if token.is_expired():
			token.delete()
			raise AuthenticationFailed('Sesión expirada.')
		
		if token.current_ip != ip:
			raise AuthenticationFailed('Acceso desde IP no autorizada.')

		if token.user_agent != ua:
			raise AuthenticationFailed('Acceso desde el dispositivo no autorizado.')

		self.refresh_token_expires_at(token)
		return (token.user, token)
	