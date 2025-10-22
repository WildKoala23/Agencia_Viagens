from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from minha_app import views

urlpatterns = [
  path('', views.home, name='home'),
  path('clientes/', views.clientes, name='clientes'),
  path('clientes/eliminar/<int:cliente_id>/', views.eliminar_cliente, name='eliminar_cliente'),
  path('destinos/', views.destinos, name='destinos'),
  path('destinos/eliminar/<int:destino_id>/', views.eliminar_destino, name='eliminar_destino'),
  path('voos/', views.voos, name='voos'),
  #path('voos/eliminar/<int:voo_id>', views.eliminar_voos, name='eliminar_voo'),
  # path('hoteis/', views.hotel, name='hoteis'),
  path('pacotes/', views.pacotes, name='pacotes'),
  path('feedbacks/', views.feedbacks, name='feedbacks'),
  # path('reservas/', views.reservas, name='reservas'),
  path('pagamentos/', views.pagamentos, name='pagamentos'),
  path('faturas/', views.faturas, name='faturas'),
]