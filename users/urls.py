from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.user, name='user'),
    path('api/pacotes_por_pais/', views.api_pacotes_por_pais, name='api_pacotes_por_pais'),
    path('pacotes_por_pais', views.api_pacotes_por_pais, name='pacotes_por_pais'),
    path('compras', views.comprasUser, name='comprasUser'),
    path('feedbacks', views.feedbacksUser, name='feedbacksUser'),
    path('perfil', views.perfilUser, name='perfilUser'),
    path('insert', views.inserir_clientes, name='inserir_clientes'),
    path('editar/<int:cliente_id>/', views.editar_cliente, name='editar_cliente'),
    path('eliminar/<int:cliente_id>/', views.eliminar_cliente, name='eliminar_cliente'),
    path('login/', views.loginUser, name="login"),
    path('register/', views.registerUser, name="register"),
    path('logout/', LogoutView.as_view(), name='logout'),
]
