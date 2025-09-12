from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken


class LoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        tokens = response.data
        print(tokens)
        response.data = {
            "detalle": "Autenticación exitosa",
            "estatus": response.status_code,
            "datos": tokens
        }
        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                "detalle": "Sesión cerrada correctamente",
                "estatus": status.HTTP_205_RESET_CONTENT,
                "datos": {}
            }, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({
                "detalle": "Error al cerrar sesión",
                "estatus": status.HTTP_400_BAD_REQUEST,
                "datos": {"error": str(e)}
            }, status=status.HTTP_400_BAD_REQUEST)