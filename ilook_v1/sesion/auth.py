from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from core.models import TokenConVencimiento

class TokenConVencimientoAutenticacion(TokenAuthentication):
    model = TokenConVencimiento

    def autenticar_credencial(self, key):
        try:
            token = TokenConVencimiento.objects.get(key=key)
        except TokenConVencimiento.DoesNotExist:
            raise AuthenticationFailed('Error en el token.')

        if token.is_expired():
            token.delete()
            raise AuthenticationFailed('Sesión expirada.')

        return (token.user, token)