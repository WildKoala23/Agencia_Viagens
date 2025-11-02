from django.urls import path
from . import views

urlpatterns = [
  path('pagamentos', views.pagamentos, name='pagamentos'),
  path('faturas', views.faturas, name='faturas'),
  path('faturas/<int:fatura_id>/', views.fatura_detalhes, name='fatura_detalhes'),
]