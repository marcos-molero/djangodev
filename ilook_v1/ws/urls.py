from django.urls import path
from rest_framework.routers import DefaultRouter
from ws.views import (
  Ilr001ListView, Ilr001DictView, Ilr001CreateView, Ilr001DetailView, Ilr001UpdateView, Ilr001DeleteView,
  Ilr002ListView, Ilr002CreateView, Ilr002DetailView, Ilr002UpdateView, Ilr002DeleteView,
  Ilm002ListView, Ilm002CreateView, Ilm002DetailView, Ilm002UpdateView, Ilm002DeleteView,
  Ilm003ListView, Ilm003CreateView, Ilm003DetailView, Ilm003UpdateView, Ilm003DeleteView,
  Ilm004ListView, Ilm004CreateView, Ilm004DetailView, Ilm004UpdateView, Ilm004DeleteView,
  TestUpLoadView,
  Ilm006ListView, Ilm006CreateView, Ilm006DetailView, Ilm006UpdateView, Ilm006DeleteView,
  Ilm016ViewSet,
  Ilm027ListView, Ilm027CreateView, Ilm027DetailView, Ilm027UpdateView, Ilm027DeleteView,
  Ilr001ViewSet
)

router = DefaultRouter()
router.register(r'tablas_generales', Ilr001ViewSet, basename='tablas_generales')
router.register(r'reglas_paises', Ilm016ViewSet, basename='reglas_paises')

urlpatterns = [
  path('ilr001/', Ilr001ListView.as_view(), name='listar_ilr001'),
  path('ilr001/dict/<int:tabla_id>/', Ilr001DictView.as_view(), name='dict_ilr001'),
  path('ilr001/crt/', Ilr001CreateView.as_view(), name='crear_ilr001'),
  path('ilr001/<int:tabla_id>/<str:item_id>/', Ilr001DetailView.as_view(), name='detalle_ilr001'),
  path('ilr001/upd/<int:tabla_id>/<str:item_id>/', Ilr001UpdateView.as_view(), name='cambiar_ilr001'),
  path('ilr001/del/<int:tabla_id>/<str:item_id>/', Ilr001DeleteView.as_view(), name='eliminar_ilr001'),

  path('ilr002/', Ilr002ListView.as_view(), name='listar_ilr002'),
  path('ilr002/crt/', Ilr002CreateView.as_view(), name='crear_ilr002'),
  path('ilr002/<int:codigo>/', Ilr002DetailView.as_view(), name='detalle_ilr002'),
  path('ilr002/upd/<int:codigo>/', Ilr002UpdateView.as_view(), name='cambiar_ilr002'),
  path('ilr002/del/<int:codigo>/', Ilr002DeleteView.as_view(), name='eliminar_ilr002'),

  path('ilm002/', Ilm002ListView.as_view(), name='listar_ilm002'),
  path('ilm002/crt/', Ilm002CreateView.as_view(), name='crear_ilm002'),
  path('ilm002/<str:codigo>/', Ilm002DetailView.as_view(), name='detalle_ilm002'),
  path('ilm002/upd/<str:codigo>/', Ilm002UpdateView.as_view(), name='cambiar_ilm002'),
  path('ilm002/del/<str:codigo>/', Ilm002DeleteView.as_view(), name='eliminar_ilm002'),

  path('ilm003/', Ilm003ListView.as_view(), name='listar_ilm003'),  
  path('ilm003/crt/', Ilm003CreateView.as_view(), name='crear_ilm003'),
  path('ilm003/<str:codigo>/', Ilm003DetailView.as_view(), name='detalle_ilm003'),
  path('ilm003/upd/<str:codigo>/', Ilm003UpdateView.as_view(), name='cambiar_ilm003'),
  path('ilm003/del/<str:codigo>/', Ilm003DeleteView.as_view(), name='eliminar_ilm003'),

  path('ilm004/', Ilm004ListView.as_view(), name='listar_ilm004'),  
  path('ilm004/crt/', Ilm004CreateView.as_view(), name='crear_ilm004'),
  path('ilm004/<str:codigo>/', Ilm004DetailView.as_view(), name='detalle_ilm004'),
  path('ilm004/upd/<str:codigo>/', Ilm004UpdateView.as_view(), name='cambiar_ilm004'),
  path('ilm004/del/<str:codigo>/', Ilm004DeleteView.as_view(), name='eliminar_ilm004'),

  path('test/upload/', TestUpLoadView.as_view(), name='test'),

  path('ilm006/', Ilm006ListView.as_view(), name='listar_ilm006'),
  path('ilm006/crt/', Ilm006CreateView.as_view(), name='crear_ilm006'),
  path('ilm006/<int:codigo>/', Ilm006DetailView.as_view(), name='detalle_ilm006'),
  path('ilm006/upd/<int:codigo>/', Ilm006UpdateView.as_view(), name='cambiar_ilm006'),
  path('ilm006/del/<int:codigo>/', Ilm006DeleteView.as_view(), name='eliminar_ilm006'),

  path('ilm027/', Ilm027ListView.as_view(), name='listar_ilm027'),
  path('ilm027/crt/', Ilm027CreateView.as_view(), name='crear_ilm027'),
  path('ilm027/<int:codigo_id>/', Ilm027DetailView.as_view(), name='detalle_ilm027'),
  path('ilm027/<int:codigo_id>/<int:secuencia_id>/', Ilm027DetailView.as_view(), name='detalle_ilm027'),
  path('ilm027/upd/<int:codigo_id>/<int:secuencia_id>/', Ilm027UpdateView.as_view(), name='cambiar_ilm027'),
  path('ilm027/del/<int:codigo_id>/<int:secuencia_id>/', Ilm027DeleteView.as_view(), name='eliminar_ilm027'),

  path(
    'reglas_paises/<int:regla_id>/<str:pais_id>/',
    Ilm016ViewSet.as_view({
      'get': 'retrieve',
      'put': 'update',
      'delete': 'destroy'
    }),
    name='detalle_regla_pais'
  ),

  ] + router.urls
