"""
URL configuration for ilook_v1 project.

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
  CargarTransaccionesISOView, 
  EjecutarValidacionesISOView, 
  CargarTransaccionesLK1View,
  EjecutarValidacionesLK1View,
  LoteLK1ResumenView,
)

urlpatterns = [
    path('iso/cargar/', CargarTransaccionesISOView.as_view(), name='iso-cargar'),
    path('iso/ejecutar/', EjecutarValidacionesISOView.as_view(), name='iso-ejecutar'),
    path('lk1/cargar/', CargarTransaccionesLK1View.as_view(), name='lk1-cargar'),
    path('lk1/ejecutar/', EjecutarValidacionesLK1View.as_view(), name='lk1-ejecutar'),
    path('lk1/lotes/', LoteLK1ResumenView.as_view(), name='lk1-lotes'),
]
