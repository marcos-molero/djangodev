from rest_framework import status
from utils.logging import registrar_log, AUDIT_ACCION, AUDIT_CANAL, AUDIT_NIVEL
from core.models import TmpTransaccionISO, Ilm006
from .cumple_regla import cumple_regla
from .actualizar_estatus import actualizar_estatus
from .registrar_alerta import registrar_alerta


def validar_transacciones_iso(request, proceso_id, usuario, proceso):
  """
  Ejecuta validaciones sobre las reglas.
  En caso de encontrar alguna que cumnplimente, se genera registro en Ilh003.
  """

  registrar_log(
    mensaje = 'Inicia proceso de validación',
    request = request,
    modulo = 'validar.services.validar_proceso',
    accion = AUDIT_ACCION.proceso,
    nivel = AUDIT_NIVEL.info,
    canal = AUDIT_CANAL.aplicacion
  )

  try:
    transacciones = []
    if proceso == 'atm':
      transacciones = TmpTransaccionISO.objects.filter(user=usuario, estatus='0', proceso=proceso_id)
    else:
      return {
        'respuesta': 'No indico un proceso valido.', 
        'status': status.HTTP_400_BAD_REQUEST,
        'datos': {},
      }
    reglas = Ilm006.objects.filter(m006040='0')
    alertas_generadas = 0

    # Si no consigue transacciones pendiente por procesar en el TmpTransaccionISO
    if not transacciones:
      return {
        'respuesta': 'No hay transacciones cargadas para validar.', 
        'status': status.HTTP_400_BAD_REQUEST,
        'datos': {},
      }
    
    # Si no consigue reglas activas.
    if not reglas:
      return {
        'respuesta': 'No hay reglas activas para validar.', 
        'status': status.HTTP_400_BAD_REQUEST,
        'datos': {},
      }

    # Se deben generar alertas todas las reglas.
    for tx in transacciones:
      alerta = False
      for regla in reglas:
        print(f'Regla-num: {regla.m006001}, resultado={cumple_regla(tx, regla)}')
        if cumple_regla(tx, regla):
          registrar_alerta(tx, regla, True)
          alerta=True

      actualizar_estatus(tx, '2')
      if alerta:
        alertas_generadas += 1

    registrar_log(
      mensaje = 'Se han generado las validaciones.',
      request = request,
      modulo = 'validar.services.validar_proceso',
      accion = AUDIT_ACCION.proceso,
      nivel = AUDIT_NIVEL.info,
      canal = AUDIT_CANAL.aplicacion
    )
    return {
      'respuesta': 'Se han generado las validaciones.', 
      'status': status.HTTP_200_OK, 
      'datos': {
        'proceso': proceso_id, 
        'transacciones_validadas': transacciones.count(),
        'alertas_generadas': alertas_generadas,            
      }}
  
  except Exception as e:
    registrar_log(
      mensaje = 'Ocurrio un error al validar las transacciones.',
      request = request,
      modulo = 'validar.services.validar_proceso',
      accion = AUDIT_ACCION.proceso,
      nivel = AUDIT_NIVEL.warning,
      canal = AUDIT_CANAL.aplicacion
    )

    return {
      'respuesta': 'Ocurrio un error al validar las transacciones.',
      'status': status.HTTP_400_BAD_REQUEST,
      'datos': {
        'proceso': proceso_id,
        'transacciones_validadas': len(transacciones),
        'alertas_generadas': alertas_generadas,
        'detalle': str(e)
      }}
