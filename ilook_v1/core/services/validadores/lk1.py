from utils.ilr001_validadores import validar_ilr001


def validar_codigo_transaccion(codigo):
    return validar_ilr001(14, codigo, "Código de transacción")

def validar_operacion_contable(codigo):
    return validar_ilr001(23, codigo, "Operación contable")

def validar_canal(codigo):
    return validar_ilr001(1, codigo, "Canal transaccional")

def validar_pais_origen(codigo):
    return validar_ilr001(3, codigo, "País de origen")

def validar_categoria_comercio(codigo):
    return validar_ilr001(12, codigo, "Categoría del comercio")

def validar_codigo_respuesta(codigo):
    return validar_ilr001(17, codigo, "Código de respuesta")

def validar_pais_emisor(codigo):
    return validar_ilr001(3, codigo, "País emisor")

def validar_transaccion_lk1(instancia):
    errores = []

    errores += validar_codigo_transaccion(instancia.lk1cod)
    errores += validar_operacion_contable(instancia.lk1tip)
    errores += validar_canal(instancia.lk1can)
    errores += validar_pais_origen(instancia.lk1pai)
    errores += validar_categoria_comercio(instancia.lk1cat)
    errores += validar_codigo_respuesta(instancia.lk1res)
    errores += validar_pais_emisor(instancia.lk1pap)

    return errores