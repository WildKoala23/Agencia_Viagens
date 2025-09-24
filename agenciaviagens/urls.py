from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from minha_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('clientes/', views.listar_clientes, name='listar_clientes'),
    path('inserir_cliente/', views.inserir_cliente, name='inserir_cliente'),

    # redireciona "/" para "/clientes/"
    path('', RedirectView.as_view(url='/clientes/', permanent=False)),
]