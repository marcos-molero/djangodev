from django.conf import settings
from django.db import transaction
from core.models import TmpTransaccionISO
from utils.logging import registrar_log, AUDIT_ACCION, AUDIT_CANAL, AUDIT_NIVEL
from . import dividir_dataframe_en_chunks

import os
import pandas as pd


def cargar_archivo_iso(request, pi_path_archivo, pi_username):
  """
  Proceso de carga del archivo.
  """

  registrar_log(
    mensaje = f'Iniciando carga del archivo {pi_path_archivo} al sistema.',
    request = request,
    modulo = 'validar.services.procesar_archivo_en_segundo_plano',
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
      df_iter = pd.read_csv(pi_path_archivo, sep='|', chunksize=settings.GL_CHUNK_SIZE)

    contador_proceso = 1
    numero_lote = 1

    for df_chunk in df_iter:
      registros = []

      for _, lc_linea in df_chunk.iterrows():
        lc_datos = {
          f'de{int(col):03}': str(lc_linea[col]).zfill(settings.CAMPOS_CON_ZFIL[col]) 
          if col in settings.CAMPOS_CON_ZFIL 
          else str(lc_linea[col]) 
          for col in df.columns if col.isdigit()
        }

        # Campos automaticos.
        lc_datos['user'] = pi_username
        lc_datos['estatus'] = '0'
        lc_datos['proceso'] = contador_proceso
        contador_proceso = (contador_proceso % settings.GL_PROCESOS_VALIDACION) + 1

        registros.append(TmpTransaccionISO(**lc_datos))

      # Guardar un lote completo.
      # aca usamos transaction porque Postgre permite manejar el commit.
      try:
        with transaction.atomic():
          TmpTransaccionISO.objects.bulk_create(registros)
        registrar_log(
          mensaje = f'Trabajo # {numero_lote} de carga del archivo [{pi_path_archivo}] finalizado.',
          request = request,
          modulo = 'validar.services.procesar_archivo_en_segundo_plano',
          accion = AUDIT_ACCION.proceso,
          nivel = AUDIT_NIVEL.info,
          canal = AUDIT_CANAL.aplicacion
        )
      except Exception as lote_error:
        registrar_log(
          mensaje = f'Error en la carga del lote #{numero_lote}: {str(lote_error)}',
          request = request,
          modulo = 'validar.services.procesar_archivo_en_segundo_plano',
          accion = AUDIT_ACCION.proceso,
          nivel = AUDIT_NIVEL.info,
          canal = AUDIT_CANAL.aplicacion
        )
      numero_lote += 1

  except Exception as e:
    registrar_log(
      mensaje = f'Ocurrio un error inesperado: {str(e)}',
      request = request,
      modulo = 'validar.services.procesar_archivo_en_segundo_plano',
      accion = AUDIT_ACCION.proceso,
      nivel = AUDIT_NIVEL.info,
      canal = AUDIT_CANAL.aplicacion
    )

  finally:
    # Eliminar el archivo temporal
    if os.path.exists(pi_path_archivo):
      os.remove(pi_path_archivo)
