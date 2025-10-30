from rest_framework import serializers
from core.models import Tmp_transaccion_LK1

class LoteLK1ResumenSerializer(serializers.Serializer):
  usuario = serializers.CharField(source = 'lk1usu')
  fecha = serializers.DateField()
  lote = serializers.CharField(source = 'lk1fid')
  estatus = serializers.CharField(source = 'lk1est')
  estatus_descripcion = serializers.SerializerMethodField()
  cantidad_registros = serializers.IntegerField(source = 'cantidad')

  def get_estatus_descripcion(self, obj):
    return Tmp_transaccion_LK1(lk1est=obj['lk1est']).get_lk1est_display()