from rest_framework.response import Response

def respuesta_json(detalle: str, codigo: int, datos: dict = None):
    """
    Construye una respuesta estándar para la API.

    Args:
        detalle (str): Mensaje descriptivo.
        codigo (int): Código de estado personalizado.
        datos (dict, opcional): Datos adicionales a incluir.

    Returns:
        Response: Objeto de respuesta DRF.
    """
    return Response({
        "detalle": detalle,
        "codigo": codigo,
        "datos": datos or {}
    }, status=codigo)