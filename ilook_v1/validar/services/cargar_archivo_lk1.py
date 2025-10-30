from datetime import datetime
from django.conf import settings
from django.db.models import Max
from django.db import transaction
from core.models import Tmp_transaccion_LK1
from utils.logging import registrar_log, AUDIT_ACCION, AUDIT_CANAL, AUDIT_NIVEL
from . import dividir_dataframe_en_chunks

import os
import pandas as pd
import uuid


def cargar_archivo_lk1(request, pi_path_archivo, pi_username):
  """
  Proceso de carga del archivo.
  Genera identificador unico para cada archivo cargado. lk1pro
  Genera secuencia de carga de los registros. lk1seq
  """

  identificador_carga = f"LK1_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:12]}"

  registrar_log(
    mensaje = f'Iniciando carga del archivo {pi_path_archivo} al sistema.',
    request = request,
    modulo = 'validar.services.procesar_archivo_LK1_en_segundo_plano',
    accion = AUDIT_ACCION.proceso,
    nivel = AUDIT_NIVEL.info,
    canal = AUDIT_CANAL.aplicacion
  )

  try:
  # Detectar tipo de archivo
    if pi_path_archivo.endswith('.xlsx'):
      df = pd.read_excel(pi_path_archivo)
      df_iter = dividir_dataframe_en_chunks(df, settings.GL_CHUNK_SIZE)
    else:
      df_iter = pd.read_csv(pi_path_archivo, sep=',', chunksize=settings.GL_CHUNK_SIZE)

    numero_lote = 1

    for df_chunk in df_iter:
      registros = []

      # Recupero la ultima secuencia para este proceso.
      ultima_seq = Tmp_transaccion_LK1.objects.filter(
        lk1fid = identificador_carga,
        lk1pro = numero_lote
      ).aggregate(Max('lk1seq'))['lk1seq__max'] or 0

      for i, (_, lc_linea) in enumerate(df_chunk.iterrows(), start=1):
        # Limpiar valor NaN de Pandas.
        lc_linea = lc_linea.where(pd.notnull(lc_linea), '')
        lc_datos = {
          'lk1usu': pi_username,
          'lk1fid': identificador_carga,
          'lk1pro': numero_lote,
          'lk1seq': ultima_seq + i,
          'lk1est': '0',
          'lk1hoy': lc_linea.get('LK1HOY'),
          'lk1hor': lc_linea.get('LK1HOR'),
          'lk1ori': lc_linea.get('LK1ORI'),
          'lk1cod': lc_linea.get('LK1COD'),
          'lk1tip': lc_linea.get('LK1TIP'),
          'lk1sbs': lc_linea.get('LK1SBS'),
          'lk1cla': lc_linea.get('LK1CLA'),
          'lk1nta': lc_linea.get('LK1NTA'),
          'lk1mon': lc_linea.get('LK1MON'),
          'lk1div': lc_linea.get('LK1DIV'),
          'lk1can': lc_linea.get('LK1CAN'),
          'lk1ter': lc_linea.get('LK1TER'),
          'lk1nop': lc_linea.get('LK1NOP'),
          'lk1ciu': lc_linea.get('LK1CIU'),
          'lk1pai': lc_linea.get('LK1PAI'),
          'lk1cat': lc_linea.get('LK1CAT'),
          'lk1res': lc_linea.get('LK1039'),
          'lk1dno': lc_linea.get('LK1DNO'),
          'lk1aut': lc_linea.get('LK1038'),
          'lk1pem': lc_linea.get('LK1022'),
          'lk1per': lc_linea.get('LK1PER'),
          'lk1nac': lc_linea.get('LK1NAC'),
          'lk1ced': lc_linea.get('LK1CED'),
          'lk1cai': lc_linea.get('LK1041'),
          'lk1com': lc_linea.get('LK1COM'),
          'lk1mid': lc_linea.get('LK1MID'),
          'lk1nri': lc_linea.get('LK1NRI'),
          'lk1pre': lc_linea.get('LK1PRE'),
          'lk1pap': lc_linea.get('LK1PAP'),
          'lk1cte': lc_linea.get('LK1CTE'),
          'lk1sat': lc_linea.get('LK1SAT'),
          'lk1fil': lc_linea.get('LK1FIL'),
        }
        registros.append(Tmp_transaccion_LK1(**lc_datos))

      # Guardar un lote completo.
      # aca usamos transaction porque Postgre permite manejar el commit.
      try:
        with transaction.atomic():
          Tmp_transaccion_LK1.objects.bulk_create(registros)
        registrar_log(
          mensaje = f'Trabajo # {numero_lote} de carga del archivo LK1 [{pi_path_archivo}] finalizado.',
          request = request,
          modulo = 'validar.services.procesar_archivo_LK1_en_segundo_plano',
          accion = AUDIT_ACCION.proceso,
          nivel = AUDIT_NIVEL.info,
          canal = AUDIT_CANAL.aplicacion
        )
        # Enviar Correo?
      except Exception as lote_error:
        registrar_log(
          mensaje = f'Error en la carga del lote LK1 #{numero_lote}: {str(lote_error)}',
          request = request,
          modulo = 'validar.services.procesar_archivo_LK1_en_segundo_plano',
          accion = AUDIT_ACCION.proceso,
          nivel = AUDIT_NIVEL.error,
          canal = AUDIT_CANAL.aplicacion
        )
        # Enviar Correo?
      numero_lote += 1

  except Exception as e:
    registrar_log(
      mensaje = f'Ocurrio un error inesperado en carga LK1: {str(e)}',
      request = request,
      modulo = 'validar.services.procesar_archivo_LK1_en_segundo_plano',
      accion = AUDIT_ACCION.proceso,
      nivel = AUDIT_NIVEL.error,
      canal = AUDIT_CANAL.aplicacion
    )
    # Enviar Correo?

  finally:
    # Eliminar el archivo temporal
    if os.path.exists(pi_path_archivo):
      os.remove(pi_path_archivo)
