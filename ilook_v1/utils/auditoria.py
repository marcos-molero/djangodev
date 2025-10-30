from functools import wraps
from .logging import registrar_log  # o desde donde lo tengas 
from validar.models import AuditoriaValidacion


def grabar_auditoria(mensaje: str, info: dict, datos: None):
  """
  Registro de auditoria para proceso en lote.
  Este funciona para los procesos de validación de transacciones.

  entry
  - mensaje (str) : Descripción de la entrada en el registro.
  - info (dict): Información sobre el proceso de carga/validacion.
  - datos (?): Cualquier información adicional para registro.
  """
  try:
    AuditoriaValidacion.objects.create(
      proceso = info['proceso_carga'],
      proceso_validacion = info['proceso_validacion'],
      mensaje = mensaje,
      datos = datos
    )
  except Exception as e:
    pass



# Decorador para vistas basadas en funciones (FBV)

def auditar_evento_fbv(modulo: str, accion: str, canal: str = 'app', nivel: str = 'info'):
    def decorador(func):
      @wraps(func)
      def wrapper(request, *args, **kwargs):
        try:
          usuario = request.user.username if request.user.is_authenticated else 'anonimo'
          ip = request.META.get('REMOTE_ADDR')
          ua = request.META.get('HTTP_USER_AGENT', '')

          registrar_log(
            mensaje = f'Acceso a [{modulo}]',
            usuario = usuario,
            ip = ip,
            ua = ua,
            modulo = modulo,
            accion = accion,
            nivel = nivel,
            canal = canal
          )

        except Exception as e:
          registrar_log(
            mensaje = f'Error en decorador FBV: [{repr(e)}]',
            usuario = 'sistema',
            ip = 'N/A',
            ua = 'N/A',
            modulo = modulo,
            accion = accion,
            nivel = 'error',
            canal = 'app'
          )
        return func(request, *args, **kwargs)
      return wrapper
    return decorador


# Decorador para vistas basadas en clase (CBV)

def auditar_evento_cbv(modulo: str, accion: str, canal: str = 'app', nivel: str = 'info'):
  def decorador(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
      try:
        request = self.request
        usuario = request.user.username if request.user.is_authenticated else 'anonimo'
        ip = request.META.get('REMOTE_ADDR')
        ua = request.META.get('HTTP_USER_AGENT', '')

        registrar_log(
          mensaje = f'Acceso a [{modulo}]',
          usuario = usuario,
          ip = ip,
          ua = ua,
          modulo = modulo,
          accion = accion,
          nivel = nivel,
          canal = canal
        )
      except Exception as e:
        registrar_log(
          mensaje = f'Error en decorador CBV [{repr(e)}]',
          usuario = 'sistema',
          ip = 'N/A',
          ua = 'N/A',
          modulo = modulo,
          accion = accion,
          nivel = 'error',
          canal = 'app'
        )
      return func(self, *args, **kwargs)
    return wrapper
  return decorador
