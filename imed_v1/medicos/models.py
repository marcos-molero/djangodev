from django.db import models
from django.contrib.auth import get_user_model
from django.forms import ValidationError
from core.models import DIAS_CHOICES, ESTATUS_MEDICOS_CHOICES

# Create your models here.
class Especialidad(models.Model):
  nombre = models.CharField(max_length=100, unique=True)
  descripcion = models.TextField(blank=True)

  class Meta:
    ordering = ['nombre']
    verbose_name = 'Especialidad'
    verbose_name_plural = 'Especialidades'

  def __str__(self):
    return self.nombre
  

class Medico(models.Model):
  usuario = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
  licencia = models.CharField(max_length=50)
  telefono = models.CharField(max_length=20)
  especialidad = models.ForeignKey(Especialidad, on_delete=models.SET_NULL, null=True)
  fecha_ingreso = models.DateField()
  estatus = models.CharField(max_length=2, choices=ESTATUS_MEDICOS_CHOICES)

  class Meta:
    indexes = [
      models.Index(fields=['especialidad']),
      models.Index(fields=['estatus']),
    ]
    verbose_name = 'Medico'
    verbose_name_plural = 'Medicos'

  def __str__(self):
    return self.usuario.get_full_name().upper()


class Horario(models.Model):
  descripcion = models.CharField(max_length=20)
  medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='horarios')
  dia = models.CharField(max_length=2, choices=DIAS_CHOICES)
  hora_inicio = models.TimeField()
  hora_fin = models.TimeField()

  class Meta:
    verbose_name = 'Horario'
    verbose_name_plural = 'Horario'

  def __str__(self):
    return f'{self.medico.usuario.get_full_name().upper()} - {self.get_dia_display()} {self.hora_inicio} - {self.hora_fin}'

  def clean(self):
    if self.hora_inicio >= self.hora_fin:
      raise ValidationError('La hora inicio debe ser menor a la hora fin.')
    
