from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import AccessTokenOnlySerializer


class LoginView(TokenObtainPairView):
    serializer_class = AccessTokenOnlySerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Aquí podrías registrar el logout en la base de datos si lo deseas
        return Response({"detalle": "Sesión cerrada correctamente."}, status=status.HTTP_200_OK)