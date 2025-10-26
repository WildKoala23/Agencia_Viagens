from django.urls import path
from . import views

urlpatterns = [
    path("destinos", views.destinos, name="destinos"),
    path("eliminar/<int:destino_id>/", views.eliminar_destino, name="eliminar_destino"),
    path("pacotes", views.pacotes, name="pacotes"),
    #voos
    path("voos", views.voos, name="voos"),
    path('voos/', views.voos, name='voos'),
    path('voos/<int:voo_id>/', views.voos, name='editar_voo'),
    path('voos/eliminar/<int:voo_id>/', views.eliminar_voo, name='eliminar_voo'),
    #------
    path("hoteis/", views.hotel, name="hoteis"),
    path("hoteis/eliminar/<int:hotel_id>/", views.eliminar_hotel, name="eliminar_hotel"),
    
]