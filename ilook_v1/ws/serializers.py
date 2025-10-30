from rest_framework import serializers
from core.models import *
from core.services.leer_Ilr001 import get_ilr001_descripcion

class Ilr001ListSerializer(serializers.ModelSerializer):
  """
  Tablas generales.
  """
  estatus_display = serializers.SerializerMethodField()

  class Meta:
    model = Ilr001
    fields = (
      'r001001',
      'r001003',
      'r001004',
      'estatus_display',
    )

  def get_estatus_display(self, obj):
    return obj.get_r001004_display().strip() if obj.r001004 else ''

class Ilr001Serializer(serializers.ModelSerializer):
  """
  Tablas generales.
  """
  estatus_display = serializers.SerializerMethodField()

  class Meta:
    model = Ilr001
    fields = (
      'r001001',
      'r001002',
      'r001003',
      'r001004',
      'estatus_display',
      'r001005',
      'r001006',
    )
    read_only_fields = ('r001007', 'r001008')

  def validate_r001003(self, value):
    if value.strip() == '':
      raise serializers.ValidationError("El valor de descripcion no puede ser blancos.")
    return value.strip()

  def validate_r001001(self, value):
    if value == 0:
      raise serializers.ValidationError("El valor de tabla_id no puede ser cero.")
    return value
  
  def get_estatus_display(self, obj):
    return obj.get_r001004_display().strip() if obj.r001004 else ''


class Ilr002Serializer(serializers.ModelSerializer):
  """
  Horarios
  """
  estatus_descripcion = serializers.SerializerMethodField()

  class Meta:
    model = Ilr002
    fields = ['r002001', 'r002002', 'r002003', 'r002004', 'r002005', 'estatus_descripcion']

  def validate(self, data):
    lc_inicio = data.get('r002003')
    lc_fin = data.get('r002004')
    if lc_inicio and lc_fin and lc_fin < lc_inicio:
      raise serializers.ValidationError('Hora cierre no puede ser menor.')
    return data

  def validate_r002005(self, value):
    if not Ilr001.objects.filter(r001001=8, r001002=value).exists():
        raise serializers.ValidationError('Estatus invalido.')
    return value   
  
  def get_estatus_descripcion(self, obj):
    try:
      lc_estatus = Ilr001.objects.filter(r001001=8, r001002=obj.r002005).first()
      return lc_estatus.r001003 if lc_estatus else None
    except Exception:
      return None
    

class Ilm002Serializer(serializers.ModelSerializer):
  """
  Monedas
  """
  estatus_descripcion = serializers.SerializerMethodField()

  class Meta:
    model = Ilm002
    fields = '__all__'

  def validate_m002011(self, value):
    if not Ilr001.objects.filter(r001001=8, r001002=value).exists():
        raise serializers.ValidationError('Estatus invalido.')
    return value
  
  def get_estatus_descripcion(self, obj):
    try:
      lc_estatus = Ilr001.objects.filter(r001001=8, r001002=obj.m002011).first()
      return lc_estatus.r001003 if lc_estatus else None
    except Exception:
      return None


class Ilm003Serializer(serializers.ModelSerializer):
  """
  Paises
  """
  estatus_descripcion = serializers.SerializerMethodField()
  moneda_descripcion =  serializers.SerializerMethodField()

  class Meta:
    model = Ilm003
    fields = '__all__'

  def validate_m003005(self, value):
    if not Ilr001.objects.filter(r001001=8, r001002=value).exists():
        raise serializers.ValidationError('Estatus invalido.')
    return value
  
  def validate_m003004(self, value):
    if not Ilm002.objects.filter(m002001=value).exists():
      raise serializers.ValidationError('Moneda inválida.')
    return value
  
  def get_estatus_descripcion(self, obj):
    try:
      lc_estatus = Ilr001.objects.filter(r001001=8, r001002=obj.m003005).first()
      return lc_estatus.r001003 if lc_estatus else None
    except Exception:
      return None

  def get_moneda_descripcion(self, obj):
    try:
      lc_moneda = Ilm002.objects.filter(m002001=obj.m003004).first()
      return lc_moneda.m002002 if lc_moneda else None
    except Exception:
      return None


class Ilm004Serializer(serializers.ModelSerializer):
  """
  Serializer para el modelo Ilm004 (Alertas). 
  Incluye validaciones contra Ilr001 y descripciones extendidas.
  
  FK: Tablas(Ilr001)
  """
  estatus_descripcion = serializers.SerializerMethodField()
  gravedad_descripcion = serializers.SerializerMethodField()
  accion_descripcion = serializers.SerializerMethodField()
  clase_descripcion = serializers.SerializerMethodField()

  class Meta:
    model = Ilm004
    fields = [
      'm004001', 
      'm004002', 
      'm004003', 'gravedad_descripcion',
      'm004004', 'accion_descripcion',
      'm004005', 'estatus_descripcion',
      'm004006', 'clase_descripcion',
      ]
    read_only_fields = ['m004007', 'm004008']

  # Gravedad
  def validate_m004003(self, value):
    value = value.strip().upper()
    if not Ilr001.objects.filter(r001001=6, r001002=value).exists():
        raise serializers.ValidationError('Gravedad invalido.')
    return value

  # Accion
  def validate_m004004(self, value):
    value = value.strip().upper()
    if not Ilr001.objects.filter(r001001=7, r001002=value).exists():
        raise serializers.ValidationError('Acción invalido.')
    return value

  # Clase
  def validate_m004006(self, value):
    value = value.strip().upper()
    if not Ilr001.objects.filter(r001001=19, r001002=value).exists():
        raise serializers.ValidationError('Clase invalido.')
    return value

  def get_gravedad_descripcion(self, obj):
    return obj.get_gravedad_display()

  def get_accion_descripcion(self, obj):
    return obj.get_accion_display()

  def get_estatus_descripcion(self, obj):
    return obj.get_estatus_catalogo_display()

  def get_clase_descripcion(self, obj):
    return obj.get_clase_display()

  # Limpiar campos CHAR.
  def to_representation(self, instance):
    data = super().to_representation(instance)
    data['m004002'] = data['m004002'].strip() if data.get('m004002') else None
    return data


class Ilm006Serializer(serializers.ModelSerializer):
  """
  Reglas
  """
  estatus_descripcion = serializers.SerializerMethodField()
  codigo_resp_automatica_descripcion = serializers.SerializerMethodField()
  codigo_alerta_descripcion = serializers.SerializerMethodField()
  nivel_riesgo_descripcion = serializers.SerializerMethodField()
  tarjeta_presente_descripcion = serializers.SerializerMethodField()
  tipo_operacion_contable_descripcion = serializers.SerializerMethodField()
  
  class Meta:
    model = Ilm006
    fields = '__all__'

  def validar_lapso(self, data):
    lc_lapso = data.get('m006028')
    lc_unidad_lapso = data.get('m006029')
    lc_cant_limite_trx = data.get('m006033')
    lc_monto_limite_trx = data.get('m006035')
    lc_acum_limite = data.get('m006037')

    if lc_lapso:

      if not lc_unidad_lapso:
        raise serializers.ValidationError({'m006028': 'Debe indicar la unidad del lapso de tiempo.'})

      condiciones = [
        (lc_cant_limite_trx > 0 and lc_monto_limite_trx == 0 and lc_acum_limite == 0),
        (lc_monto_limite_trx > 0 and lc_cant_limite_trx == 0 and lc_acum_limite == 0),
        (lc_acum_limite > 0 and lc_monto_limite_trx == 0 and lc_cant_limite_trx == 0),
      ]

    if not any(condiciones):
      raise serializers.ValidationError({'m006028': 'Si especifica Lapso de tiempo, debe indicar solo una de las condiciones.'})

    return data
  
  def validar_rango_horas(self, data):
    lc_desde = data.get('m006025')
    lc_hasta = data.get('m006026')
    if lc_desde and lc_hasta:
      if lc_hasta < lc_desde:
        raise serializers.ValidationError({'m006025': 'La hora desde no puede ser mayor que la hora hasta.'})

  def validate(self, data):
    self.validar_lapso(data)
    self.validar_rango_horas(data)
    return data

  def validate_m006031(self, value):
    if not Ilr001.objects.filter(r001001=17, r001002=value).exists():
        raise serializers.ValidationError('Código de respuesta inválido.')
    return value
  
  def validate_m006039(self, value):
    if not Ilm004.objects.filter(m004001=value).exists():
        raise serializers.ValidationError('Código de alerta inválido.')
    return value

  def validate_m006040(self, value):
    if not Ilr001.objects.filter(r001001=8, r001002=value).exists():
        raise serializers.ValidationError('Estatus invalido.')
    return value

  def validate_m006044(self, value):
    if not Ilr001.objects.filter(r001001=21, r001002=value).exists():
        raise serializers.ValidationError('Nivel de riesgo invalido.')
    return value

  def validate_m006045(self, value):
    if not Ilr001.objects.filter(r001001=22, r001002=value).exists():
        raise serializers.ValidationError('Tarjeta Presente invalido.')
    return value

  def validate_m006046(self, value):
    if not Ilr001.objects.filter(r001001=20, r001002=value).exists():
        raise serializers.ValidationError('POS Country invalido.')
    return value

  def validate_m006048(self, value):
    if not Ilr001.objects.filter(r001001=23, r001002=value).exists():
        raise serializers.ValidationError('Tipo de Operación invalido.')
    return value

  # def validate_m006049(self, value):
  #   if not Ilm0027.objects.filter(m027001=value).exists():
  #       raise serializers.ValidationError('Código de transacción WEB invalido.')
  #   return value

  def get_estatus_descripcion(self, obj):
    try:
      lc_estatus = Ilr001.objects.filter(r001001=8, r001002=obj.m004005).first()
      return lc_estatus.r001003 if lc_estatus else None
    except Exception:
      return None

  def get_codigo_resp_automatica_descripcion(self, obj):
    try:
      lc_tabla = Ilr001.objects.filter(r001001=17, r001002=obj.m006031).first()
      return lc_tabla.r001003 if lc_tabla else None
    except Exception:
      return None

  def get_codigo_alerta_descripcion(self, obj):
    try:
      lc_tabla = Ilm004.objects.filter(m004001=obj.m006039).first()
      return lc_tabla.m004002 if lc_tabla else None
    except Exception:
      return None

  def get_nivel_riesgo_descripcion(self, obj):
    try:
      lc_tabla = Ilr001.objects.filter(r001001=21, r001002=obj.m006044).first()
      return lc_tabla.r001003 if lc_tabla else None
    except Exception:
      return None

  def get_tarjeta_presente_descripcion(self, obj):
    try:
      lc_tabla = Ilr001.objects.filter(r001001=22, r001002=obj.m006045).first()
      return lc_tabla.r001003 if lc_tabla else None
    except Exception:
      return None

  def get_tipo_operacion_contable_descripcion(self, obj):
    try:
      lc_tabla = Ilr001.objects.filter(r001001=23, r001002=obj.m006048).first()
      return lc_tabla.r001003 if lc_tabla else None
    except Exception:
      return None


class Ilm027Serializer(serializers.ModelSerializer):
  """
  Transacciones con sensibilidad de riesgo
  FK:
  """
  class Meta:
    model = Ilm027
    exclude = ['pk']


class Ilh003Serializer(serializers.ModelSerializer):
  """
  Historico de alertas
  FK: Ilr001, Ilm004
  """
  class Meta:
    model = Ilh003
    fields = '__all__'


class Ilm016Serializer(serializers.ModelSerializer):
  """
  Paises para validación de Reglas 

  """
  pais_display = serializers.SerializerMethodField()

  class Meta:
    model = Ilm016
    fields = (
      'm016001',
      'm016003',
      'pais_display',
      'm016004',
    )
    read_only_fields = ['m016005', 'm016006',]

  def get_pais_display(self, obj):
    return get_ilr001_descripcion(3, obj.m016003).strip() if obj.m016003 else ''
  
  def validate_m016003(self, value):
    if not get_ilr001_descripcion(3, value):
      raise serializers.ValidationError("Codigo de pais no valido según catalogo ILR001.")
    return value

  def validate(self, data):
    regla = data.get('m016001')
    codigo_pais = data.get('m016003')

    if Ilm016.objects.filter(m016001 = regla, m016003 = codigo_pais).exists():
      raise serializers.ValidationError("El país ya está registrado para la regla.")
    return data
