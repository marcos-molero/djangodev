from django.db import models
from django.conf import settings
from django.forms import ValidationError
from core.services.validadores.lk1 import validar_transaccion_lk1
from django.core.exceptions import ValidationError
from .services.leer_Ilr001 import get_ilr001_descripcion


"""
Tuplas de selección simple
"""
OPCIONES_SI_NO = [
  ('S', 'Si'),
	('N', 'No')
]
OPCIONES_CANAL_SELECCIONADO = [
  ('  ', 'No validar'),
  ('RR', 'Operaciones financieras'),
  ('00', 'Canales')
]
OPCIONES_ELEMENTO_SELECCIONADO = [
  (' ', 'No validar'),
  ('E', 'Modo entrada libre'),
  ('L', 'Listar')
]
OPCIONES_LAPSO_TIEMPO = [
  ('S', 'Segundos'),
  ('M', 'Minutos'),
  ('H', 'Horas')
]
OPCIONES_TIPO_PERSONA = [
  (' ', 'No validar'),
  ('N', 'Natural'),
  ('J', 'Juridico'),
  ('G', 'Gobierno')
]
OPCIONES_FERIADO = [
  ('F', 'Feriado'),
  ('H', 'Habil'),
  ('A', 'Ambos'),
]
OPCIONES_TIPO_ASIENTO = [
	('D', 'DEBITO'),
	('C', 'CREDITO')
]
OPCIONES_NACIONALIDAD = [
	('N', 'Nacional'),
	('E', 'Extranjero'),
]
OPCIONES_ESTATUS_TABLA = [
	('0', 'Activo'),
	('9', 'Inactivo'),
]
OPCIONES_TIPO_DOCUMENTO = [
   ('V', 'Cedula'),
   ('P', 'Pasaporte'),
   ('R', 'RIF'),
]
OPCIONES_ESTATUS_PROCESO = [
   ('0', 'Pendiente por procesar'),
   ('1', 'En proceso'),
   ('2', 'Error'),
   ('4', 'Con alerta'),
   ('9', 'Procesado'),
]


class Ilr001(models.Model):
	"""
	Tablas generales del sistema
    
	FK:
	"""
	pk = models.CompositePrimaryKey('r001001', 'r001002')
	r001001 = models.SmallIntegerField(verbose_name='Tabla')
	r001002 = models.CharField(max_length=15, verbose_name='Item', blank=True, null=False)
	r001003 = models.CharField(max_length=150, verbose_name='Descripción', blank=True, null=False)
	r001004 = models.CharField(max_length=1, verbose_name='Estatus', choices=OPCIONES_ESTATUS_TABLA)
	r001005 = models.CharField(max_length=50, verbose_name='Filler ALF', blank=True)
	r001006 = models.DecimalField(max_digits=15, decimal_places=6, verbose_name='Filler NUM')
	r001007 = models.CharField(max_length=10, verbose_name='Usuario')
	r001008 = models.DateTimeField(verbose_name='Fecha Actualización', auto_now=True)

	class Meta:
		managed = False
		db_table = 'ilr001'
		db_table_comment = 'iLook - Tablas Generales'
		verbose_name = 'Tabla'
		verbose_name_plural = 'Tablas'
  
	def __str__(self):
		return f'{self.r001001}-{self.r001002}: {self.r001003}'


class Ilr002(models.Model):
    """
    Horarios de atención al publico

    FK:
    """
    r002001 = models.SmallIntegerField(primary_key=True, verbose_name='Código')
    r002002 = models.CharField(max_length=30, verbose_name='Descripción')
    r002003 = models.TimeField(verbose_name='Inicio')
    r002004 = models.TimeField(verbose_name='Fin')
    r002005 = models.CharField(max_length=1, verbose_name='Estatus')

    class Meta:
        managed = False
        db_table = 'ilr002'
        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios'


class Ilm002(models.Model):
  """
  Tabla de monedas.

  FK: Ilr001
  """
  m002001 = models.CharField(max_length=15, primary_key=True, verbose_name='Código')
  m002002 = models.CharField(max_length=40, verbose_name='Descripción')
  m002003 = models.CharField(max_length=3, verbose_name='ISO')
  m002004 = models.CharField(max_length=15, verbose_name='Moneda contravalor', blank=True)
  m002005 = models.DecimalField(max_digits=15, decimal_places=6, verbose_name='Tasa actual')
  m002006 = models.DecimalField(max_digits=15, decimal_places=6, verbose_name='Tasa anterior')
  m002007 = models.DecimalField(max_digits=15, decimal_places=6, verbose_name='Tasa promedio')
  m002008 = models.DecimalField(max_digits=15, decimal_places=6, verbose_name='Tasa generica')
  m002009 = models.DecimalField(max_digits=15, decimal_places=6, verbose_name='Tasa generica anterior')
  m002010 = models.DecimalField(max_digits=15, decimal_places=6, verbose_name='Tasa generica promedio')
  m002011 = models.CharField(max_length=1, verbose_name='Estatus', choices=OPCIONES_ESTATUS_TABLA)
  m002012 = models.CharField(max_length=10, verbose_name='Usuario')
  m002013 = models.DateTimeField(auto_now=True, verbose_name='Fecha actualización')

  class Meta:
    managed = False
    db_table = 'ilm002'
    db_table_comment = 'Tabla de monedas'
    verbose_name = 'Moneda'
    verbose_name_plural = 'Monedas'

  def clean(self):
    if not Ilr001.objects.filter(r001001=3, r001002=self.m002003).exists():
      raise ValidationError(f'El codigo de pais ISO {self.m002003} no es valido.')
    
  def get_Ilr001(self):
    return Ilr001.objects.filter(r001001=3, r001002=self.m002003).first()
  
  def display_moneda_catalogo(self):
    ilr = self.get_Ilr001()
    return ilr.r001005 if ilr else 'No registrado.'
  

class Ilm003(models.Model):
    """
    Paises
    FK: Ilr001
    """
    m003001 = models.CharField(max_length=3, primary_key=True, verbose_name='Codigo')
    m003002 = models.CharField(max_length=40, verbose_name='Descripción')
    m003003 = models.CharField(max_length=2, verbose_name='Código Alfabetico ISO')
    m003004 = models.CharField(max_length=15, verbose_name='Moneda Oficial')
    m003005 = models.CharField(max_length=1, verbose_name='Estatus')
    m003006 = models.CharField(max_length=10, verbose_name='Usuario')
    m003007 = models.DateTimeField(auto_now=True, verbose_name='Fecha')

    class Meta:
        managed = False
        db_table = 'ilm003'
        db_table_comment = 'iLook - Paises'
        verbose_name = 'Pais'
        verbose_name_plural = 'Paises'


class Ilm004(models.Model):
  """
  Maestro de alertas, definidas.

  FK: Ilr001
  """
  m004001 = models.CharField(max_length=10, primary_key=True, verbose_name='Código')
  m004002 = models.CharField(max_length=80, verbose_name='Descripción')
  m004003 = models.CharField(max_length=2, verbose_name='Gravedad')
  m004004 = models.CharField(max_length=2, verbose_name='Acción')
  m004005 = models.CharField(max_length=1, verbose_name='Estatus', choices=OPCIONES_ESTATUS_TABLA)
  m004006 = models.CharField(max_length=1, verbose_name='Clase')
  m004007 = models.CharField(max_length=10, verbose_name='Usuario')
  m004008 = models.DateTimeField(auto_now=True, verbose_name='fecha')

  class Meta:
    managed = False
    db_table = 'ilm004'
    db_table_comment = 'iLook - Alertas'
    verbose_name = 'Alerta'
    verbose_name_plural = 'Alertas'

  def get_ilr001(self, tabla, codigo):
    lc_valor = Ilr001.objects.filter(r001001=tabla, r001002=codigo, r001004='0').values_list('r001003', flat=True).first()
    return lc_valor.strip() if lc_valor else None

  def get_gravedad_display(self):
    return self.get_ilr001(6, self.m004003)
  def get_accion_display(self):
    return self.get_ilr001(7, self.m004004)
  def get_estatus_catalogo_display(self):
    lc_valor = self.get_m004005_display()
    return lc_valor.strip() if lc_valor else None
  def get_clase_display(self):
    return self.get_ilr001(19, self.m004006)

  def clean(self):
    errores = []
    if not Ilr001.objects.filter(r001001=6, r001002=self.m004003, r001004='0').exists():
      errores.append("Gravedad inválida o inactiva.")
    if not Ilr001.objects.filter(r001001=7, r001002=self.m004004, r001004='0').exists():
      errores.append("Acción inválida o inactiva.")
    if not Ilr001.objects.filter(r001001=19, r001002=self.m004006, r001004='0').exists():
      errores.append("Clase inválida o inactiva.")
    if errores:
      raise ValidationError(errores)


class Ilm006(models.Model):
    """
    Modelo: Reglas de usuario

    Permitir que usuarios definan reglas dinámicas para evaluar transacciones financieras. 
    Si una transacción cumple con los criterios de una regla, se genera una alerta correspondiente.
        
    FK: Ilr001, Ilm004
    """
    # Numero de relación
    # Identificador unico para cada regla de usuario.
    m006001 = models.DecimalField(max_digits=4, decimal_places=0, primary_key=True, verbose_name='Número')
    # Descripción
    # Detalle del concepto de la regla de usuario.
    m006002 = models.CharField(max_length=100, verbose_name='Descripción')
    # Prioridad
    # No utilizado por el momento
    m006003 = models.DecimalField(max_digits=2, decimal_places=0, verbose_name='Prioridad')
    # Origen
    # Identifica el ambito de donde viene una transacción a evaluar en especifico.
    m006004 = models.CharField(max_length=2, verbose_name='Origen', blank=True, choices=OPCIONES_CANAL_SELECCIONADO)
    # País
    # Identifica la zona de verificación de la transacción.
    # L = Ilr001(3)
    m006005 = models.CharField(max_length=1, verbose_name='País', blank=True, choices=OPCIONES_ELEMENTO_SELECCIONADO)
    # Categoria comercio
    # Identifica el tipo de comercio
    # L = Ilr001(12)
    m006007 = models.CharField(max_length=1, verbose_name='Categoria Comercio', blank=True, choices=OPCIONES_ELEMENTO_SELECCIONADO)
    # Instrumento
    # Forma de pago o instrumento financiero de la transacción.
    # E
    m006009 = models.CharField(max_length=1, verbose_name='Instrumento', blank=True)
    # BIN
    # Numero de cuenta del instrumento.
    # L = Ilr001(16)
    m006011 = models.CharField(max_length=1, verbose_name='BIN', blank=True, choices=OPCIONES_ELEMENTO_SELECCIONADO)
    # Canal
    # Indentifica el canal por el cual llega la transacción.
    # L = Ilr001(1)
    m006013 = models.CharField(max_length=1, verbose_name='Canal', blank=True, choices=OPCIONES_ELEMENTO_SELECCIONADO)
    # Terminal
    # Identifica el dispositivo 
    # E
    m006015 = models.CharField(max_length=1, verbose_name='Terminal', blank=True)
    # POS Entry mode
    # Información sobre el cobro/merchant/dispositivo/tarjeta
    # L = Ilr001(15)
    m006017 = models.CharField(max_length=1, verbose_name='POS Entry mode', blank=True, choices=OPCIONES_ELEMENTO_SELECCIONADO)
    # Alerta
    # No utilizado
    m006019 = models.CharField(max_length=1, verbose_name='Alerta', blank=True, choices=OPCIONES_ELEMENTO_SELECCIONADO)
    # Código de transaccion
    # Identifica la transaccion ISO 
    # L = Ilr001(14)
    m006021 = models.CharField(max_length=1, verbose_name='Código Transacción', blank=True, choices=OPCIONES_ELEMENTO_SELECCIONADO)
    # Tipo de persona
    # Identifica el tipo de persona titular del instrumento.
    m006023 = models.CharField(max_length=2, verbose_name='Tipo de Persona', blank=True, choices=OPCIONES_TIPO_PERSONA)
    # Hora desde
    # Periodo de tiempo a evaluar la transacción DESDE.
    m006025 = models.TimeField(verbose_name='Hora desde', blank=True, null=True)
    # Hora hasta
    # Periodo de tiempo a evaluar la transacción HASTA.
    m006026 = models.TimeField(verbose_name='Hora hasta', blank=True, null=True)
    # Lapso
    # Unidad de duración para la evaluaciuón de la transación
    m006028 = models.DecimalField(max_digits=3, decimal_places=0, verbose_name='Lapso')
    # Unidad de lapso
    # Unidad de tiempo a procesar.
    m006029 = models.CharField(max_length=1, verbose_name='Unidad del lapso', choices=OPCIONES_LAPSO_TIEMPO)
    # Codigo respuesta automática
    # Identifica el codigo para la respuesta del evento.
    # FK: Ilr001(17)
    m006031 = models.CharField(max_length=4, verbose_name='Codigo respuesta automática')
    # Limite de transacciones
    # Identifica limite para las transacciones permitidas en el lapso establecido.
    m006033 = models.DecimalField(max_digits=9, decimal_places=0, verbose_name='Limite de transacciones')
    # Monto limite por transaccion
    # Estables limite de monto para la transacción.
    # Evaluado por mayor/igual >=
    m006035 = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True, verbose_name='Monto limite por transacción')
    # Monto limite acumulado
    # Estables limite de monto para la transacción con acumulado por lapso establecido.
    # Evaluado por mayor/igual >=
    m006037 = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True, verbose_name='Monto limite acumulado')
    # Codigo de la alerta
    # Alerta a emitir si se cumple la regla.
    # FK: Ilm004
    m006039 = models.CharField(max_length=10, verbose_name='Código de la alerta')
    # Estatus
    # Estatsu del registro
    # FK: Ilr001(8)
    m006040 = models.CharField(max_length=1, verbose_name='Estatus')
    # Usuario ultima actualizacion
    # Campo automático, se extrae del request.
    m006041 = models.CharField(max_length=10, verbose_name='Usuario')
    # Fecha ultima actualizacion
    # Campo automático.
    m006042 = models.DateTimeField(verbose_name='Fecha')
    # LK1MID - DE42 MERCHANT ID
    # Codigo del comercio 
    # E
    m006043 = models.CharField(max_length=1, verbose_name='DE42', choices=OPCIONES_ELEMENTO_SELECCIONADO)
    # LK1NRI - DE48s42 NIV RIESGO
    # Este es el nivel de riesgo del comercio
    # FK: Ilr001(21)
    m006044 = models.CharField(max_length=3, verbose_name='DE48S42')
    # LK1PRE - DE61s4 TARJ PRESENT
    # Identifica si el tarjeta-habiente estubo presente en la transacción.
    # FK: Ilr001(22)
    m006045 = models.DecimalField(max_digits=4, decimal_places=0, verbose_name='DE61S4')
    # LK1PAP - DE61s13 POS COUNTRY
    # No se utiliza por el momento
    # L = Ilr001(20)
    m006046 = models.CharField(max_length=1, blank=True, verbose_name='DE61S13')
    # Puntos sensibiliad de riesgo
    # Valor que indentifica si el riesgo es mas susceptible de implicar riesgos
    # E
    m006047 = models.DecimalField(max_digits=3, decimal_places=0, verbose_name='Puntos sensibiliad de riesgo')
    # Tipo operación contable
    # Identifica la operacion financiera a evaluar
    # FK: Ilr001(23)
    m006048 = models.CharField(max_length=6, verbose_name='Tipo operación contable')
    # Código transacción Web
    # Identifica las operaciones web a evaluar.
    # L = Ilm027
    m006049 = models.CharField(max_length=1, verbose_name='Código transacción Web', choices=OPCIONES_ELEMENTO_SELECCIONADO)
    # Feriado
    # Idenfica si la transacción se da en un dia habil o feriado.
    m006050 = models.CharField(max_length=1, verbose_name='Feriado', choices=OPCIONES_FERIADO)
    # Validación primera transacción
    # Se verifica si es la primera transaccion registrada
    m006051 = models.CharField(max_length=1, verbose_name='Primera Transacción', choices=OPCIONES_SI_NO)

    class Meta:
        managed = False
        db_table = 'ilm006'
        verbose_name='Regla'
        verbose_name_plural='Reglas'


class Ilm027(models.Model):
    """
    Transacciones con sensibilidad de riesgo
    FK:
    """
    pk = models.CompositePrimaryKey('m027001', 'm027002')
    m027001 = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='Código')
    m027002 = models.DecimalField(max_digits=3, decimal_places=0, verbose_name='Secuencia')
    m027003 = models.CharField(max_length=150, verbose_name='Descripción')
    m027004 = models.DecimalField(max_digits=3, decimal_places=0, verbose_name='Sensibilidad del riesgo')
    m027005 = models.CharField(max_length=1, verbose_name='Aprobado o rechazado')
    m027006 = models.CharField(max_length=1, verbose_name='Estatus')
    m027007 = models.CharField(max_length=10, verbose_name='Usuario')
    m027008 = models.DateTimeField(verbose_name='Fecha', auto_now=True)

    class Meta:
        managed = False
        db_table = 'ilm027'
        verbose_name = 'TransaccionConSensibilidad'
        verbose_name_plural = 'TransaccionesConSensibilidad'


class Ilh003(models.Model):
    """
    Modelo: Ilh003

    Este modelo almacena el resultado del analisis del proceso de riesgos.

    Métodos:
        - is_expired(): Retorna True si el token ha vencido según el tiempo definido en settings.TOKEN_VENCE_SEG.
        - __str__(): Representación textual del token.

    Uso típico:
        Se utiliza para almacenar resultado del analisis de registros de transacciones.
    """
    # Id unico sistema iLook
    h003001 = models.DecimalField(max_digits=21, decimal_places=0, verbose_name='Código iLook')
    # Canal
    # FK: Ilr001(1)
    h003002 = models.CharField(max_length=15, verbose_name='Canal')
    # Moneda
    # FK: Ilm002.m002001
    h003003 = models.CharField(max_length=15, verbose_name='Moneda')
    # Año de ¿proceso?
    # Campo automático
    h003004 = models.SmallIntegerField(verbose_name='Año')
    # Mes de ¿proceso?
    # Campo automático
    h003005 = models.SmallIntegerField(verbose_name='Mes')
    # Día de ¿proceso?
    # Campo automático
    h003006 = models.SmallIntegerField(verbose_name='Dia')
    # Hora de ¿proceso?
    # Campo automático
    h003007 = models.TimeField(verbose_name='Hora')
    # Codigo de alerta
    # FK: Ilm004.m004001
    h003008 = models.CharField(max_length=10, verbose_name='Alerta')
    # Estatus
    # FK: Ilr001(8)
    h003009 = models.CharField(max_length=1, verbose_name='Estatus')
    # Usuario que carga/procesa
    # Campo automático
    h003010 = models.CharField(max_length=10, verbose_name='Usuario')
    # Fecha y Hora de Generac
    # Campo automático
    h003011 = models.DateTimeField(verbose_name='Fecha y Hora de Generac')
    # Monto de la transaccion
    h003012 = models.DecimalField(max_digits=19, decimal_places=2, verbose_name='Monto de la transaccion')
    # Tipo (Debito o Credito)
    h003013 = models.CharField(max_length=1, verbose_name='Tipo (Debito o Credito)', choices=OPCIONES_TIPO_ASIENTO)
    # Comentario del Operador
    h003014 = models.CharField(max_length=500, blank=True, verbose_name='Comentario del Operador')
    # Hora_LK1
    h003015 = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Hora_LK1')
    # Origen
    # FK: Choices
    h003016 = models.CharField(max_length=2, verbose_name='Origen', choices=OPCIONES_CANAL_SELECCIONADO)
    # Clase de alerta
    # FK: Ilr001(19)
    h003017 = models.CharField(max_length=1, verbose_name='Clase')
    # Terminal
    h003018 = models.CharField(max_length=10, blank=True, verbose_name='Terminal')
    # Evaluado ¿monto? ¿que?
    h003019 = models.DecimalField(max_digits=19, decimal_places=2, verbose_name='Evaluado')
    # Promedio
    h003020 = models.DecimalField(max_digits=19, decimal_places=2, verbose_name='Promedio')
    # Máximo
    h003021 = models.DecimalField(max_digits=19, decimal_places=2, verbose_name='Máximo')
    # Codigo Resultado
    # FK: Ilr001(17)
    h003022 = models.CharField(max_length=10, verbose_name='Codigo Resultado')
    # LK1COD - COD DE TRANSACCION
    # FK: Ilr001()
    h003023 = models.DecimalField(max_digits=3, decimal_places=0, verbose_name='LK1COD - COD DE TRANSACCION')
    # LK1NOP - Nombre del POS
    h003024 = models.CharField(max_length=23, blank=True, verbose_name='LK1NOP - Nombre del POS')
    # LK1039 - Cod de respuesta
    h003025 = models.DecimalField(max_digits=2, decimal_places=0, blank=True, verbose_name='LK1039 - Cod de respuesta')
    # LK1DNO - Destino Nodo   
    h003026 = models.CharField(max_length=6, blank=True, verbose_name='LK1DNO - Destino Nodo')
    # LK1038 - No de Autorización
    h003027 = models.CharField(max_length=6, blank=True, verbose_name='LK1038 - No de Autorización')
    # LK1022 - Entry Mode
    h003028 = models.CharField(max_length=3, blank=True, verbose_name='LK1022 - Entry Mode')
    # LK1PER - PERSONA: N, J , G
    # Choices
    h003029 = models.CharField(max_length=1, verbose_name='LK1PER - PERSONA: N, J , G', choices=OPCIONES_TIPO_PERSONA)
    # Usuario / Analista Upd
    # Blank en insert
    # Automatico en update
    h003030 = models.CharField(max_length=10, blank=True, verbose_name='Usuario / Analista Upd')
    # Fecha y Hora de Update
    # null en insert
    # automático en update
    h003031 = models.DateTimeField(blank=True, null=True, verbose_name='Fecha y Hora de Update')
    # Secuencia de operaciones - Deprecado
    h003032 = models.IntegerField(verbose_name='Secuencia de operaciones')
    # Codigo de Comercio ¿ISO? ¿REDES? ¿INTERNO?
    h003033 = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='Codigo de Comercio')
    # Nacionalidad
    # Choices
    h003034 = models.CharField(max_length=1, verbose_name='Nacionalidad', choices=OPCIONES_NACIONALIDAD)
    # Cedula o Rif DNI NIE TIE ¿numerico?
    h003035 = models.DecimalField(max_digits=9, decimal_places=0, verbose_name='Cedula o Rif')
    # LK1041 - Campo 41 
    h003036 = models.CharField(max_length=8, blank=True, verbose_name='LK1041 - Campo 41 ')
    # LK1MID - DE42 MERCHANT ID
    h003037 = models.CharField(max_length=15, blank=True, verbose_name='LK1MID - DE42 MERCHANT ID')
    # LK1NRI - DE48s42 NIV RIESGO
    h003038 = models.CharField(max_length=3, blank=True, verbose_name='LK1NRI - DE48s42 NIV RIESGO')
    # LK1PRE - DE61s4 TARJ PRESENT
    h003039 = models.DecimalField(max_digits=4, decimal_places=0, verbose_name='LK1PRE - DE61s4 TARJ PRESENT')
    # LK1PAP - DE61s13 POS COUNTRY
    h003040 = models.DecimalField(max_digits=3, decimal_places=0, verbose_name='LK1PAP - DE61s13 POS COUNTRY')
    # Limite de Sensibilidad en la Regla
    h003041 = models.DecimalField(max_digits=3, decimal_places=0, verbose_name='Limite de Sensibilidad en la Regla')
    # Total Acumulado Sens. del Cliente
    # ¿Todas las transacciones ya procesadas por ¿cliente??
    # Cliente = ¿DNI o Merchant?
    h003042 = models.DecimalField(max_digits=3, decimal_places=0, verbose_name='Total Acumulado Sens. del Cliente')
    # Codigo del Cliente
    # ¿Interno o externo, ej: codigo de cliente MC?
    # ¿numerico?
    h003043 = models.DecimalField(max_digits=9, decimal_places=0)
    # TIPO OPERAC. CONTAB
    # FK: Ilr001(23)
    h003044 = models.CharField(max_length=6, verbose_name='TIPO OPERAC. CONTAB')
    # Indice ILH003 (Autogenerado)
    h003045 = models.AutoField(primary_key=True, verbose_name='Indice ILH003 (Autogenerado)')
    # Indice ILH001
    # ¿FK? ¿por que no usaron el mismo h003045?
    h003046 = models.IntegerField(verbose_name='Indice ILH001')
    # Saldo Anterior
    # ¿de quien o de qué?
    h003047 = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Saldo Anterior')
    # IA - Calculo Prediccion Numerico
    # me caga el nombre T_T.
    h003048 = models.DecimalField(max_digits=17, decimal_places=15, verbose_name='IA - Calculo Prediccion Numerico')
    # Clasificacion Riesgo IA
    h003049 = models.CharField(max_length=20, verbose_name='Clasificacion Riesgo IA')

    class Meta:
        managed = False
        db_table = 'ilh003'
        db_table_comment = 'iLook - Historico de alertas'
        verbose_name = 'HistoricoAlerta'
        verbose_name_plural = 'HistoricoAlertas'


class TmpTransaccionISO(models.Model):
  """
  Modelo temporal para almacenar transacciones ISO 8583.
  Cada campo representa un Data Element (DE) del estándar ISO 8583.
  """
  # Campos de control de carga
  user = models.CharField(max_length=20, verbose_name='Usuario de carga')
  estatus = models.CharField(max_length=1, verbose_name='Estatus')
  proceso = models.IntegerField(verbose_name='Id Proceso de Validacion')

  # Campos ISO 1 a 128
  de002 = models.CharField(max_length=21, null=True, verbose_name='DE002 - PAN')
  de003 = models.CharField(max_length=6, null=True, verbose_name='DE003 - Processing Code')
  de004 = models.DecimalField(max_digits=12, decimal_places=2, null=True, verbose_name='DE004 - Amount')
  de005 = models.DecimalField(max_digits=12, decimal_places=2, null=True, verbose_name='DE005 - Amount, settlement')
  de006 = models.DecimalField(max_digits=12, decimal_places=2, null=True, verbose_name='DE006 - Amount, cardholder billing')
  de007 = models.CharField(max_length=10, null=True, verbose_name='DE007 - Transmission date & time')
  de008 = models.IntegerField(null=True, verbose_name='DE008 - Amount, cardholder billing fee')
  de009 = models.IntegerField(null=True, verbose_name='DE009 - Conversion rate, settlement')
  de010 = models.IntegerField(null=True, verbose_name='DE010 - Conversion rate, cardholder billing')
  de011 = models.IntegerField(null=True, verbose_name='DE011 - System trace audit number (STAN)')
  de012 = models.IntegerField(null=True, verbose_name='DE012 - Local transaction time (hhmmss)')
  de013 = models.IntegerField(null=True, verbose_name='DE013 - Local transaction date (MMDD)')
  de014 = models.IntegerField(null=True, verbose_name='DE014 - Expiration date (YYMM)')
  de015 = models.IntegerField(null=True, verbose_name='DE015 - Settlement date')
  de016 = models.IntegerField(null=True, verbose_name='DE016 - Currency conversion date')
  de017 = models.IntegerField(null=True, verbose_name='DE017 - Capture date')
  de018 = models.CharField(max_length=4, null=True, verbose_name='DE018 - Merchant type, or merchant category code')
  de019 = models.CharField(max_length=3, null=True, verbose_name='DE019 - Acquiring institution (country code)')
  de020 = models.SmallIntegerField(null=True, verbose_name='DE020 - PAN extended (country code)')
  de021 = models.SmallIntegerField(null=True, verbose_name='DE021 - Forwarding institution (country code)')
  de022 = models.CharField(max_length=12, null=True, verbose_name='DE022 - Point of service entry mode')
  de023 = models.SmallIntegerField(null=True, verbose_name='DE023 - Application PAN sequence number')
  de024 = models.SmallIntegerField(null=True, verbose_name='DE024 - Function code (ISO 8583:1993), or network international identifier (NII)')
  de025 = models.SmallIntegerField(null=True, verbose_name='DE025 - Point of service condition code')
  de026 = models.SmallIntegerField(null=True, verbose_name='DE026 - Point of service capture code')
  de027 = models.SmallIntegerField(null=True, verbose_name='DE027 - Authorizing identification response length')
  de028 = models.IntegerField(null=True, verbose_name='DE028 - Amount, transaction fee')
  de029 = models.IntegerField(null=True, verbose_name='DE029 - Amount, settlement fee')
  de030 = models.IntegerField(null=True, verbose_name='DE030 - Amount, transaction processing fee')
  de031 = models.IntegerField(null=True, verbose_name='DE031 - Amount, settlement processing fee')
  de032 = models.CharField(max_length=11, null=True, verbose_name='DE032 - Acquiring institution identification code')
  de033 = models.CharField(max_length=11, null=True, verbose_name='DE033 - Forwarding institution identification code')
  de034 = models.CharField(max_length=28, null=True, verbose_name='DE034 - Primary account number, extended')
  de035 = models.CharField(max_length=37, null=True, verbose_name='DE035 - Track 2 data')
  de036 = models.CharField(max_length=104, null=True, verbose_name='DE036 - Track 3 data')
  de037 = models.CharField(max_length=12, null=True, verbose_name='DE037 - Retrieval reference number')
  de038 = models.CharField(max_length=6, null=True, verbose_name='DE038 - Authorization identification response')
  de039 = models.CharField(max_length=2, null=True, verbose_name='DE039 - Response code')
  de040 = models.CharField(max_length=3, null=True, verbose_name='DE040 - Service restriction code')
  de041 = models.CharField(max_length=8, null=True, verbose_name='DE041 - Card acceptor terminal identification')
  de042 = models.CharField(max_length=15, null=True, verbose_name='DE042 - Card acceptor identification code ')
  de043 = models.CharField(max_length=40, null=True, verbose_name='DE043 - Card acceptor name/location')
  de044 = models.CharField(max_length=25, null=True, verbose_name='DE044 - Additional response data')
  de045 = models.CharField(max_length=76, null=True, verbose_name='DE045 - Track 1 data')
  de046 = models.CharField(max_length=999, null=True, verbose_name='DE046 - Additional data (ISO)')
  de047 = models.CharField(max_length=999, null=True, verbose_name='DE047 - Additional data (national)')
  de048 = models.CharField(max_length=999, null=True, verbose_name='DE048 - Additional data (private)')
  de049 = models.CharField(max_length=3, null=True, verbose_name='DE049 - Currency code, transaction')
  de050 = models.CharField(max_length=3, null=True, verbose_name='DE050 - Currency code, settlement')
  de051 = models.CharField(max_length=3, null=True, verbose_name='DE051 - Currency code, cardholder billing')
  de052 = models.CharField(max_length=8, null=True, verbose_name='DE052 - Personal identification number data')
  de053 = models.CharField(max_length=16, null=True, verbose_name='DE053 - Security related control information')
  de054 = models.CharField(max_length=120, null=True, verbose_name='DE054 - Additional amounts')
  de055 = models.CharField(max_length=999, null=True, verbose_name='DE055 - ICC data - EMV having multiple tags')
  de056 = models.CharField(max_length=999, null=True, verbose_name='DE056 - Reserved (ISO)')
  de057 = models.CharField(max_length=999, null=True, verbose_name='DE057 - Reserved (national)')
  de058 = models.CharField(max_length=999, null=True, verbose_name='DE058 - Reserved (national)')
  de059 = models.CharField(max_length=999, null=True, verbose_name='DE059 - Reserved (national)')
  de060 = models.CharField(max_length=999, null=True, verbose_name='DE060 - Reserved (national)')
  de061 = models.CharField(max_length=999, null=True, verbose_name='DE061 - Reserved (private)')
  de062 = models.CharField(max_length=999, null=True, verbose_name='DE062 - Reserved (private)')
  de063 = models.CharField(max_length=999, null=True, verbose_name='DE063 - Reserved (private)')
  de064 = models.CharField(max_length=8, null=True, verbose_name='DE064 - Message authentication code (MAC)')
  de065 = models.CharField(max_length=1, null=True, verbose_name='DE065 - Extended bitmap indicator')
  de066 = models.CharField(max_length=1, null=True, verbose_name='DE066 - Settlement code')
  de067 = models.CharField(max_length=2, null=True, verbose_name='DE067 - Extended payment code')
  de068 = models.CharField(max_length=3, null=True, verbose_name='DE068 - Receiving institution country code')
  de069 = models.CharField(max_length=3, null=True, verbose_name='DE069 - Settlement institution country code')
  de070 = models.CharField(max_length=3, null=True, verbose_name='DE070 - Network management information code')
  de071 = models.CharField(max_length=4, null=True, verbose_name='DE071 - Message number')
  de072 = models.CharField(max_length=4, null=True, verbose_name='DE072 - Last message\'s number')
  de073 = models.CharField(max_length=6, null=True, verbose_name='DE073 - Action date (YYMMDD)')
  de074 = models.CharField(max_length=10, null=True, verbose_name='DE074 - Number of credits')
  de075 = models.CharField(max_length=10, null=True, verbose_name='DE075 - Credits, reversal number')
  de076 = models.CharField(max_length=10, null=True, verbose_name='DE076 - Number of debits')
  de077 = models.CharField(max_length=10, null=True, verbose_name='DE077 - Debits, reversal number')
  de078 = models.CharField(max_length=10, null=True, verbose_name='DE078 - Transfer number')
  de079 = models.CharField(max_length=10, null=True, verbose_name='DE079 - Transfer, reversal number')
  de080 = models.CharField(max_length=10, null=True, verbose_name='DE080 - Number of inquiries')
  de081 = models.CharField(max_length=10, null=True, verbose_name='DE081 - Number of authorizations')
  de082 = models.CharField(max_length=12, null=True, verbose_name='DE082 - Credits, processing fee amount')
  de083 = models.CharField(max_length=12, null=True, verbose_name='DE083 - Credits, transaction fee amount')
  de084 = models.CharField(max_length=12, null=True, verbose_name='DE084 - Debits, processing fee amount')
  de085 = models.CharField(max_length=12, null=True, verbose_name='DE085 - Debits, transaction fee amount')
  de086 = models.CharField(max_length=16, null=True, verbose_name='DE086 - Total amount of credits')
  de087 = models.CharField(max_length=16, null=True, verbose_name='DE087 - Credits, reversal amount')
  de088 = models.CharField(max_length=16, null=True, verbose_name='DE088 - Total amount of debits')
  de089 = models.CharField(max_length=16, null=True, verbose_name='DE089 - Debits, reversal amount')
  de090 = models.CharField(max_length=42, null=True, verbose_name='DE090 - Original data elements')
  de091 = models.CharField(max_length=1, null=True, verbose_name='DE091 - File update code')
  de092 = models.CharField(max_length=2, null=True, verbose_name='DE092 - File security code')
  de093 = models.CharField(max_length=5, null=True, verbose_name='DE093 - Response indicator')
  de094 = models.CharField(max_length=7, null=True, verbose_name='DE094 - Service indicator')
  de095 = models.CharField(max_length=45, null=True, verbose_name='DE095 - Replacement amounts')
  de096 = models.CharField(max_length=8, null=True, verbose_name='DE096 - Message security code')
  de097 = models.CharField(max_length=16, null=True, verbose_name='DE097 - Net settlement amount')
  de098 = models.CharField(max_length=25, null=True, verbose_name='DE098 - Payee')
  de099 = models.CharField(max_length=11, null=True, verbose_name='DE099 - Settlement institution identification code')
  de100 = models.CharField(max_length=11, null=True, verbose_name='DE100 - Receiving institution identification code')
  de101 = models.CharField(max_length=17, null=True, verbose_name='DE101 - File name')
  de102 = models.CharField(max_length=28, null=True, verbose_name='DE102 - Account identification 1')
  de103 = models.CharField(max_length=28, null=True, verbose_name='DE103 - Account identification 2')
  de104 = models.CharField(max_length=100, null=True, verbose_name='DE104 - Transaction description')
  de105 = models.CharField(max_length=999, null=True, verbose_name='DE105 - Reserved for ISO use')
  de106 = models.CharField(max_length=999, null=True, verbose_name='DE106 - Reserved for ISO use')
  de107 = models.CharField(max_length=999, null=True, verbose_name='DE107 - Reserved for ISO use')
  de108 = models.CharField(max_length=999, null=True, verbose_name='DE108 - Reserved for ISO use')
  de109 = models.CharField(max_length=999, null=True, verbose_name='DE109 - Reserved for ISO use')
  de110 = models.CharField(max_length=999, null=True, verbose_name='DE110 - Reserved for ISO use')
  de111 = models.CharField(max_length=999, null=True, verbose_name='DE111 - Reserved for ISO use')
  de112 = models.CharField(max_length=999, null=True, verbose_name='DE112 - Reserved for national use')
  de113 = models.CharField(max_length=999, null=True, verbose_name='DE113 - Reserved for national use')
  de114 = models.CharField(max_length=999, null=True, verbose_name='DE114 - Reserved for national use')
  de115 = models.CharField(max_length=999, null=True, verbose_name='DE115 - Reserved for national use')
  de116 = models.CharField(max_length=999, null=True, verbose_name='DE116 - Reserved for national use')
  de117 = models.CharField(max_length=999, null=True, verbose_name='DE117 - Reserved for national use')
  de118 = models.CharField(max_length=999, null=True, verbose_name='DE118 - Reserved for national use')
  de119 = models.CharField(max_length=999, null=True, verbose_name='DE119 - Reserved for national use')
  de120 = models.CharField(max_length=999, null=True, verbose_name='DE120 - Reserved for private use')
  de121 = models.CharField(max_length=999, null=True, verbose_name='DE121 - Reserved for private use')
  de122 = models.CharField(max_length=999, null=True, verbose_name='DE122 - Reserved for private use')
  de123 = models.CharField(max_length=999, null=True, verbose_name='DE123 - Reserved for private use')
  de124 = models.CharField(max_length=999, null=True, verbose_name='DE124 - Reserved for private use')
  de125 = models.CharField(max_length=999, null=True, verbose_name='DE125 - Reserved for private use')
  de126 = models.CharField(max_length=999, null=True, verbose_name='DE126 - Reserved for private use')
  de127 = models.CharField(max_length=999, null=True, verbose_name='DE127 - Reserved for private use')
  de128 = models.CharField(max_length=999, null=True, verbose_name='DE128 - Reserved for private use')

  fecha_carga = models.DateTimeField(auto_now_add=True)

  class Meta:
    db_table = 'tmp_transaccion_iso'
    verbose_name = 'Transacción ISO'
    verbose_name_plural = 'Transacciones ISO'
    permissions = [
       ('cargar_archivo_iso', 'Puede cargar archivo ISO'),
       ('ejecutar_validaciones_iso', 'Puede ejecutar validaciones ISO')
    ]


class Tmp_transaccion_LK1(models.Model):
  lk1fec = models.DateTimeField(verbose_name='Fecha-Hora de carga', auto_now_add=True)
  lk1act = models.DateTimeField(verbose_name='Fecha-Hora de proceso', auto_now=True)
  lk1usu = models.CharField(max_length=20, verbose_name='Usuario carga')
  lk1fid = models.CharField(max_length=50, db_index=True, verbose_name='Identificador de carga Id')
  lk1pro = models.IntegerField(verbose_name='Proceso de carga')
  lk1seq = models.IntegerField(verbose_name='Secuencia de carga por proceso')
  lk1est = models.CharField(max_length=1, verbose_name='Estatus', choices=OPCIONES_ESTATUS_PROCESO)

  lk1hoy = models.DecimalField(max_digits=7, decimal_places=0, verbose_name='Fecha de transaccion SAAMMDD')
  lk1hor = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Hora de transaccion HHMMSSxxx')
  lk1ori = models.CharField(max_length=2, blank=True, verbose_name='Origen', choices=OPCIONES_CANAL_SELECCIONADO)
  lk1cod = models.DecimalField(max_digits=3, decimal_places=0, verbose_name='Codigo de transaccion')
  lk1tip = models.CharField(max_length=6, blank=True, verbose_name='Tipo operacion contable')
  lk1sbs = models.CharField(max_length=1, blank=True, verbose_name='Tipo de movimiento', choices=OPCIONES_TIPO_ASIENTO)
  lk1cla = models.CharField(max_length=20, blank=True, verbose_name='Numero de producto')
  lk1nta = models.CharField(max_length=20, blank=True, verbose_name='Numero de tarjeta')
  lk1mon = models.DecimalField(max_digits=17, decimal_places=2, verbose_name='Monto de la transaccion')
  lk1div = models.CharField(max_length=3, blank=True, verbose_name='Divisa original de la transaccion')
  lk1can = models.DecimalField(max_digits=3, decimal_places=0, verbose_name='Canal transaccional')
  lk1ter = models.CharField(max_length=10, blank=True, verbose_name='Terminal/POS/ATM')
  lk1nop = models.CharField(max_length=23, blank=True, verbose_name='Nombre del POS')
  lk1ciu = models.CharField(max_length=14, blank=True, verbose_name='Ciudad')
  lk1pai = models.CharField(max_length=3, blank=True, verbose_name='Pais origen')
  lk1cat = models.CharField(max_length=4, blank=True, verbose_name='Categoria del comercio')
  lk1res = models.DecimalField(max_digits=2, decimal_places=0, verbose_name='Codigo respuesta')
  lk1dno = models.CharField(max_length=6, blank=True, verbose_name='Destino nodo')
  lk1aut = models.CharField(max_length=6, blank=True, verbose_name='Numero de autorizacion')
  lk1pem = models.CharField(max_length=3, blank=True, verbose_name='Modo de ingreso - 022 POS Entry mode')
  lk1per = models.CharField(max_length=1, blank=True, verbose_name='Tipo de persona', choices=OPCIONES_TIPO_PERSONA)
  lk1nac = models.CharField(max_length=1, blank=True, verbose_name='Tipo de documento Id', choices=OPCIONES_TIPO_DOCUMENTO)
  lk1ced = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='Numero de documento Id')
  lk1cai = models.CharField(max_length=8, blank=True, verbose_name='Identificacion del aceptante - 041 Card acceptor terminal identification')
  lk1com = models.DecimalField(max_digits=9, decimal_places=0, verbose_name='Codigo del comercio')
  lk1mid = models.CharField(max_length=15, blank=True, verbose_name='Codigo del comercio emisor - DE42')
  lk1nri = models.CharField(max_length=3, blank=True, verbose_name='Nivel de riesgo - DE48s42')
  lk1pre = models.DecimalField(max_digits=4, decimal_places=0, verbose_name='Tarjeta Presente - DE61s4')
  lk1pap = models.DecimalField(max_digits=3, decimal_places=0, verbose_name='Pais emisor - DE61s13')
  lk1cte = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='No definido')
  lk1sat = models.DecimalField(max_digits=17, decimal_places=2, verbose_name='Saldo anterior')
  lk1fil = models.CharField(max_length=21, blank=True, verbose_name='Uso libre')

  class Meta:
    db_table = 'tmp_transacciones_lk1'
    db_table_comment = 'iLook - Carga movimiento formato LK1'
    verbose_name = 'TransaccionLK1'
    verbose_name_plural = 'TransaccionesLK1'
    permissions = [
      ("cargar_archivo_lk1", "Puede cargar archivos LK1"),
      ("validar_archivo_lk1", "Puede validar archivos LK1"),
    ]
    unique_together = ('lk1fid', 'lk1pro', 'lk1seq')

  def __str__(self):
    return f'Id Archivo: {self.lk1fid}, Proceso: {self.lk1pro}, Secuencia: {self.lk1seq} - {self.lk1hoy}-{self.lk1hor}'

  def get_codigo_transaccion_display(self):
    return self.get_ilr001_descripcion(14, self.lk1cod)
  def get_codigo_operacion_contable_display(self):
    return self.get_ilr001_descripcion(23, self.lk1tip)
  def get_canal_display(self):
    return self.get_ilr001_descripcion(1, self.lk1can)
  def get_pais_origen_display(self):
    return self.get_ilr001_descripcion(3, self.lk1pai)
  def get_categoria_comercio_display(self):
    return self.get_ilr001_descripcion(12, self.lk1cat)
  def get_codigo_respuesta_display(self):
    return self.get_ilr001_descripcion(17, self.lk1res)
  def get_pais_emisor_display(self):
    return self.get_ilr001_descripcion(3, self.lk1pap)

  def clean(self):
    errores = validar_transaccion_lk1(self)
    if errores:
      raise ValidationError(errores)


class Ilm016(models.Model):
  """
  Tabla maestra de paises a validar.
  Esta tabla une ILM006 con ILR0001 para establecer lista de paises para validar transacciones.
  FK:   (1) ILM006.M006005
        (2) ILR001.R001001 = 3 y ILR001.R001002
  """
  pk = models.CompositePrimaryKey('m016001', 'm016002')
  m016001 = models.DecimalField(max_digits=4, decimal_places=0, verbose_name='Numero de regla')
  m016002 = models.CharField(max_length=150, verbose_name='Descripcion Pais ISO')
  m016003 = models.CharField(max_length=15, verbose_name='Codigo Pais ISO')
  m016004 = models.SmallIntegerField()
  m016005 = models.CharField(max_length=10, verbose_name='Usuario')
  m016006 = models.DateTimeField(verbose_name='Fecha alta')

  class Meta:
    managed = False    
    db_table = 'ilm016'
    db_table_comment = 'iLook - Paises para validar transacciones'
    verbose_name = 'ReglaPais'
    verbose_name_plural = 'ReglasPaises'
    # permissions = [
    #   ("cargar_archivo_lk1", "Puede cargar archivos LK1"),
    #   ("validar_archivo_lk1", "Puede validar archivos LK1"),
    # ]

  def __str__(self):
    return f'Regla: {self.m016001} - {self.m016003}'