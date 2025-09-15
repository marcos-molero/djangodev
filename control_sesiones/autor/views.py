from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from .models import Autor, EstiloLiterario
from .serializers import AutorSerializer, EstiloLiterarioSerializer

class AutorViewSet(viewsets.ModelViewSet):
  queryset = Autor.objects.all()
  serializer_class = AutorSerializer
  permission_classes = [DjangoModelPermissions]

  # Establecer los paquetes de django, motor, busqueda y ordenamiento
  filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
  # establecer los campos para busqueda MATCH por igual.
  filterset_fields = ['nacionalidad', 'fecha_nacimiento']
  # Establecer los campos para busqueda LIKE parcial.
  # O sea aca se utiliza la palabra "search=" para buscar en estos campos.
  search_fields = ['nombre', 'apellido', 'biografia']
  # Finalmente los campos para ordenar. Creo que lo hace con el request. 
  # o sea ya manda los registros ordenados 
  ordering_fields = ['apellido', 'nombre', 'fecha_nacimiento']


class EstiloLiterarioViewSet(viewsets.ModelViewSet):
  queryset = EstiloLiterario.objects.all()
  serializer_class = EstiloLiterarioSerializer
  permission_classes = [DjangoModelPermissions]

  filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
  search_fields = ['nombre']
