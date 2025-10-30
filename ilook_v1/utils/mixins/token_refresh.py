# utils/mixins/token.py

from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from sesion.models import TokenConVencimiento

class TokenRefreshMixin:
  """
  Mixin que extiende la expiración del token si el usuario está autenticado
  y el token es válido.
  """
  def dispatch(self, request, *args, **kwargs):
    token = getattr(request, 'auth', None)

    print(request.user)

    if isinstance(token, TokenConVencimiento) and not token.is_expired():
      token.expires_at = timezone.now() + timedelta(seconds=settings.TOKEN_TIMEOUT_SECONDS)
      token.save(update_fields=['expires_at'])

    return super().dispatch(request, *args, **kwargs)