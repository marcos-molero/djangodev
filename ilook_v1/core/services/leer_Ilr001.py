"""
Paquete: core.services.leer_Ilr001
Recupera la descripcion del pais desde el maestro de tablas generales.
"""
def get_ilr001_descripcion(tabla : int, codigo : str) -> str | None:
  from core.models import Ilr001
  
  lc_valor = Ilr001.objects.filter(
    r001001 = tabla, 
    r001002 = codigo, 
    r001004 = '0'
  ).values_list('r001003', flat=True).first()
  return lc_valor.strip() if lc_valor else None
