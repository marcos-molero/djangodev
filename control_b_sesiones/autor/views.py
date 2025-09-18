from rest_framework import viewsets, status
from utils.decorators import validar_token_y_permiso
from autor.models import Autor
from utils.respuesta_json import respuesta_json
from .serializers import AutorSerializer


# Create your views here.
class AutorViewSet(viewsets.ViewSet):

  @validar_token_y_permiso('view', Autor)
  def list(self, request):
    autores = Autor.objects.all()
    serializer = AutorSerializer(autores, many=True)
    return respuesta_json(
      detalle = 'Lista de Autores.',
      codigo = status.HTTP_200_OK,
      datos = serializer.data
    )
    # datos = [
    #   {
    #     'id': autor.id, 
    #     'nombre': autor.nombre, 
    #     'lugar_nacimiento': autor.lugar_nacimiento,
    #     'fecha_nacimiento': autor.fecha_nacimiento
    #   } 
    #   for autor in autores
    # ]
    # return respuesta_json(
    #   detalle = 'Lista de autores',
    #   codigo = 200,
    #   datos = datos
    # )
  
  @validar_token_y_permiso('add', Autor)
  def create(self, request):
    serializer = AutorSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return respuesta_json(detalle='Autor creado.', codigo=201, datos=serializer.data)
    return respuesta_json(detalle='Datos inválidos.', codigo=400, datos=serializer.errors)

  @validar_token_y_permiso('view', Autor)
  def retrieve(self, request, pk=None):
    try:
      autor = Autor.objects.get(pk=pk)
      serializer = AutorSerializer(autor)
      return respuesta_json(detalle='Autor obtenido.', codigo=200, datos=serializer.data)
    except Autor.DoesNotExist:
      return respuesta_json(detalle='Autor no encontrado.', codigo=404)

  @validar_token_y_permiso('change', Autor)
  def update(self, request, pk=None):
    try:
      autor = Autor.objects.get(pk=pk)
    except Autor.DoesNotExist:
      return respuesta_json(detalle='Autor no encontrado.', codigo=404)

    serializer = AutorSerializer(autor, data=request.data, partial=True)
    if serializer.is_valid():
      serializer.save()
      return respuesta_json(detalle='Autor actualizado.', codigo=200, datos=serializer.data)
    return respuesta_json(detalle='Datos inválidos.', codigo=400, datos=serializer.errors)

  @validar_token_y_permiso('delete', Autor)
  def destroy(self, request, pk=None):
    try:
      autor = Autor.objects.get(pk=pk)
      autor.delete()
      return respuesta_json(detalle='Autor eliminado.', codigo=200)
    except Autor.DoesNotExist:
      return respuesta_json(detalle='Autor no encontrado.', codigo=404)