from rest_framework import serializers
from .models import Autor, EstiloLiterario


class EstiloLiterarioSerializer(serializers.ModelSerializer):
  class Meta:
    model = EstiloLiterario
    fields = ['id', 'nombre']


class AutorSerializer(serializers.ModelSerializer): 
  estilos=EstiloLiterarioSerializer(many=True, read_only=True)
  estilos_ids=serializers.PrimaryKeyRelatedField(
    queryset=EstiloLiterario.objects.all(),
    many=True,
    write_only=True,
    source='estilos'
  )
  class Meta: 
    model = Autor 
    fields = [
      'id', 'nombre', 'apellido', 'nacionalidad', 'fecha_nacimiento', 'biografia',
      'estilos', 'estilos_ids'
    ]

