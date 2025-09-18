import uuid
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
  fecha_nacimiento=models.DateField(null=True, blank=True)
  lugar_nacimiento=models.CharField(max_length=255, null=True, blank=True)
  direccion=models.TextField(null=True, blank=True)
  telefono=models.CharField(max_length=20, null=True, blank=True)

class SessionToken(models.Model):
  user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
  token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
  created_at = models.DateTimeField(auto_now_add=True)
  expires_at = models.DateTimeField(db_index=True)

  def is_expired(self):
    return timezone.now() > self.expires_at
  
  def __str__(self):
    return f'Token de {self.user.username} - Expira: {self.expires_at}'