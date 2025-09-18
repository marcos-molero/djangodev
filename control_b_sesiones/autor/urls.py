from django.urls import path, include
from autor.views import AutorViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'autores', AutorViewSet, basename='autor')

urlpatterns = [
    path('', include(router.urls)),
]
