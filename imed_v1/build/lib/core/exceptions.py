from rest_framework.views import exception_handler

def imed_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        detalle = response.data.get("detail", "Error inesperado")
        estatus = response.status_code
        datos = {k: v for k, v in response.data.items() if k != "detail"}

        response.data = {
            "detalle": detalle,
            "estatus": estatus,
            "datos": datos
        }

    return response