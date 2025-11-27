from django.urls import path
from . import views

urlpatterns = [
  path('pagamentos', views.pagamentos, name='pagamentos'),
  path('faturas', views.faturas, name='faturas'),
  path('processar-pagamento/<int:pacote_id>/<int:hotel_id>/<int:voo_id>/', views.processar_pagamento, name='processar_pagamento'),
  path('compra-sucesso/<int:compra_id>/', views.compra_sucesso, name='compra_sucesso'),
]