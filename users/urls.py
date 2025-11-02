from django.urls import path
from . import views

urlpatterns = [
    path('', views.user, name='user'),
    path('compras/', views.comprasUser, name='comprasUser'),
    path('insert/', views.clientes, name='clientes'),
    path('eliminar/<int:cliente_id>/', views.eliminar_cliente, name='eliminar_cliente'),
]
