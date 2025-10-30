from datetime import time
from core.models import Ilm016, Tmp_transaccion_LK1, Ilm006
from utils.logging import registrar_log, AUDIT_ACCION, AUDIT_CANAL, AUDIT_NIVEL

def lc_grabar_log(info: dict, tx: Tmp_transaccion_LK1, regla: Ilm006):
  registrar_log(
    mensaje = f'Regla [{regla.m001001}] no coincide para transaccion [{tx.lk1fid, tx.lk1pro, tx.lk1seq}].',
    modulo = 'validar.services.evaluar_regla',
    accion = AUDIT_ACCION.validacion,
    nivel = AUDIT_NIVEL.warning,
    canal = AUDIT_CANAL.validacion,
    request_usuario = info['usuario'],
    request_ip = info['ip'],
    request_ua = info['ua'],
  )


def evaluar_regla(info: dict, tx: Tmp_transaccion_LK1, regla: Ilm006) -> bool:
  """
  Este servicio se encargará de aplicar la lógica de cruce para el tipo de 
  transacción ATM, incluyendo la validación directa y la validación cruzada 
  con ILM016.

  entry:
    - tx: instancia de Tmp_transaccion_LK1
    - regla: instancia de Ilm006

  returns:
    - bool : True si cumple la regla
             False si falla alguna validación.
  """
  try:
    # Origen
    if regla.m006004 and regla.m006004.strip() != '':
      if regla.m006004 and tx.lk1ori != regla.m006004:
        lc_grabar_log(info, tx, regla)
        return False

    # Rango de horas.
    if regla.m006025 and regla.m006026:
      hh = int(str(tx.lk1hor).zfill(11)[0:2])
      mm = int(str(tx.lk1hor).zfill(11)[2:4])
      ss = int(str(tx.lk1hor).zfill(11)[4:6])
      #print(f'lk1hor: {str(tx.lk1hor).zfill(11)}, Hora: {hh}, minuto: {mm}, segundo: {ss}')
      hora = time(hh, mm, ss)

      # Cuando la hora_hasta pasa de las 00:00
      hora_desde = regla.m006025
      hora_hasta = regla.m006026
      # si la hora pasa de medianoche
      if hora_desde < hora_hasta:
        if not (hora_desde <= hora <= hora_hasta):
          lc_grabar_log(info, tx, regla)
          return False
      else:
        if not (hora >= hora_desde and hora <= hora_hasta):
          lc_grabar_log(info, tx, regla)
          return False

    # Monto de la trx.
    if regla.m006035 and regla.m006035 > 0.00:
      if tx.lk1mon <= regla.m006035:
        lc_grabar_log(info, tx, regla)
        return False

    # Tablas dependientes o referencias cruzadas.

    # Validar Canales
    if regla.m006005 == 'L':
      if not Ilm016.objects.filter(m016001=regla.m006001, m016003=tx.lk1pai).exists():
        lc_grabar_log(info, tx, regla)
        return False

  except Exception as e:
    registrar_log(
      mensaje = f'Ocurrio un error inesperado, lote {info['id_lote']}. Transaccion [{tx.lk1fid},{tx.lk1pro},{tx.lk1seq}] : {str(e)}.',
      modulo = 'validar.services.evaluar_regla',
      accion = AUDIT_ACCION.proceso,
      nivel = AUDIT_NIVEL.info,
      canal = AUDIT_CANAL.validacion,
      request_usuario = info['usuario'],
      request_ip = info['ip'],
      request_ua = info['ua']
    )
    # Le cambio el estatus a la transaccion para notificar error en la aplicación.
    tx.lk1est = 'E'
    return False

  # Si no hay errores de ningun tipo.
  return True