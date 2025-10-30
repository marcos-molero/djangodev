from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from django.conf import settings
from core.models import Tmp_transaccion_LK1, Ilm006
from .evaluar_regla import evaluar_regla
from .registrar_alerta import registrar_alerta
from .actualizar_estatus import actualizar_estatus
from utils.logging import registrar_log, AUDIT_ACCION, AUDIT_CANAL, AUDIT_NIVEL
from utils.auditoria import grabar_auditoria

import uuid


def validar_transacciones_lk1(request):
  """
  Ejecuta validaciones sobre las reglas.
  En caso de encontrar alguna que cumnplimente, se genera registro en Ilh003.
  """
  registrar_log(
    mensaje = 'Inicio del proceso de validacion de archivo LK1',
    request = request,
    modulo = 'validar.services.validar_transacciones_lk1',
    accion = AUDIT_ACCION.proceso,
    nivel = AUDIT_NIVEL.info,
    canal = AUDIT_CANAL.aplicacion
  )

  proceso_validacion = f"VAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
  pendientes = list(Tmp_transaccion_LK1.objects.filter(lk1est='0'))
  total = len(pendientes)
  workers = settings.GL_PROCESOS_VALIDACION or 4
  chunk_size = settings.GL_CHUNK_SIZE or max(1, total // workers)

  # Si no hay transacciones.
  if total == 0:
    registrar_log(
      mensaje = 'No hay transacciones pendientes para revisar en archivo LK1',
      request = request,
      modulo = 'validar.services.validar_transacciones_lk1',
      accion = AUDIT_ACCION.proceso,
      nivel = AUDIT_NIVEL.warning,
      canal = AUDIT_CANAL.aplicacion
    )

  def procesar_lote(args):

    id_lote, lote, request = args

    #print(f'Lote: {id_lote}. Transacciones: {lote}')

    registrar_log(
      mensaje = f'Procesando validaciones de archivo LK1, lote {id_lote}.',
      request = request,
      modulo = 'validar.services.validar_transacciones_lk1',
      accion = AUDIT_ACCION.proceso,
      nivel = AUDIT_NIVEL.info,
      canal = AUDIT_CANAL.aplicacion
    )

    info = {
      'proceso_carga': None,
      'proceso_validacion': proceso_validacion,
      'id_lote': id_lote,
      'usuario': request.user.username,
      'ip': request.META.get('REMOTE_ADDR'),
      'ua': request.META.get('HTTP_USER_AGENT', ''),
    }

    try:
      for transaccion in lote:
        actualizar_estatus(transaccion, '1')
        info['proceso_carga'] = transaccion.lk1fid
        reglas = Ilm006.objects.filter(m006040='0')

        genero_alerta = False
        for regla in reglas:
          if evaluar_regla(info, transaccion, regla):
            #registrar_alerta(transaccion, regla)
            actualizar_estatus(transaccion, '4')
            genero_alerta = True
            grabar_auditoria(
              mensaje = f'[Regla] {regla.m006001} aplicada a la transaccion [{transaccion.lk1fid}, {transaccion.lk1pro}, {transaccion.lk1seq}].',
              info=info,
              datos=f'[[Transaccion]] {str(transaccion)} [[Regla]] {str(regla)}'
            )
            break  # Solo una alerta por transacción
        # Si no genero alerta.
        if not genero_alerta and transaccion.lk1est != 'E':
          actualizar_estatus(transaccion, '9')
          grabar_auditoria(
            mensaje = f'La transaccion [{transaccion.lk1fid}, {transaccion.lk1pro}, {transaccion.lk1seq}] no cumple con ninguna regla configurada y activa.',
            info=info,
            datos=f'[[Transaccion]] {str(transaccion)} [[Regla]] {str(regla)}'
          )
        # Si hubo algun error en la validación.
        if not genero_alerta and transaccion.lk1est == 'E':
          actualizar_estatus(transaccion, '2')
          grabar_auditoria(
            mensaje = f'La transaccion [{transaccion.lk1fid}, {transaccion.lk1pro}, {transaccion.lk1seq}] no pudo ser validada por errores en la data.',
            info=info,
            datos=f'[[Transaccion]] {str(transaccion)} [[Regla]] {str(regla)}'
          )

      registrar_log(
        mensaje = f'Proceso de validaciones de archivo LK1, lote {id_lote} Finalizado.',
        request = request,
        modulo = 'validar.services.validar_transacciones_lk1',
        accion = AUDIT_ACCION.proceso,
        nivel = AUDIT_NIVEL.info,
        canal = AUDIT_CANAL.aplicacion
      )
    except Exception as e:
      registrar_log(
        mensaje=f'Error en auditoría lote {id_lote}: {str(e)}',
        request=request,
        modulo='validar.services.validar_transacciones_lk1',
        accion=AUDIT_ACCION.error,
        nivel=AUDIT_NIVEL.error,
        canal=AUDIT_CANAL.aplicacion
      )


  # lotes = [1, 2, ..., n]
  lotes = [
    (idx + 1, pendientes[i:i + chunk_size], request)
    for idx, i in enumerate(range(0, total, chunk_size))
  ]
  with ThreadPoolExecutor(max_workers=workers) as executor:
    executor.map(procesar_lote, lotes)

