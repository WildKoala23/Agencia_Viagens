from django.urls import path
from . import views

urlpatterns = [
    path("destinos", views.destinos, name="destinos"),
    path("eliminar/<int:destino_id>/", views.eliminar_destino, name="eliminar_destino"),
]