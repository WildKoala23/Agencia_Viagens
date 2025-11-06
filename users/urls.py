from django.urls import path
from . import views

urlpatterns = [
    path('', views.user, name='user'),
    path('compras', views.comprasUser, name='comprasUser'),
    path('feedbacks', views.feedbacksUser, name='feedbacksUser'),
    path('perfil', views.perfilUser, name='perfilUser'),
    path('insert', views.inserir_clientes, name='inserir_clientes'),
    path('eliminar/<int:cliente_id>/', views.eliminar_cliente, name='eliminar_cliente'),
    path('login', views.login, name="login")
]
