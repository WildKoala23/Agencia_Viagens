from django.urls import path
from . import views

urlpatterns = [
  path('pagamentos', views.pagamentos, name='pagamentos'),
  path('faturas', views.faturas, name='faturas'),
  path('faturas/criar-completa/', views.criar_fatura_completa, name='criar_fatura_completa'),
  path('faturas/editar/<int:fatura_id>/', views.editar_fatura, name='editar_fatura'),
  path('faturas/eliminar/<int:fatura_id>/', views.eliminar_fatura, name='eliminar_fatura'),
  path('faturas/atualizar-total/<int:fatura_id>/', views.atualizar_total_fatura, name='atualizar_total_fatura'),
  path('faturas/<int:fatura_id>/adicionar-linha/', views.adicionar_linha_fatura, name='adicionar_linha_fatura'),
]
