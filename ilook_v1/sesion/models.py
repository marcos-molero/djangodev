from datetime import timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from utils.logging import registrar_log, AUDIT_ACCION, AUDIT_CANAL, AUDIT_NIVEL

class TokenConVencimiento(models.Model):
  """
  Modelo: TokenConVencimiento

  Este modelo gestiona tokens únicos asociados a usuarios, con una fecha de creación y una lógica de expiración configurable.

  Campos:
    - key: Identificador único del token.
    - user: Relación uno a uno con el usuario.
    - created_at: Fecha de creación del token.

  Métodos:
    - is_expired(): Retorna True si el token ha vencido según el tiempo definido en settings.TOKEN_VENCE_SEG.
    - __str__(): Representación textual del token.

  Uso típico:
    Se utiliza para validar acciones temporales como recuperación de contraseña, activación de cuenta, etc.
  """
  key = models.CharField(max_length=40, primary_key=True)
  user = models.OneToOneField(User, related_name='token_con_vencimiento', on_delete=models.CASCADE)
  created_at = models.DateTimeField(auto_now_add=True)
  expires_at = models.DateTimeField()
  current_ip = models.CharField(max_length=255)
  user_agent = models.TextField()

  class Meta:
    indexes = [
      models.Index(fields=['user']),
      models.Index(fields=['expires_at'])
    ]
    ordering = ['-expires_at']

  def save(self, *args, **kwargs):
    if not self.expires_at:
      self.expires_at = timezone.now() + timedelta(seconds=settings.TOKEN_TIMEOUT_SECONDS)
    super().save(*args, **kwargs)

  def is_expired(self):
    return timezone.now() > self.expires_at
  
  def __str__(self):
    return f'Token({self.key}) para {self.user.username}'

  @classmethod
  def eliminar_expirados(cls):
      expirados = cls.objects.filter(expires_at__lt=timezone.now())
      cantidad = expirados.count()
      try:
        expirados.delete()
        registrar_log(
          mensaje = f'Se han eliminado {cantidad} entradas de Tokens vencidos.',
          request = None,
          modulo = 'Token.eliminar_vencidos',
          accion = AUDIT_ACCION.eliminar,
          nivel = AUDIT_NIVEL.info,
          canal=AUDIT_CANAL.datos
        )
      except Exception as e:
        registrar_log(
          mensaje = f'Ocurrio un error al eliminar entradas de Tokens vencidos. {str(e)}',
          request = None,
          modulo = 'Token.eliminar_vencidos',
          accion = AUDIT_ACCION.eliminar,
          nivel = AUDIT_NIVEL.info,
          canal=AUDIT_CANAL.datos
        )