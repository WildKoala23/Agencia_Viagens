from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from minha_app import views

urlpatterns = [
  path('', views.home, name='home'),
  path('clientes/', views.clientes, name='clientes'),
  path('destinos/', views.destinos, name='destinos'),
  path('voos/', views.voos, name='voos'),
  path('hoteis/', views.hotéis, name='hoteis'),
  path('pacotes/', views.pacotes, name='pacotes'),
  path('feedbacks/', views.feedbacks, name='feedbacks'),
  path('reservas/', views.reservas, name='reservas'),
  path('pagamentos/', views.pagamentos, name='pagamentos'),
  path('faturas/', views.faturas, name='faturas'),
]