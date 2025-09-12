from django.forms import ValidationError
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Medico, Especialidad, Horario
from .serializers import MedicoSerializer, EspecialidadSerializer, HorarioSerializer
from core.models import DIAS_CHOICES


DIAS_MAP = dict(DIAS_CHOICES)


class MedicoViewSet(viewsets.ModelViewSet):
    queryset = Medico.objects.select_related('usuario', 'especialidad').prefetch_related('horarios')
    serializer_class = MedicoSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['especialidad', 'estatus']
    search_fields = ['usuario__lastname', 'usuario__firstname', 'licencia', 'especialidad']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "detalle": "Listado de médicos",
            "estatus": status.HTTP_200_OK,
            "datos": serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "detalle": "Detalle del médico",
            "estatus": status.HTTP_200_OK,
            "datos": serializer.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "detalle": "Médico creado correctamente",
            "estatus": status.HTTP_201_CREATED,
            "datos": serializer.data
        })
    
    def perform_create(self, serializer):
        serializer.save(
            fecha_ingreso = timezone.now().date(),
            estatus = '00'
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "detalle": "Médico actualizado correctamente",
            "estatus": status.HTTP_200_OK,
            "datos": serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "detalle": "Médico eliminado",
            "estatus": status.HTTP_204_NO_CONTENT,
            "datos": {}
        })


class DisponibilidadMedicoView(APIView):
    def get(self, request, medico_id, dia):
        horarios = Horario.objects.filter(medico_id=medico_id, dia=dia)
        serializer = HorarioSerializer(horarios, many=True)
        return Response({
            "detalle": "Disponibilidad del médico",
            "estatus": status.HTTP_200_OK,
            "datos": serializer.data
        })


class EspecialidadViewSet(viewsets.ModelViewSet):
    queryset = Especialidad.objects.all()
    serializer_class = EspecialidadSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['nombre']
    search_fields = ['nombre']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "detalle": "Listado de Especialidades",
                "estatus": status.HTTP_200_OK,
                "datos": serializer.data
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "detalle": "Listado de Especialidades",
            "estatus": status.HTTP_200_OK,
            "datos": serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "detalle": "Detalle de la especialidad",
            "estatus": status.HTTP_200_OK,
            "datos": serializer.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "detalle": "Especialidad creada correctamente",
            "estatus": status.HTTP_201_CREATED,
            "datos": serializer.data
        })

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "detalle": "Especialidad actualizado correctamente",
            "estatus": status.HTTP_200_OK,
            "datos": serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "detalle": "Especialidad eliminado",
            "estatus": status.HTTP_204_NO_CONTENT,
            "datos": {}
        })
    

class HorarioViewSet(viewsets.ModelViewSet):
    queryset = Horario.objects.select_related('medico__usuario')
    serializer_class = HorarioSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['medico', 'dia', 'descripcion']
    search_fields = ['descripcion', 'medico__usuario__firstname', 'medico__usuario__lastname', 'medico__especialidad']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        agrupado = {}

        horarios = page if page is None else queryset

        for horario in horarios:
            medico_nombre = horario.medico.usuario.get_full_name()
            descripcion = horario.descripcion
            dia_nombre = self.DIAS_MAP.get(horario.dia, horario.dia)

            if medico_nombre not in agrupado:
                agrupado[medico_nombre] = {}

            if descripcion not in agrupado[medico_nombre]:
                agrupado[medico_nombre][descripcion] = {'dias': {}}

            agrupado[medico_nombre][descripcion]['dias'][dia_nombre] = {
                'hora_inicio': horario.hora_inicio.strftime('%H:%M:%S'),
                'hora_fin': horario.hora_fin.strftime('%H:%M:%S'),
            }

        resultado = []
        for medico, turnos in agrupado.items():
            resultado.append({
                'medico_nombre': medico,
                'turnos': turnos
            })

        if page is not None:
            return self.get_paginated_response({
                "detalle": "Listado de horarios",
                "estatus": status.HTTP_200_OK,
                "datos": resultado
            })

        return Response({
            "detalle": "Listado de horarios",
            "estatus": status.HTTP_200_OK,
            "datos": resultado
        })

    def retrieve(self, request, *args, **kwargs):
        medico_id = kwargs.get('pk')  # Usamos pk como identificador del médico

        try:
            medico = Medico.objects.get(pk=medico_id)
        except Medico.DoesNotExist:
            return Response({
                'detalle': 'Médico no encontrado',
                'estatus': status.HTTP_404_NOT_FOUND,
                'datos': {}
            })

        horarios = Horario.objects.filter(medico=medico)
        agrupado = {}

        for horario in horarios:
            descripcion = horario.descripcion
            dia_codigo = horario.dia
            dia_nombre = DIAS_MAP.get(dia_codigo, dia_codigo)

            if descripcion not in agrupado:
                agrupado[descripcion] = {'dias': {}}

            agrupado[descripcion]['dias'][dia_nombre] = {
                'hora_inicio': horario.hora_inicio.strftime('%H:%M:%S'),
                'hora_fin': horario.hora_fin.strftime('%H:%M:%S')
            }

        return Response({
            'detalle': f'Horarios del médico {medico.usuario.get_full_name()}',
            'estatus': status.HTTP_200_OK,
            'datos': {
                'medico': medico.id,
                'medico_nombre': medico.usuario.get_full_name(),
                'turnos': agrupado
            }
        })

    def create(self, request, *args, **kwargs):
        data = request.data
        medico_id = data.get('medico')
        turnos = data.get('turnos')

        if not medico_id or not turnos:
            return Response({                
                'detalle': 'Faltan campos requeridos: medico y turnos.',
                'estatus': status.HTTP_400_BAD_REQUEST,
                'datos': {}
            })
        
        try:
            medico = Medico.objects.get(pk=medico_id)
        except Medico.DoesNotExist:
            return Response({
                'detalle': 'Medico no encontrado.',
                'estatus': status.HTTP_400_BAD_REQUEST,
                'datos': {}
            })
        
        horarios_creados = []
        errores = []

        for descripcion, turno in turnos.items():
            dias = turno.get('dias', {})
            for dia_codigo, horario in dias.items():
                hora_inicio = horario.get('hora_inicio')
                hora_fin = horario.get('hora_fin')

                horario_obj = Horario(
                    medico = medico,
                    descripcion = descripcion,
                    dia = dia_codigo,
                    hora_inicio = hora_inicio,
                    hora_fin = hora_fin
                )

                try:
                    horario_obj.clean()
                    horario_obj.save()
                    horarios_creados.append(HorarioSerializer(horario_obj).data)
                except ValidationError as e:
                    errores.append({
                        'descripcion': descripcion,
                        'dia': dia_codigo,
                        'error': str(e)
                    })

        if errores:
            return Response({
                'detalle': 'Algunos horarios no se han podido crear.',
                'estatus': status.HTTP_207_MULTI_STATUS,
                'datos': {
                    'creados': horarios_creados,
                    'errores': errores
                }
            })
            
        return Response({
            'detalle': 'Horarios creados satisfactoriamente.',
            'estatus': status.HTTP_200_OK,
            'datos': horarios_creados
        })        

    def update(self, request, *args, **kwargs):
        data = request.data
        medico_id = data.get('medico')
        turnos = data.get('turnos')

        if not medico_id or not turnos:
            return Response({
                'detalle': 'Faltan campos requeridos: "medico" y "turnos"',
                'estatus': status.HTTP_400_BAD_REQUEST,
                'datos': {}
            })

        try:
            medico = Medico.objects.get(pk=medico_id)
        except Medico.DoesNotExist:
            return Response({
                'detalle': 'Médico no encontrado',
                'estatus': status.HTTP_404_NOT_FOUND,
                'datos': {}
            })

        # Eliminar horarios actuales
        Horario.objects.filter(medico=medico).delete()

        horarios_creados = []
        errores = []

        for descripcion, turno in turnos.items():
            dias = turno.get('dias', {})
            for dia_codigo, horario in dias.items():
                hora_inicio = horario.get('hora_inicio')
                hora_fin = horario.get('hora_fin')

                horario_obj = Horario(
                    medico=medico,
                    descripcion=descripcion,
                    dia=dia_codigo,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin
                )

                try:
                    horario_obj.clean()
                    horario_obj.save()
                    horarios_creados.append(HorarioSerializer(horario_obj).data)
                except ValidationError as e:
                    errores.append({
                        'descripcion': descripcion,
                        'dia': dia_codigo,
                        'error': str(e)
                    })

        if errores:
            return Response({
                'detalle': 'Algunos horarios no se pudieron actualizar',
                'estatus': status.HTTP_207_MULTI_STATUS,
                'datos': {
                    'actualizados': horarios_creados,
                    'errores': errores
                }
            })

        return Response({
            'detalle': 'Horarios actualizados correctamente',
            'estatus': status.HTTP_200_OK,
            'datos': horarios_creados
        })

    def destroy(self, request, *args, **kwargs):
        medico_id = kwargs.get('pk')

        try:
            medico = Medico.objects.get(pk=medico_id)
        except Medico.DoesNotExist:
            return Response({
                'detalle': 'Médico no encontrado',
                'estatus': status.HTTP_404_NOT_FOUND,
                'datos': {}
            })

        horarios = Horario.objects.filter(medico=medico)
        total = horarios.count()

        if total == 0:
            return Response({
                'detalle': 'El médico no tiene horarios asignados',
                'estatus': status.HTTP_204_NO_CONTENT,
                'datos': {}
            })

        horarios.delete()

        return Response({
            'detalle': f'Se eliminaron {total} horarios del médico {medico.usuario.get_full_name()}',
            'estatus': status.HTTP_200_OK,
            'datos': {}
        })
