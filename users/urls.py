from django.urls import path
from . import views

urlpatterns = [
    path('', views.user, name='user'),
    path('clientes/', views.clientes, name='clientes'),
    path("clientes/eliminar/<int:cliente_id>/", views.eliminar_cliente, name="eliminar_cliente"),
    path('feedbacks/', views.feedbacks, name='feedbacks'),
    path('feedbacks/editar/<int:feedback_id>/', views.editar_feedback, name='editar_feedback'),
    path('feedbacks/eliminar/<int:feedback_id>/', views.eliminar_feedback, name='eliminar_feedback'),
]
