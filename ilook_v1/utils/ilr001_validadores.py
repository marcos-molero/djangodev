def validar_ilr001(tabla, codigo, campo_nombre):
  """
  Valida tablas en el maestro de Tablas Generales

  parms:
    - tabla <str> : Codigo de la tabla a consultar.
    - codigo <str> : Codigo del valor a verificar. Detalle de la tabla.
    - campo_nombre <str> : Nombre del campo para efectos de personalizar respuesta.

  returns:
    - String : Devuelve una cadena indicando el campo y error.
  """
  from core.models import Ilr001
  
  if not Ilr001.objects.filter(r001001=tabla, r001002=codigo, r001004='0').exists():
    return [f"{campo_nombre} inválido: {codigo}"]
  return []