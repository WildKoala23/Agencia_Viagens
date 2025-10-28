from django.urls import path
from . import views

urlpatterns = [
  path('clientes/', views.clientes, name='clientes'),
  path("clientes/eliminar/<int:cliente_id>/", views.eliminar_cliente, name="eliminar_cliente"),
  path('feedbacks/', views.feedbacks, name='feedbacks'),
]