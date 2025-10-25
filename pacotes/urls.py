from django.urls import path
from . import views

urlpatterns = [
    path("destinos", views.destinos, name="destinos"),
    path("eliminar/<int:destino_id>/", views.eliminar_destino, name="eliminar_destino"),
    path("pacotes", views.pacotes, name="pacotes"),
    path("voos", views.voos, name="voos"),
    path("eliminar/<int:voo_id>/", views.eliminar_voo, name="eliminar_voo"),
    path("hoteis/", views.hotel, name="hoteis"),
]