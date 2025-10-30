from django_filters import rest_framework as filters
from core.models import Ilr001


class Ilr001Filter(filters.FilterSet):
  tabla = filters.NumberFilter(field_name='r001001')
  codigo = filters.CharFilter(field_name='r001002')

  class Meta:
    model = Ilr001
    fields = ['tabla', 'codigo']

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
