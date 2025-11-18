from django.urls import path
from . import views

urlpatterns = [
  path('pagamentos', views.pagamentos, name='pagamentos'),
  path('faturas', views.faturas, name='faturas'),
]