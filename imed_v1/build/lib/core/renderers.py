from rest_framework.renderers import JSONRenderer

class IMEDRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response", None)
        status_code = response.status_code if response else 200

        detalle = data.pop("detalle", "Operación exitosa")
        estatus = data.pop("estatus", status_code)
        datos = data

        return super().render({
            "detalle": detalle,
            "estatus": estatus,
            "datos": datos
        }, accepted_media_type, renderer_context)