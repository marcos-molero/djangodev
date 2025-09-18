from django.db import models

# Create your models here.
class EstiloLiterario(models.Model):
  nombre = models.CharField(max_length=255)

  class Meta:
    verbose_name = 'EstiloLiterario'
    verbose_name_plural = 'EstilosLiterarios'
    ordering = ['nombre']

  def __str__(self):
    return self.nombre


class Autor(models.Model):
  nombre = models.CharField(max_length=255)
  estilo = models.ManyToManyField(EstiloLiterario)
  lugar_nacimiento = models.CharField(max_length=255)
  fecha_nacimiento = models.DateField(blank=True, null=True)
