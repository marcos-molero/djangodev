from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from sesion.models import TokenConVencimiento

class RefrescarTokenMiddleware:
  """
  Middleware que extiende la expiración del token si el usuario está autenticado.

  args:
    token

  returns:
    none
  """

  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    token = getattr(request, 'auth', None)
    print(request.user)

    if isinstance(token, TokenConVencimiento) and not token.is_expired():
      # Actualiza la expiración
      token.expires_at = timezone.now() + timedelta(seconds=settings.TOKEN_TIMEOUT_SECONDS)
      token.save(update_fields=['expires_at'])

    return self.get_response(request)