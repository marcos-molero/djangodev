from utils.logging import registrar_log, AUDIT_NIVEL, AUDIT_ACCION, AUDIT_CANAL
from .registrar_alerta import registrar_alerta


def cumple_regla(tx, regla):
  """ 
  Verifica si la transacción cumple con las reglas del usuario.
  Si no cumple una regla, no registra una alerta en Ilh003.
  Todos los campos del archivo forman una sentencia logica AND.

  Es decir, se deben cumplir todas las condiciones cargadas en Reglas, para emitir Alerta.

  emitir_alerta : Campo indicador para determinar si emite o no la alerta.
  """

  emitir_alerta = False

  # Origen
  # Campo critico
  # ---------------------------------------------------------------------------------------
  if tx.lk1ori != '' and not regla.objects.filter(m006004=tx.lk1ori).exists():
    registrar_log(
      mensaje = f'Transaccion {tx} no cumple con regla Origen.',
      request = None,
      modulo = 'validar.archivo_lk1',
      accion = AUDIT_ACCION.proceso,
      nivel = AUDIT_NIVEL.error,
      canal = AUDIT_CANAL.datos
    )
    #return False
    emitir_alerta = True
  
  # Pais origen
  # Campo critico
  # ---------------------------------------------------------------------------------------
  if not emitir_alerta and tx.lk1pai != '' and regla.objects.filter(m006005=tx.lk1pai).exists():
    registrar_log(
      mensaje = f'Transaccion {tx} no cumple con regla Pais origen.',
      request = None,
      modulo = 'validar.archivo_lk1',
      accion = AUDIT_ACCION.proceso,
      nivel = AUDIT_NIVEL.error,
      canal = AUDIT_CANAL.datos
    )
    return False

  if emitir_alerta:
    registrar_alerta(tx, regla, True)

  return True
