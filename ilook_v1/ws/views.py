from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, Http404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from concurrent.futures import ThreadPoolExecutor
from core.models import *
from ws.serializers import *
from sesion.auth import TokenConVencimientoAutenticacion
from sesion.utils import respuesta_json
import pandas as pd


def custom_404_view(request, exception=None):
  """
  Manejador para respuestas 404
  """
  try:
    return JsonResponse({'detalle': 'Ruta no autorizada.', 'codigo': 404, 'datos': None,}, status=status.HTTP_404_NOT_FOUND)
  except Exception as e:
    print('Error', str(e))

def custom_500_view(request, exception=None):
  """
  Manejador para respuestas 500
  """
  try:
    return JsonResponse({'detalle': 'Ocurrio un error inesperado.', 'codigo': 500, 'datos': None,}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  except Exception as e:
    print('Error', str(e))

"""
Tablas Generales
Este mantenimiento de tabla es para una clave compuesta de dos campos.
FK:
"""
class Ilr001ListView(generics.ListAPIView):
  queryset = Ilr001.objects.all()
  serializer_class = Ilr001Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  # Filtros, ordenar y pagineo 
  filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
  filterset_fields = ['r001001', 'r001002'] # [tabla, item]

  # Busqueda
  search_fields = ['r001003'] # [descripcion]

  # Ordenamiento
  ordering_fiels = ['r001001', 'r001002', 'r001003'] # [tabla, item, descripcion]
  ordering = ['r001001', 'r001002']

  def get_queryset(self):
    user = self.request.user
    if not user.has_perm("core.view_ilr001"):
        raise PermissionDenied()
    return super().get_queryset()


class Ilr001CreateView(generics.CreateAPIView):
  queryset = Ilr001.objects.all()
  serializer_class = Ilr001Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def create(self, request, *args, **kwargs):
    try:
      # Validar usuario autorizado.
      lc_user = request.user
      if not lc_user:
        raise PermissionDenied()
      
      # Copiar la data e incluir campos "automáticos".
      lc_data = request.data.copy()
      lc_data['r001007'] = lc_user.username
      lc_data['r001008'] = timezone.now()

      # Validar existencia
      lc_tabla_id = lc_data.get('r001001')
      lc_item_id = lc_data.get('r001002')
      if Ilr001.objects.filter(r001001=lc_tabla_id, r001002=lc_item_id).exists():
        return respuesta_json('Registro ya existe.', status.HTTP_400_BAD_REQUEST)

      # Actualizar el modelo.
      lc_serializer = self.get_serializer(data=lc_data)
      if lc_serializer.is_valid():
        lc_instancia = lc_serializer.save()
        return respuesta_json('Registros creado correctamente.', status.HTTP_201_CREATED, datos=Ilr001Serializer(lc_instancia).data)
      
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)
    except Exception as e:
      print ('Error en Ilr001CreateView:', str(e))
      return respuesta_json('Ocurrio un error al insertar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


class Ilr001DetailView(generics.RetrieveAPIView):
  queryset = Ilr001.objects.all()
  serializer_class = Ilr001Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    user = self.request.user
    if not user.has_perm("core.view_ilr001"):
      raise PermissionDenied("Usuario no autorizado.")
    lc_tabla_id = self.kwargs.get('tabla_id')
    lc_item_id = self.kwargs.get('item_id')
    return get_object_or_404(Ilr001, r001001=lc_tabla_id, r001002=lc_item_id)
  
  def retrieve(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_serializer = self.get_serializer(lc_instancia)
      return respuesta_json('Detalle del registro', status.HTTP_200_OK, datos=lc_serializer.data)
    except Exception as e:
      print("Error en Ilr001DetailView: ", str(e))
      return respuesta_json('Error al leer el registro', status.HTTP_500_INTERNAL_SERVER_ERROR)


class Ilr001UpdateView(generics.UpdateAPIView):
  queryset = Ilr001.objects.all()
  serializer_class = Ilr001Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_user = self.request.user
    if not lc_user:
      raise PermissionDenied()
    lc_tabla_id = self.kwargs.get('tabla_id')
    lc_item_id = self.kwargs.get('item_id')
    return get_object_or_404(Ilr001, r001001=lc_tabla_id, r001002=lc_item_id)
  
  def update(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_data = request.data.copy()

      # Eliminar los campos claves.
      lc_data.pop('r001001', None)
      lc_data.pop('r001002', None)

      # ACtualizar campos "automaticos".
      lc_data['r001007'] = request.user.username
      lc_data['r001008'] = timezone.now()

      lc_serializer = self.get_serializer(lc_instancia, data=lc_data, partial=True)
      if lc_serializer.is_valid():
        lc_grabar = lc_serializer.save()
        return respuesta_json('Registro actualizador correctamente.', status.HTTP_200_OK, datos=Ilr001Serializer(lc_grabar).data)
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)

    except Exception as e:
      print ('Error en Ilr001UpdateView: ', str(e))
      return respuesta_json('Error al actualizar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


class Ilr001DeleteView(generics.DestroyAPIView):
  queryset = Ilr001.objects.all()
  serializer_class = Ilr001Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_user = self.request.user
    if not lc_user:
      raise PermissionDenied()
    lc_tabla_id = self.kwargs.get('tabla_id')
    lc_item_id = self.kwargs.get('item_id')
    return get_object_or_404(Ilr001, r001001=lc_tabla_id, r001002=lc_item_id)
  
  def destroy(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_instancia.delete()
      return respuesta_json('Registro eliminado correctamente.', status.HTTP_200_OK)
    except Exception as e:
      print('Error en Ilr001DeleteView: ', str(e))
      return respuesta_json('Error al eliminar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


"""
Monedas
FK: Ilr001
"""
class Ilm002ListView(generics.ListAPIView):
  queryset = Ilm002.objects.all()
  serializer_class = Ilm002Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  # Filtros, ordenar y pagineo 
  filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
  filter_set_fields = ['m002001', 'm002003']

  # Busqueda
  search_fields = ['m002002']

  # Ordenamiento
  ordering_fields = ['m002001', 'm002003', 'm002003']
  ordering = ['m002001']

  def get_queryset(self):
    user = self.request.user
    if not user.has_perm('core.view_ilm002'):
      raise PermissionDenied()
    return super().get_queryset()


class Ilm002CreateView(generics.CreateAPIView):
  queryset = Ilm002.objects.all()
  serializer_class = Ilm002Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  # sobrescribimos el create
  def create(self, request, *args, **kwargs):
    try:
      lc_user = request.user
      if not lc_user.has_perm('core.add_ilm002'):
        raise PermissionDenied()
      
      lc_data = request.data.copy()

      # Campos "automaticos"
      lc_data['m002012'] = lc_user.username
      lc_data['m002013'] = timezone.now()

      if Ilm002.objects.filter(m002001=lc_data.get('m002001')).exists():
        return respuesta_json('Registro ya existe.', status.HTTP_400_BAD_REQUEST)
      
      lc_serializer = self.get_serializer(data=lc_data)
      if lc_serializer.is_valid():
        lc_instancia = lc_serializer.save()
        return respuesta_json('Registro creado satisfactoriamente.', status.HTTP_201_CREATED, datos=Ilm002Serializer(lc_instancia).data)
      
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)
    
    except Exception as e:
      print('Error en Ilm002CreateView: ', str(e))
      return respuesta_json('Ocurrio un error al insertar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


class Ilm002DetailView(generics.RetrieveAPIView):
  queryset = Ilm002.objects.all()
  serializer_class = Ilm002Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    user = self.request.user
    if not user.has_perm("core.view_ilm002"):
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilm002, m002001=lc_codigo)
  
  def retrieve(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_serializer = self.get_serializer(lc_instancia)
      return respuesta_json('Detalle del registro.', status.HTTP_200_OK, datos=lc_serializer.data)
    except Http404:
      return respuesta_json('No existe el registro.', status.HTTP_404_NOT_FOUND)
    except Exception as e:
      print("Error en Ilm002DetailView: ", str(e))
      return respuesta_json('Error al leer el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


class Ilm002UpdateView(generics.UpdateAPIView):
  queryset = Ilm002.objects.all()
  serializer_class = Ilm002Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_user = self.request.user
    if not lc_user:
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilm002, m002001=lc_codigo)
  
  def update(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_data = request.data.copy()
      lc_user = request.user

      # Eliminar campos clave
      lc_data.pop('m002001', None)

      # Campos "automaticos"
      lc_data['m002012'] = lc_user.username
      lc_data['m002013'] = timezone.now()

      lc_serializer = self.get_serializer(lc_instancia, data=lc_data, partial=True)
      if lc_serializer.is_valid():
        lc_grabar = lc_serializer.save()
        return respuesta_json('Registro actualizado correctamente.', status.HTTP_200_OK, datos=Ilm002Serializer(lc_grabar).data)
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)

    except Http404:
      return respuesta_json('No existe el registro.', status.HTTP_404_NOT_FOUND)
    except Exception as e:
      print ('Error en Ilm002UpdateView: ', str(e))
      return respuesta_json('Error al actualizar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


class Ilm002DeleteView(generics.DestroyAPIView):
  queryset = Ilm002.objects.all()
  serializer_class = Ilm002Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_user = self.request.user
    if not lc_user:
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilm002, m002001=lc_codigo)
  
  def destroy(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_instancia.delete()
      return respuesta_json('Registro eliminado correctamente.', status.HTTP_200_OK)
    except Http404:
      return respuesta_json('No existe el registro.', status.HTTP_404_NOT_FOUND)
    except Exception as e:
      print('Error en Ilr002DeleteView: ', str(e))
      return respuesta_json('Error al eliminar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


"""
Paises
FK: Ilr001, Ilm002
"""
class Ilm003ListView(generics.ListAPIView):
  queryset = Ilm003.objects.all()
  serializer_class = Ilm003Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  # Filtros, ordenar y pagineo 
  filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
  filter_set_fields = ['m003001', 'm003003']

  # Busqueda
  search_fields = ['m003002']

  # Ordenamiento
  ordering_fields = ['m003001', 'm003003', 'm003003']
  ordering = ['m003001']

  def get_queryset(self):
    user = self.request.user
    if not user.has_perm('core.view_ilm003'):
      raise PermissionDenied()
    return super().get_queryset()


class Ilm003CreateView(generics.CreateAPIView):
  queryset = Ilm003.objects.all()
  serializer_class = Ilm003Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  # sobrescribimos el create
  def create(self, request, *args, **kwargs):
    try:
      lc_user = request.user
      if not lc_user.has_perm('core.add_ilm003'):
        raise PermissionDenied()
      
      lc_data = request.data.copy()

      # Campos "automaticos"
      lc_data['m003006'] = lc_user.username
      lc_data['m003007'] = timezone.now()

      if Ilm003.objects.filter(m003001=lc_data.get('m003001')).exists():
        return respuesta_json('Registro ya existe.', status.HTTP_400_BAD_REQUEST)
      
      lc_serializer = self.get_serializer(data=lc_data)
      if lc_serializer.is_valid():
        lc_instancia = lc_serializer.save()
        return respuesta_json('Registro creado satisfactoriamente.', status.HTTP_201_CREATED, datos=Ilm003Serializer(lc_instancia).data)
      
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)
    
    except Exception as e:
      print('Error en Ilm003CreateView: ', str(e))
      return respuesta_json('Ocurrio un error al insertar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


class Ilm003DetailView(generics.RetrieveAPIView):
  queryset = Ilm003.objects.all()
  serializer_class = Ilm003Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    user = self.request.user
    if not user.has_perm("core.view_ilm003"):
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilm003, m003001=lc_codigo)
  
  def retrieve(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_serializer = self.get_serializer(lc_instancia)
      return respuesta_json('Detalle del registro.', status.HTTP_200_OK, datos=lc_serializer.data)
    except Http404:
      return respuesta_json('No existe el registro.', status.HTTP_404_NOT_FOUND)
    except Exception as e:
      print("Error en Ilm003DetailView: ", str(e))
      return respuesta_json('Error al leer el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


class Ilm003UpdateView(generics.UpdateAPIView):
  queryset = Ilm003.objects.all()
  serializer_class = Ilm003Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_user = self.request.user
    if not lc_user:
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilm003, m003001=lc_codigo)
  
  def update(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_data = request.data.copy()
      lc_user = request.user
      print('datos: ', lc_data)

      # Eliminar campos clave
      lc_data.pop('m003001', None)

      # Campos "automaticos"
      lc_data['m003006'] = lc_user.username
      lc_data['m003007'] = timezone.now()

      lc_serializer = self.get_serializer(lc_instancia, data=lc_data, partial=True)
      if lc_serializer.is_valid():
        lc_grabar = lc_serializer.save()
        return respuesta_json('Registro actualizado correctamente.', status.HTTP_200_OK, datos=Ilm003Serializer(lc_grabar).data)
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)

    except Http404:
      return respuesta_json('No existe el registro.', status.HTTP_404_NOT_FOUND)
    except Exception as e:
      print ('Error en Ilm003UpdateView: ', str(e))
      return respuesta_json('Error al actualizar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


class Ilm003DeleteView(generics.DestroyAPIView):
  queryset = Ilm003.objects.all()
  serializer_class = Ilm003Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_user = self.request.user
    if not lc_user:
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilm003, m003001=lc_codigo)
  
  def destroy(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_instancia.delete()
      return respuesta_json('Registro eliminado correctamente.', status.HTTP_200_OK)
    except Http404:
      return respuesta_json('No existe el registro.', status.HTTP_404_NOT_FOUND)
    except Exception as e:
      print('Error en Ilr003DeleteView: ', str(e))
      return respuesta_json('Error al eliminar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


"""
Alerta
FK: Ilr001
"""
class Ilm004ListView(generics.ListAPIView):
  queryset = Ilm004.objects.all()
  serializer_class = Ilm004Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  # Filtros, ordenar y pagineo 
  filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
  filter_set_fields = ['m004001', 'm004003', 'm004004', 'm004006']

  # Busqueda
  search_fields = ['m004002']

  # Ordenamiento
  ordering_fields = ['m004001', 'm004003', 'm004003']
  ordering = ['m004001']

  def get_queryset(self):
    user = self.request.user
    if not user.has_perm('core.view_ilm004'):
      raise PermissionDenied()
    return super().get_queryset()


class Ilm004CreateView(generics.CreateAPIView):
  queryset = Ilm004.objects.all()
  serializer_class = Ilm004Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  # sobrescribimos el create
  def create(self, request, *args, **kwargs):
    try:
      lc_user = request.user
      if not lc_user.has_perm('core.add_ilm004'):
        raise PermissionDenied()
      
      lc_data = request.data.copy()

      # Campos "automaticos"
      lc_data['m004007'] = lc_user.username
      lc_data['m004008'] = timezone.now()

      if Ilm004.objects.filter(m004001=lc_data.get('m004001')).exists():
        return respuesta_json('Registro ya existe.', status.HTTP_400_BAD_REQUEST)
      
      lc_serializer = self.get_serializer(data=lc_data)
      if lc_serializer.is_valid():
        lc_instancia = lc_serializer.save()
        return respuesta_json('Registro creado satisfactoriamente.', status.HTTP_201_CREATED, datos=Ilm004Serializer(lc_instancia).data)
      
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)
    
    except Exception as e:
      print('Error en Ilm004CreateView: ', str(e))
      return respuesta_json('Ocurrio un error al insertar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


class Ilm004DetailView(generics.RetrieveAPIView):
  queryset = Ilm004.objects.all()
  serializer_class = Ilm004Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    user = self.request.user
    if not user.has_perm("core.view_ilm004"):
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilm004, m004001=lc_codigo)
  
  def retrieve(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_serializer = self.get_serializer(lc_instancia)
      return respuesta_json('Detalle del registro.', status.HTTP_200_OK, datos=lc_serializer.data)
    except Http404:
      return respuesta_json('No existe el registro.', status.HTTP_404_NOT_FOUND)
    except Exception as e:
      print("Error en Ilm003DetailView: ", str(e))
      return respuesta_json('Error al leer el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


class Ilm004UpdateView(generics.UpdateAPIView):
  queryset = Ilm004.objects.all()
  serializer_class = Ilm004Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_user = self.request.user
    if not lc_user:
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilm004, m004001=lc_codigo)
  
  def update(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_data = request.data.copy()
      lc_user = request.user

      # Eliminar campos clave
      lc_data.pop('m004001', None)

      # Campos "automaticos"
      lc_data['m004007'] = lc_user.username
      lc_data['m004008'] = timezone.now()

      lc_serializer = self.get_serializer(lc_instancia, data=lc_data, partial=True)
      if lc_serializer.is_valid():
        lc_grabar = lc_serializer.save()
        return respuesta_json('Registro actualizado correctamente.', status.HTTP_200_OK, datos=Ilm004Serializer(lc_grabar).data)
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)

    except Http404:
      return respuesta_json('No existe el registro.', status.HTTP_404_NOT_FOUND)
    except Exception as e:
      print ('Error en Ilm004UpdateView: ', str(e))
      return respuesta_json('Error al actualizar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


class Ilm004DeleteView(generics.DestroyAPIView):
  queryset = Ilm004.objects.all()
  serializer_class = Ilm004Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_user = self.request.user
    if not lc_user:
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilm004, m004001=lc_codigo)
  
  def destroy(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_instancia.delete()
      return respuesta_json('Registro eliminado correctamente.', status.HTTP_200_OK)
    except Http404:
      return respuesta_json('No existe el registro.', status.HTTP_404_NOT_FOUND)
    except Exception as e:
      print('Error en Ilr003DeleteView: ', str(e))
      return respuesta_json('Error al eliminar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestUpLoadView(APIView):
  parser_classes = [MultiPartParser]
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]
  queryset = Ilm004.objects.all()

  def post(self, request, format=None):
    try:
      lc_user = request.user
      if not lc_user.has_perm('core.add_ilm004'):
        return respuesta_json('Usuario no autorizado.', status.HTTP_403_FORBIDDEN)
        
      lc_archivo = request.FILES.get('archivo')
      if not lc_archivo:
        return respuesta_json('No se recibió ningún archivo.', status.HTTP_400_BAD_REQUEST)
        
      # Detectar que tipo de archivo es
      lc_extension = lc_archivo.name.split('.')[-1].lower()
      if lc_extension == 'csv':
        df = pd.read_csv(lc_archivo, dtype=str)
      elif lc_extension in ['xls', 'xlsx']:
        df = pd.read_excel(lc_archivo, dtype=str)
      else:
        return respuesta_json('Formato de archivo no soportado.', status.HTTP_406_NOT_ACCEPTABLE)
        
      resultados = {
        'procesados': 0,
        'exitosos': 0,
        'errores': []
      }

      def procesar_fila(fila):
        lc_datos = fila.to_dict()
        lc_datos['m004007'] = lc_user.username
        lc_serializer = Ilm004Serializer(data = lc_datos)
        if lc_serializer.is_valid():
          lc_serializer.save()
          resultados['exitosos'] += 1
        else:
          resultados['errores'].append({'fila': lc_datos, 'errores': lc_serializer.errors})

      with ThreadPoolExecutor(max_workers=10) as ejecutor:
        for _, fila in df.iterrows():
          resultados['procesados'] += 1
          ejecutor.submit(procesar_fila, fila)

      return respuesta_json('Carga por lotes finalizada.', status.HTTP_200_OK, datos=resultados)
      
    except Exception as e:
      print ('Error en Ilm004BatchUploadView: ', str(e))
      return respuesta_json('Error interno al procesar el archivo.', status.HTTP_500_INTERNAL_SERVER_ERROR)


"""
Reglas.
FK: Ilr001, Ilm004, Ilm006
"""
class Ilm006ListView(generics.ListAPIView):
  queryset = Ilm006.objects.all()
  serializer_class = Ilm006Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  # Filtros, ordenar y pagineo 
  filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
  filter_set_fields = ['m006001', 'm006004', 'm006031', 'm006039', 'm006043']

  # Busqueda
  search_fields = ['m006002']

  # Ordenamiento
  ordering_fields = ['m006001', 'm006004']
  ordering = ['m006001']

  def get_queryset(self):
    user = self.request.user
    if not user.has_perm('core.view_ilm006'):
      raise PermissionDenied()
    return super().get_queryset()


class Ilm006CreateView(generics.CreateAPIView):
  queryset = Ilm006.objects.all()
  serializer_class = Ilm006Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  # sobrescribimos el create
  def create(self, request, *args, **kwargs):
    try:
      lc_user = request.user
      if not lc_user.has_perm('core.add_ilm006'):
        raise PermissionDenied()
      
      lc_data = request.data.copy()

      # Campos "automáticos"
      lc_data['m006041'] = lc_user.username
      lc_data['m006042'] = timezone.now()

      if Ilm006.objects.filter(m006001=lc_data.get('m006001')).exists():
        return respuesta_json('Registro ya existe.', status.HTTP_400_BAD_REQUEST)
      
      lc_serializer = self.get_serializer(data=lc_data)
      if lc_serializer.is_valid():
        lc_instancia = lc_serializer.save()
        return respuesta_json('Registro creado satisfactoriamente.', status.HTTP_201_CREATED, datos=Ilm006Serializer(lc_instancia).data)
      
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)
    
    except Exception as e:
      print('Error en Ilm006CreateView: ', str(e))
      return respuesta_json('Ocurrio un error al insertar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


class Ilm006DetailView(generics.RetrieveAPIView):
  queryset = Ilm006.objects.all()
  serializer_class = Ilm006Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    user = self.request.user
    if not user.has_perm("core.view_ilm006"):
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilm006, m006001=lc_codigo)
  
  def retrieve(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_serializer = self.get_serializer(lc_instancia)
      return respuesta_json('Detalle del registro', status.HTTP_200_OK, datos=lc_serializer.data)
    except Exception as e:
      print("Error en Ilm006DetailView: ", str(e))
      return respuesta_json('Error al leer el registro', status.HTTP_500_INTERNAL_SERVER_ERROR)


class Ilm006UpdateView(generics.UpdateAPIView):
  queryset = Ilm006.objects.all()
  serializer_class = Ilm006Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_user = self.request.user
    if not lc_user:
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilm006, m006001=lc_codigo)
  
  def update(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_data = request.data.copy()

      # no permitir el campo "codigo"
      lc_data.pop('m006001', None)

      # Campos "automaticos"
      lc_data['m006041'] = request.user.username
      lc_data['m006042'] = timezone.now()

      lc_serializer = self.get_serializer(lc_instancia, data=lc_data, partial=True)
      if lc_serializer.is_valid():
        lc_grabar = lc_serializer.save()
        return respuesta_json('Registro actualizador correctamente.', status.HTTP_200_OK, datos=Ilm006Serializer(lc_grabar).data)
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)

    except Exception as e:
      print ('Error en Ilm006UpdateView: ', str(e))
      return respuesta_json('Error al actualizar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


class Ilm006DeleteView(generics.DestroyAPIView):
  queryset = Ilm006.objects.all()
  serializer_class = Ilm006Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_user = self.request.user
    if not lc_user:
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilm006, m006001=lc_codigo)
  
  def destroy(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_instancia.delete()
      return respuesta_json('Registro eliminado correctamente.', status.HTTP_200_OK)
    except Exception as e:
      print('Error en Ilr002DeleteView: ', str(e))
      return respuesta_json('Error al eliminar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


"""
Horarios laborales.
FK: Ilr001
"""
class Ilr002ListView(generics.ListAPIView):
  queryset = Ilr002.objects.all()
  serializer_class = Ilr002Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  # Filtros, ordenar y pagineo 
  filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
  filter_set_fields = ['r002001']

  # Busqueda
  search_fields = ['r002002']

  # Ordenamiento
  ordering_fields = ['r002001', 'r002002']
  ordering = ['r002001']

  def get_queryset(self):
    user = self.request.user
    if not user.has_perm('core.view_ilr002'):
      raise PermissionDenied()
    return super().get_queryset()


class Ilr002CreateView(generics.CreateAPIView):
  queryset = Ilr002.objects.all()
  serializer_class = Ilr002Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  # sobrescribimos el create
  def create(self, request, *args, **kwargs):
    try:
      lc_user = request.user
      if not lc_user.has_perm('core.add_ilr002'):
        raise PermissionDenied()
      
      lc_data = request.data.copy()

      if Ilr002.objects.filter(r002001=lc_data.get('r002001')).exists():
        return respuesta_json('Registro ya existe.', status.HTTP_400_BAD_REQUEST)
      
      lc_serializer = self.get_serializer(data=lc_data)
      if lc_serializer.is_valid():
        lc_instancia = lc_serializer.save()
        return respuesta_json('Registro creado satisfactoriamente.', status.HTTP_201_CREATED, datos=ILR002Serializer(lc_instancia).data)
      
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)
    
    except Exception as e:
      print('Error en Ilr002CreateView: ', str(e))
      return respuesta_json('Ocurrio un error al insertar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


class Ilr002DetailView(generics.RetrieveAPIView):
  queryset = Ilr002.objects.all()
  serializer_class = Ilr002Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    user = self.request.user
    if not user.has_perm("core.view_ilr002"):
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilr002, r002001=lc_codigo)
  
  def retrieve(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_serializer = self.get_serializer(lc_instancia)
      return respuesta_json('Detalle del registro', status.HTTP_200_OK, datos=lc_serializer.data)
    except Exception as e:
      print("Error en Ilr002DetailView: ", str(e))
      return respuesta_json('Error al leer el registro', status.HTTP_500_INTERNAL_SERVER_ERROR)


class Ilr002UpdateView(generics.UpdateAPIView):
  queryset = Ilr002.objects.all()
  serializer_class = Ilr002Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_user = self.request.user
    if not lc_user:
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilr002, r002001=lc_codigo)
  
  def update(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_data = request.data.copy()

      lc_serializer = self.get_serializer(lc_instancia, data=lc_data, partial=True)
      if lc_serializer.is_valid():
        lc_grabar = lc_serializer.save()
        return respuesta_json('Registro actualizador correctamente.', status.HTTP_200_OK, datos=Ilr002Serializer(lc_grabar).data)
      return respuesta_json('Error de validación.', status.HTTP_400_BAD_REQUEST, datos=lc_serializer.errors)

    except Exception as e:
      print ('Error en Ilr002UpdateView: ', str(e))
      return respuesta_json('Error al actualizar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


class Ilr002DeleteView(generics.DestroyAPIView):
  queryset = Ilr002.objects.all()
  serializer_class = Ilr002Serializer
  authentication_classes = [TokenConVencimientoAutenticacion]
  permission_classes = [IsAuthenticated, DjangoModelPermissions]

  def get_object(self):
    lc_user = self.request.user
    if not lc_user:
      raise PermissionDenied()
    lc_codigo = self.kwargs.get('codigo')
    return get_object_or_404(Ilr002, r002001=lc_codigo)
  
  def destroy(self, request, *args, **kwargs):
    try:
      lc_instancia = self.get_object()
      lc_instancia.delete()
      return respuesta_json('Registro eliminado correctamente.', status.HTTP_200_OK)
    except Exception as e:
      print('Error en Ilr002DeleteView: ', str(e))
      return respuesta_json('Error al eliminar el registro.', status.HTTP_500_INTERNAL_SERVER_ERROR)


