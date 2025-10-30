from utils.logging import registrar_log, AUDIT_ACCION, AUDIT_CANAL, AUDIT_NIVEL

class TrazabilidadAutenticacionMiddleware:
  """
  Middleware que registra accesos autenticados con trazabilidad por método y path.
  Evita duplicidad usando marca en el objeto request.
  """
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    response = self.get_response(request)

    # Evitar duplicados en el request.
    if not hasattr(request, '_log_autenticacion_registrado'):
      request._log_autenticacion_registrado = True

      path = request.path
      method = request.method

      # Solo registrar si el usuario está autenticado
      if method not in ['OPTIONS', 'HEAD']:

        if request.user.is_authenticated:
          registrar_log(
            mensaje=f'Usuario autenticado. Método: {method} Path: {path}',
            request=request,
            modulo='MiddlewareAutenticacion',
            accion=AUDIT_ACCION.acceso,
            nivel=AUDIT_NIVEL.info,
            canal=AUDIT_CANAL.autorizacion
          )
        else:
          registrar_log(
            mensaje=f'Usuario no autenticado. Método: {method} Path: {path}',
            request=request,
            modulo='MiddlewareAutenticacion',
            accion=AUDIT_ACCION.acceso,
            nivel=AUDIT_NIVEL.warning,
            canal=AUDIT_CANAL.autorizacion
          )

    return response