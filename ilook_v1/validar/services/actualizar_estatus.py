from core.models import Tmp_transaccion_LK1
from django.utils import timezone

def actualizar_estatus(tx, estatus):
  """ 
  Actualiza el estatus en el Tmp.
  """
  Tmp_transaccion_LK1.objects.filter(
    lk1fid = tx.lk1fid, 
    lk1fec = tx.lk1fec, 
    lk1hor = tx.lk1hor
  ).update(lk1est=estatus, lk1act=timezone.now())