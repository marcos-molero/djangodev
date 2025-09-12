from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings

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
    ('00', 'Canales'),
]
OPCIONES_ELEMENTO_SELECCIONADO = [
    (' ', 'No validar'),
    ('E', 'Modo entrada libre'),
    ('L', 'Listar'),
]
OPCIONES_LAPSO_TIEMPO = [
    ('S', 'Segundos'),
    ('M', 'Minutos'),
    ('H', 'Horas'),
]
OPCIONES_TIPO_PERSONA = [
    (' ', 'No validar'),
    ('N', 'Natural'),
    ('J', 'Juridico'),
    ('G', 'Gobierno'),
]
OPCIONES_FERIADO = [
    ('F', 'Feriado'),
    ('H', 'Habil'),
    ('A', 'Ambos'),
]


class TokenConVencimiento(models.Model):
  """
  Control de token con vigencia.
  """
  key = models.CharField(max_length=40, primary_key=True)
  user = models.OneToOneField(User, related_name='token_con_vencimiento', on_delete=models.CASCADE)
  created_at = models.DateTimeField(auto_now_add=True)

  def is_expired(self):
    lc_timeout = getattr(settings, 'TOKEN_TIMEOUT_SECONDS', 3600)
    return (timezone.now() - self.created_at).total_seconds() > lc_timeout
  
  def __str__(self):
    return self.key
  

class Ilr001(models.Model):
    """
    Tablas generales del sistema
    FK:
    """
    #pk = models.CompositePrimaryKey('r001001', 'r001002')
    r001001 = models.SmallIntegerField(verbose_name='Tabla')
    r001002 = models.CharField(max_length=15, verbose_name='Item')
    r001003 = models.CharField(max_length=150, verbose_name='Descripción')
    r001004 = models.CharField(max_length=1, verbose_name='Estatus')
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
        unique_together = ['r001001', 'r001002']


class Ilr002(models.Model):
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
    m002011 = models.CharField(max_length=1, verbose_name='Estatus')
    m002012 = models.CharField(max_length=10, verbose_name='Usuario')
    m002013 = models.DateTimeField(auto_now=True, verbose_name='Fecha actualización')

    class Meta:
        managed = False
        db_table = 'ilm002'
        db_table_comment = 'Tabla de monedas'
        verbose_name = 'Moneda'
        verbose_name_plural = 'Monedas'


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
    Alertas
    FK: Ilr001
    """
    m004001 = models.CharField(max_length=10, primary_key=True, verbose_name='Código')
    m004002 = models.CharField(max_length=80, verbose_name='Descripción')
    m004003 = models.CharField(max_length=2, verbose_name='Gravedad')
    m004004 = models.CharField(max_length=2, verbose_name='Acción')
    m004005 = models.CharField(max_length=1, verbose_name='Estatus')
    m004006 = models.CharField(max_length=1, verbose_name='Clase')
    m004007 = models.CharField(max_length=10, verbose_name='Usuario')
    m004008 = models.DateTimeField(auto_now=True, verbose_name='fecha')

    class Meta:
        managed = False
        db_table = 'ilm004'
        db_table_comment = 'iLook - Alertas'
        verbose_name = 'Alerta'
        verbose_name_plural = 'Alertas'


class Ilm006(models.Model):
    """
    Reglas de usuario
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
    m006019 = models.CharField(max_length=1, verbose_name='alerta', blank=True, choices=OPCIONES_ELEMENTO_SELECCIONADO)
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
