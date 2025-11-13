from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.user, name='user'),
    path('compras', views.comprasUser, name='comprasUser'),
    path('feedbacks', views.feedbacksUser, name='feedbacksUser'),
    path('perfil', views.perfilUser, name='perfilUser'),
    path('insert', views.inserir_clientes, name='inserir_clientes'),
    path('editar/<int:cliente_id>/', views.editar_cliente, name='editar_cliente'),
    path('eliminar/<int:cliente_id>/', views.eliminar_cliente, name='eliminar_cliente'),
    path('login/', views.loginUser, name="login"),
    path('logout/', LogoutView.as_view(), name='logout'),
]
