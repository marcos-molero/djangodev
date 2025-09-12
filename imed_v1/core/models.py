ESTATUS_MEDICOS_CHOICES = {
  '00': 'Activo',
  '01': 'Suspendido',
  '02': 'Vacaciones',
  '99': 'Desincorporado'
}

DIAS_CHOICES = [
  ('LU', 'Lunes'),
  ('MA', 'Martes'),
  ('MI', 'Miercoles'),
  ('JU', 'Jueves'),
  ('VI', 'Viernes'),
  ('SA', 'Sabado'),
  ('DO', 'Domingo')
]

ESTATUS_PACIENTES_CHOICES = [
  ('00', 'Activo'),
  ('01', 'Suspendido'),
  ('02', 'En registro'),
  ('98', 'Transferido'),
  ('99', 'Inactivo'),
]

SEXO_CHOICES = {
    'M': 'Masculino',
    'F': 'Femenino'
}

PARENTESCO_CHOICES = {
    'TI': 'Titular',
    'MA': 'Madre',
    'PA': 'Padre',
    'HE': 'Hermano/a',
    'ES': 'Esposo/a',
    'HI': 'Hijo/a'
}

DIAS_MAP = {
  'MON': 'LU',
  'TUE': 'MA',
  'WED': 'MI',
  'THU': 'JU',
  'FRI': 'VI',
  'SAT': 'SA',
  'SUN': 'DO',
}