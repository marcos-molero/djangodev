from rest_framework import serializers
from .models import Autor

class AutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Autor
        fields = [
            'id', 'nombre', 'lugar_nacimiento', 'fecha_nacimiento'
        ]
