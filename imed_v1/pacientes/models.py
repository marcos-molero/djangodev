from django.db import models
from django.contrib.auth import get_user_model
from core.models import ESTATUS_PACIENTES_CHOICES, SEXO_CHOICES, PARENTESCO_CHOICES


class Paciente(models.Model):
    usuario = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)
    contacto_emergencia = models.CharField(max_length=100)
    telefono_emergencia = models.CharField(max_length=20)
    estatus = models.CharField(max_length=2, choices=ESTATUS_PACIENTES_CHOICES)

    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'

    def __str__(self):
        return self.usuario.get_full_name()


class Alergia(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='alergias')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Alergia'
        verbose_name_plural = 'Alergias'

    def __str__(self):
        return f'{self.nombre} ({self.paciente.usuario.get_full_name()})'


class Patologia(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='patologias')
    nombre = models.CharField(max_length=100)
    cronica = models.BooleanField()
    fecha_diagnostico = models.DateField()

    class Meta:
        verbose_name = 'Patologia'
        verbose_name_plural = 'Patologias'

    def __str__(self):
        return f'{self.nombre} ({self.paciente})'


class Antecedente(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='antecedentes')
    tipo = models.CharField(max_length=200)
    descripcion = models.TextField()

    class Meta:
        verbose_name = 'Antecedente'
        verbose_name_plural = 'Antecedentes'

    def __str__(self):
        return f'{self.tipo} ({self.paciente})'


class ContactoPaciente(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='contactos')
    nombre = models.CharField(max_length=100)
    parentesco = models.CharField(max_length=2, choices=PARENTESCO_CHOICES)
    telefonos = models.CharField(max_length=20)

    class Meta:
        verbose_name = 'Contacto de Emergencia'
        verbose_name_plural = 'Contactos de Emergencia'

    def __str__(self):
        return f'{self.nombre} ({self.parentesco})'