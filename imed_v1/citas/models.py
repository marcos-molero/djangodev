from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from medicos.models import Medico, Horario
from pacientes.models import Paciente
from core.models import DIAS_MAP

class Cita(models.Model):
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='citas')
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='citas')
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        unique_together = ('medico', 'fecha', 'hora')  # evita duplicados

    def __str__(self):
        return f'{self.fecha} {self.hora} - {self.paciente} con {self.medico}'

    def clean(self):
        # Validar que la hora esté dentro del horario del médico
        dia_codigo = DIAS_MAP[self.fecha.strftime('%a').upper()]
        horarios = Horario.objects.filter(medico=self.medico, dia=dia_codigo)
        if not horarios.exists():
            raise ValidationError('El médico no tiene horario para ese día.')

        dentro_de_horario = any(h.hora_inicio <= self.hora < h.hora_fin for h in horarios)
        if not dentro_de_horario:
            raise ValidationError('La hora seleccionada no está dentro del horario del médico.')
        
        if Cita.objects.filter(medico=self.medico, fecha=self.fecha, hora=self.hora).exclude(pk=self.pk).exists():
            raise ValidationError('Ya existe una cita para ese médico en esa hora.')
        
        # Validar máximo de citas por día
        total_citas = Cita.objects.filter(medico=self.medico, fecha=self.fecha).exclude(pk=self.pk).count()
        if total_citas >= settings.MAXIMO_CITAS_POR_DIA:
          raise ValidationError(f'El médico ya tiene {settings.MAXIMO_CITAS_POR_DIA} citas para ese día.')

        # Validar que la hora esté alineada con el bloque de atención
        minutos = self.hora.minute
        if minutos % settings.TIEMPO_ATENCION_MINUTOS != 0:
            raise ValidationError(
                f'La hora debe estar alineada a bloques de {settings.TIEMPO_ATENCION_MINUTOS} minutos. '
                f'Por ejemplo: 08:00, 08:15, 08:30...'
            )

        # Validar que el paciente no tenga otra cita con el mismo médico ese día
        cita_existente = Cita.objects.filter(
            medico=self.medico,
            paciente=self.paciente,
            fecha=self.fecha
        ).exclude(pk=self.pk)

        if cita_existente.exists():
            raise ValidationError(
                f'El paciente ya tiene una cita con este médico el {self.fecha}. Solo se permite una por día.'
            )
