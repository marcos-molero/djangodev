from django.db import models

# Create your models here.
class AuditoriaValidacion(models.Model):
  fecha = models.DateTimeField(auto_now=True)
  proceso = models.CharField(max_length=255)
  proceso_validacion = models.CharField(max_length=255)
  mensaje = models.CharField(max_length=255)
  datos = models.TextField()

  class Meta:
    db_table_comment = 'iLook - Auditoria interna, archivos recibidos.'
    verbose_name = 'Auditoria'
    verbose_name_plural = 'Auditorias'
