from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboardUser, name='user'),
    path('compras', views.comprasUser, name='comprasUser'),
    path('feedbacks', views.feedbacksUser, name='feedbacksUser'),
    path('insert', views.inserir_clientes, name='inserir_clientes'),
    path('eliminar/<int:cliente_id>/', views.eliminar_cliente, name='eliminar_cliente'),
]
