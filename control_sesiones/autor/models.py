from django.db import models
from django.db import models 

# Create your models here.
class EstiloLiterario(models.Model):
  nombre = models.CharField(max_length=100, unique=True)

  class Meta:
    verbose_name = 'EstiloLiterario'
    verbose_name_plural = 'EstilosLiterarios'
    ordering = ['nombre']

  def __str__(self): 
    return self.nombre 


class Autor(models.Model): 
  nombre = models.CharField(max_length=100) 
  apellido = models.CharField(max_length=100) 
  nacionalidad = models.CharField(max_length=50, blank=True, null=True) 
  fecha_nacimiento = models.DateField(blank=True, null=True) 
  biografia = models.TextField(blank=True, null=True) 
  estilos = models.ManyToManyField(EstiloLiterario, related_name='autores') 

  class Meta:
    verbose_name = 'Autor'
    verbose_name_plural = 'Autores'
    ordering = ['apellido', 'nombre']

  def __str__(self): 
    return f"{self.apellido.upper()}, {self.nombre}" 
