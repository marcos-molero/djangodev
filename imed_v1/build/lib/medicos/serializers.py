from rest_framework import serializers
from .models import Especialidad, Medico, Horario


class EspecialidadSerializer(serializers.ModelSerializer):
  class Meta:
    model = Especialidad
    fields = ['id', 'nombre', 'descripcion']

class HorarioSerializer(serializers.ModelSerializer):
  medico_nombre = serializers.CharField(source='medico.usuario.get_full_name()', read_only=True)
  dia_display = serializers.CharField(source='get_dia_display', read_only=True)

  class Meta:
    model = Horario
    fields = [
      'id', 'descripcion', 'medico', 'medico_nombre', 'dia', 'dia_display', 
      'hora_inicio', 'hora_fin'
    ]

  def validate(self, attrs):
    hora_inicio = attrs.get('hora_inicio')
    hora_fin = attrs.get('hora_fin')
    if hora_inicio and hora_fin and hora_inicio >= hora_fin:
      raise serializers.ValidationError({
        'hora_inicio': 'La hora inicio no puede ser mayor a la hora fin.'
      })
    return attrs

class MedicoSerializer(serializers.ModelSerializer):
  nombre_completo = serializers.CharField(source='usuario.get_full_name', read_only=True)
  especialidad = EspecialidadSerializer(read_only=True)
  especialidad_id = serializers.PrimaryKeyRelatedField(
    queryset = Especialidad.objects.all(), source='especialidad', write_only=True
  )
  horarios = HorarioSerializer(many=True, read_only=True)

  class Meta:
    model = Medico
    fields = ['id', 'usuario', 'nombre_completo', 'licencia', 'telefono', 'especialidad', 
              'especialidad_id', 'horarios', 'fecha_ingreso', 'estatus']
    read_only_fields = ['fecha_ingreso', 'estatus']

  def validate(self, attrs):

    # Si es crear, no permitir el campo "estatus"
    if self.instance is None and 'estatus' in attrs:
      raise serializers.ValidationError({
        'estatus': 'Esta campo no está permitido.',
      })
    
    return attrs