from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Paciente, Alergia, Patologia, Antecedente, ContactoPaciente
from .serializers import (
    PacienteListadoSerializer, PacienteSerializer, FichaPacienteSerializer, AlergiaSerializer,
    PatologiaSerializer, AntecedenteSerializer, ContactoPacienteSerializer
)


class PacienteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['sexo', 'estatus']
    serializer_class = PacienteSerializer

    def get_queryset(self):
        queryset = Paciente.objects.select_related('usuario').prefetch_related(
            'antecedentes', 'patologias', 'alergias', 'contactos'
        ).order_by('id')

        nombres = self.request.query_params.get('nombres')
        apellidos = self.request.query_params.get('apellidos')
        email = self.request.query_params.get('email')

        if nombres:
            queryset = queryset.filter(usuario__first_name__icontains=nombres)
        if apellidos:
            queryset = queryset.filter(usuario__last_name__icontains=apellidos)
        if email:
            queryset = queryset.filter(usuario__email__icontains=email)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().order_by('id'))
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = PacienteListadoSerializer(page, many=True)
            return self.get_paginated_response({
                'detalle': 'Listado de pacientes',
                'estatus': status.HTTP_200_OK,
                'datos': serializer.data
            })

        serializer = PacienteListadoSerializer(queryset, many=True)
        return Response({
            'detalle': 'Listado de pacientes',
            'estatus': status.HTTP_200_OK,
            'datos': serializer.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(estatus='AC')
        return Response({
            'detalle': 'Paciente creado correctamente',
            'estatus': status.HTTP_201_CREATED,
            'datos': serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'detalle': 'Detalle del paciente',
            'estatus': status.HTTP_200_OK,
            'datos': serializer.data
        })

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'detalle': 'Paciente actualizado correctamente',
            'estatus': status.HTTP_200_OK,
            'datos': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.estatus = '99'
        instance.save()
        return Response({
            'detalle': 'Paciente marcado como inactivo',
            'estatus': status.HTTP_200_OK,
            'datos': {}
        })

    @action(detail=True, methods=['get'], url_path='ficha')
    def ficha_clinica(self, request, pk=None):
        paciente = self.get_object()
        serializer = FichaPacienteSerializer(paciente)
        return Response({
            'detalle': 'Ficha clínica del paciente',
            'estatus': status.HTTP_200_OK,
            'datos': serializer.data
        })


class AlergiaViewSet(viewsets.ModelViewSet):
    queryset = Alergia.objects.select_related('paciente__usuario').order_by('id')
    serializer_class = AlergiaSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'detalle': 'Listado de alergias',
                'estatus': status.HTTP_200_OK,
                'datos': serializer.data
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'detalle': 'Listado de alergias',
            'estatus': status.HTTP_200_OK,
            'datos': serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'detalle': 'Detalle de la alergia',
            'estatus': status.HTTP_200_OK,
            'datos': serializer.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'detalle': 'Alergia registrada correctamente',
            'estatus': status.HTTP_201_CREATED,
            'datos': serializer.data
        })

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'detalle': 'Alergia actualizada correctamente',
            'estatus': status.HTTP_200_OK,
            'datos': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({
            'detalle': 'Alergia eliminada correctamente',
            'estatus': status.HTTP_204_NO_CONTENT,
            'datos': {}
        })
    

class PatologiaViewSet(viewsets.ModelViewSet):
    queryset = Patologia.objects.select_related('paciente__usuario').order_by('id')
    serializer_class = PatologiaSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filterset_fields = ['nombre', 'fecha_diagnostico']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'detalle': 'Listado de patologias',
                'estatus': status.HTTP_200_OK,
                'datos': serializer.data
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'detalle': 'Listado de patologias',
            'estatus': status.HTTP_200_OK,
            'datos': serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'detalle': 'Detalle de la patologias',
            'estatus': status.HTTP_200_OK,
            'datos': serializer.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'detalle': 'Patologia registrada correctamente',
            'estatus': status.HTTP_201_CREATED,
            'datos': serializer.data
        })

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'detalle': 'Patologia actualizada correctamente',
            'estatus': status.HTTP_200_OK,
            'datos': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({
            'detalle': 'Patologia eliminada correctamente',
            'estatus': status.HTTP_204_NO_CONTENT,
            'datos': {}
        })


class AntecedenteViewSet(viewsets.ModelViewSet):
    queryset = Antecedente.objects.select_related('paciente__usuario').order_by('id')
    serializer_class = AntecedenteSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filterset_fields = ['tipo']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'detalle': 'Listado de antecedentes',
                'estatus': status.HTTP_200_OK,
                'datos': serializer.data
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'detalle': 'Listado de antecedentes',
            'estatus': status.HTTP_200_OK,
            'datos': serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'detalle': 'Detalle del antecedente',
            'estatus': status.HTTP_200_OK,
            'datos': serializer.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'detalle': 'Antecedente registrada correctamente',
            'estatus': status.HTTP_201_CREATED,
            'datos': serializer.data
        })

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'detalle': 'Antecedente actualizada correctamente',
            'estatus': status.HTTP_200_OK,
            'datos': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({
            'detalle': 'Antecedente eliminada correctamente',
            'estatus': status.HTTP_204_NO_CONTENT,
            'datos': {}
        })


class ContactoPacienteViewSet(viewsets.ModelViewSet):
    queryset = ContactoPaciente.objects.select_related('paciente__usuario').order_by('id')
    serializer_class = ContactoPacienteSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filterset_fields = ['nombre']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'detalle': 'Listado de contactos',
                'estatus': status.HTTP_200_OK,
                'datos': serializer.data
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'detalle': 'Listado de contactos',
            'estatus': status.HTTP_200_OK,
            'datos': serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'detalle': 'Detalle del contacto',
            'estatus': status.HTTP_200_OK,
            'datos': serializer.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'detalle': 'Contacto registrada correctamente',
            'estatus': status.HTTP_201_CREATED,
            'datos': serializer.data
        })

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'detalle': 'Contacto actualizada correctamente',
            'estatus': status.HTTP_200_OK,
            'datos': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({
            'detalle': 'Contacto eliminada correctamente',
            'estatus': status.HTTP_204_NO_CONTENT,
            'datos': {}
        })


class FichaPacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = FichaPacienteSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    # Filtros
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['sexo', 'estatus'] # <-- Esto es busqueda exacta MATCH
    search_fields = ['usuario__first_name', 'usuario__last_name', 'direccion'] #<-- Esto es busqueda parcial LIKE.
    ordering_fields = ['fecha_nacimiento', 'id']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'detalle': 'Listado de fichas de pacientes',
                'estatus': status.HTTP_200_OK,
                'datos': serializer.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return self.get_paginated_response({
            'detalle': 'Listado de fichas de pacientes',
            'estatus': status.HTTP_200_OK,
            'datos': serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.get_paginated_response({
            'detalle': 'Fichas del paciente',
            'estatus': status.HTTP_200_OK,
            'datos': serializer.data
        })
