import logging


LOGGERS = {
  'sesion': logging.getLogger('sesion'),     # login, logout, intentos fallidos, accessos no autorizados.
  'data': logging.getLogger('data'),         # Accesos CRUD
  'app': logging.getLogger('app')            # lógica de aplicación, por defecto
}

# Helper para campo "accion"
class AUDIT_ACCION:
  lista = 'list'
  crear = 'create'
  leer = 'retrieve'
  diccionario = 'dictionary'
  actualizar = 'update'
  eliminar = 'delete'
  limpiar = 'clean'
  conectarse = 'login'
  desconectarse = 'logout'
  token = 'token'
  error = 'error'
  acceso = 'access'
  validacion = 'validate'
  no_encontrado = 'not_found'
  denegado = 'denied'
  evento = 'event'
  sistema = 'system'
  proceso = 'process'


# Helper para campo NIVEL
class AUDIT_NIVEL:
  debug = 'debug'
  info = 'info'
  error = 'error'
  warning = 'warning'


# Helper para campo CANAL
class AUDIT_CANAL:
  aplicacion = 'app'
  autorizacion = 'sesion'
  datos = 'data'
  validacion = 'validacion'


def registrar_log(
  mensaje: str,
  request: str = None,
  modulo: str = None,
  accion: str = None,
  nivel: str = 'info',
  canal: str = 'app',
  request_usuario: str = None,
  request_ip: str = None,
  request_ua: str = None
):
  """
  Registra un mensaje de log con formato unificado.

  Args:
      mensaje (str): Mensaje principal.
      usuario (str): Usuario autenticado.
      request (str): Trae los datos de la peticion.
      accion (str): Acción realizada (create, update, delete, etc.).
      nivel (str): Nivel de log ('info', 'warning', 'error', etc.).
      canal (str): Logger especifico (acceso, app, data)
      request_usuario (str): En caso de no contar con el <request> se puede enviar el user.
      request_ip (str): En caso de no contar con el <request> se puede enviar la IP.
      request_ua (str): En caso de no contar con el <request> se puede enviar el user agent.
  """
  usuario = 'anonimo'
  ip = 'IP desconocida'
  ua = 'User Agent desconocido'

  if request:
    try:
      usuario = request.user.username if request.user.is_authenticated else 'anonimo'
      if usuario == 'anonimo' and request.data.get('username'):
        usuario = request.data.get('username')
    except Exception:
      pass
    ip = request.META.get('REMOTE_ADDR')
    ua = request.META.get('HTTP_USER_AGENT', '')

  if request_usuario:
    usuario = request_usuario
  if request_ip:
    ip = request_ip
  if request_ua:
    ua = request_ua

  partes = [f'[{modulo or "sistema"}]', f'[{accion or "evento"}]', mensaje]

  if usuario:
      partes.append(f'Usuario: {usuario}')
  if ip:
      partes.append(f'IP: {ip}')
  if ua:
      partes.append(f'UA: {ua}')

  texto = ' '.join(partes)

  logger = LOGGERS.get(canal, logging.getLogger('app'))

  if nivel == 'info':
    logger.info(texto)
  elif nivel == 'warning':
    logger.warning(texto)
  elif nivel == 'error':
    logger.error(texto)
  elif nivel == 'debug':
    logger.debug(texto)
  else:
    logger.info(texto)