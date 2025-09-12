from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers
from .models import Paciente, Alergia, Patologia, Antecedente, ContactoPaciente
from core.models import ESTATUS_PACIENTES_CHOICES

UserModel = get_user_model()
ESTATUS_MAP = ESTATUS_PACIENTES_CHOICES

class UserNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        return UserModel.objects.create_user(**validated_data)


class PacienteListadoSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(source='usuario.get_full_name', read_only=True)
    estatus_display = serializers.SerializerMethodField()
    class Meta:
        model = Paciente
        fields = ['id', 'nombre_completo', 'telefono', 'estatus', 'estatus_display']

    def get_estatus_display(self, obj):
        return ESTATUS_MAP.get(obj.estatus, 'Desconocido')


class PacienteSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    nombres = serializers.CharField(write_only=True)
    apellidos = serializers.CharField(write_only=True)
    nombre_completo = serializers.CharField(source='usuario.get_full_name', read_only=True)
    
    class Meta:
        model = Paciente
        fields = [
            'id', 'email', 'nombres', 'apellidos', 'usuario', 'nombre_completo',
            'fecha_nacimiento', 'sexo', 'direccion', 'telefono',
            'contacto_emergencia', 'telefono_emergencia', 'estatus'
        ]
        read_only_fields = ['usuario', 'estatus']
        extra_kwargs = {'usuario': {'required': False}}

    def create(self, validated_data):
        email = validated_data.pop('email')
        first_name = validated_data.pop('nombres')
        last_name = validated_data.pop('apellidos')

        user = UserModel.objects.create(
            username = email,
            email = email,
            first_name = first_name,
            last_name = last_name
        )
        user.set_unusable_password()
        user.save()

        # Asignar grupo "Paciente"
        try:
            grupo_paciente = Group.objects.get(name='Paciente')
            user.groups.add(grupo_paciente)
        except Group.DoesNotExist:
            raise serializers.ValidationError('El grupo "Paciente" no existe. Solicite al Administrador que lo cree.')

        validated_data['usuario'] = user
        validated_data['estatus'] = 'AC'
        paciente = Paciente.objects.create(**validated_data)
        return paciente

    def update(self, instance, validated_data):
        # Actualizar datos del usuario si se proporcionan
        user = instance.usuario
        first_name = validated_data.pop('nombres', None)
        last_name = validated_data.pop('apellidos', None)

        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        user.save()

        # Actualizar datos del paciente
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    def validate_telefono(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('El teléfono debe contener solo números.')
        return value

    def validate_fecha_nacimiento(self, value):
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError('La fecha de nacimiento no puede ser futura.')
        return value
    

class AlergiaSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.CharField(source='paciente.usuario.get_full_name', read_only=True)

    class Meta:
        model = Alergia
        fields = ['id', 'paciente', 'paciente_nombre', 'nombre', 'descripcion']


class PatologiaSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.CharField(source='paciente.usuario.get_full_name', read_only=True)

    class Meta:
        model = Patologia
        fields = ['id', 'paciente', 'paciente_nombre', 'nombre', 'cronica']
        read_only = ['fecha_diagnostico']

    def validate_fecha_diagnostico(self, value):
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError('La fecha de diagnóstico no puede ser futura.')
        return value

    def create(self, validated_data):
        validated_data['fecha_diagnostico'] = timezone.now().date()
        patologia = Patologia.objects.create(**validated_data)
        return patologia


class AntecedenteSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.CharField(source='paciente.usuario.get_full_name', read_only=True)

    class Meta:
        model = Antecedente
        fields = ['id', 'paciente', 'paciente_nombre', 'tipo', 'descripcion']


class ContactoPacienteSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.CharField(source='paciente.usuario.get_full_name', read_only=True)

    class Meta:
        model = ContactoPaciente
        fields = ['id', 'paciente', 'paciente_nombre', 'nombre', 'parentesco', 'telefonos']

    def validate_telefonos(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('El teléfono debe contener solo números.')
        return value


class FichaPacienteSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(source='usuario.get_full_name', read_only=True)
    antecedentes = AntecedenteSerializer(many=True, read_only=True)
    patologias = PatologiaSerializer(many=True, read_only=True)
    alergias = AlergiaSerializer(many=True, read_only=True)
    contactos = ContactoPacienteSerializer(many=True, read_only=True)

    class Meta:
        model = Paciente
        fields = [
            'id', 'usuario', 'nombre_completo', 'fecha_nacimiento', 'sexo',
            'direccion', 'telefono', 'contacto_emergencia', 'telefono_emergencia',
            'estatus', 'antecedentes', 'patologias', 'alergias', 'contactos'
        ]