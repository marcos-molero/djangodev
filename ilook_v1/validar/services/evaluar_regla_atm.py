from core.models import Ilm006
from utils.logging import registrar_log, AUDIT_ACCION, AUDIT_CANAL, AUDIT_NIVEL 

def evaluar_regla_atm(tx, regla):
  """
  Este servicio se encargará de aplicar la lógica de cruce para el tipo de 
  transacción ATM, incluyendo la validación directa y la validación cruzada 
  con ILM016.

  entry:
    - tx: instancia de Tmp_transaccion_LK1
    - regla: instancia de Ilm006

  returns:
    None
  """

  # Validación directa

  # Origen
  if regla.m006004 and tx.lk1ori != regla.m006004:
    registrar_log(
      mensaje = f'ATM: LK1ORI = {tx.lk1ori}, esperado = {regla.m006004}; lk1pai = {tx.lk1pai}, validacion cruzada = {regla.m006005}',
      modulo = 'validar.evaluar_regla_atm',
      accion = AUDIT_ACCION.proceso ,
      nivel = AUDIT_NIVEL.error,
      canal=AUDIT_CANAL.aplicacion,
    )
    return False

  # Validaciones cruzada

  # Lk1pai contra ILM006.
  if regla.m006005 == 'L':
    existe = Ilm006.objects.filter(
      m016001 = regla.m006001,
      m016003 = tx.lk1pai
    ).exists()
    if not existe:
      return False
    
  return True