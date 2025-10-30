import pandas as pd
from core.models import TmpTransaccionISO
from celery import shared_task

@shared_task
def cargar_transacciones_desde_archivo(path_archivo, extension):
    df = pd.read_excel(path_archivo) if extension == 'xlsx' else pd.read_csv(path_archivo, sep='|')

    for _, row in df.iterrows():
        datos = {f'de{int(col):03}': str(row[col]) for col in df.columns if col.isdigit()}
        TmpTransaccionISO.objects.create(**datos)

    return f"{len(df)} transacciones cargadas"