from django.urls import path
from . import views

urlpatterns = [
    # Pagamentos
    path('pagamentos/', views.pagamentos, name='pagamentos'),
    
    # Faturas
    path('faturas/', views.faturas, name='faturas'),
]
