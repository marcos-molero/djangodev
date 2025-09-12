"""
URL configuration for imed_v1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import (
  PacienteViewSet, AlergiaViewSet, PatologiaViewSet, AntecedenteViewSet, ContactoPacienteViewSet,
  FichaPacienteViewSet)
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'pacientes', PacienteViewSet, basename='paciente')
router.register(r'alergias', AlergiaViewSet, basename='alergia')
router.register(r'patologias', PatologiaViewSet, basename='patologia')
router.register(r'antecedentes', AntecedenteViewSet, basename='antecedente')
router.register(r'contactos', ContactoPacienteViewSet, basename='contacto')
router.register(r'fichas', FichaPacienteViewSet, basename='ficha')

urlpatterns = router.urls