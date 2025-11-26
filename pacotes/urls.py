from django.urls import path
from . import views

urlpatterns = [
    path("destinos", views.destinos, name="destinos"),
    path('destinos/editar/<int:destino_id>/', views.editar_destino, name='editar_destino'),
    path("destinos/eliminar/<int:destino_id>/", views.eliminar_destino, name="eliminar_destino"),
    path("pacotes", views.pacotes, name="pacotes"),
    #voos
    path("voos", views.voos, name="voos"),
    path('voos/', views.voos, name='voos'),
    path('voos/<int:voo_id>/', views.voos, name='editar_voo'),
    path('voos/eliminar/<int:voo_id>/', views.eliminar_voo, name='eliminar_voo'),
    #hoteis
    path("hoteis/", views.hotel, name="hoteis"),
    path("hoteis/editar/<int:hotel_id>/", views.editar_hotel, name="editar_hotel"),
    path('hoteis/eliminar/<int:hotel_id>/', views.eliminar_hotel, name='eliminar_hotel'),
    path("hoteis/<int:hotel_id>/selecionar/<int:pacote_id>/", views.selecionar_hotel, name="selecionar_hotel"),
    path("hoteis/<int:hotel_id>/detalhes/", views.hotel_detalhes, name="hotel_detalhes"),
    path("hoteis/<int:hotel_id>/imagem/", views.hotel_imagem, name="hotel_imagem"),
    path("hoteis/<int:hotel_id>/imagem-detalhe/<str:imagem_id>/", views.hotel_imagem_detalhe, name="hotel_imagem_detalhe"),


    
    path('feedbacks/', views.feedbacks, name='feedbacks'),
    path('feedbacks/estatisticas/', views.feedback_estatisticas, name='feedback_estatisticas'),
    path('feedbacks/pacote/<int:pacote_id>/', views.feedbacks_por_pacote, name='feedbacks_por_pacote'),
    path('feedbacks/eliminar/<int:feedback_id>/', views.eliminar_feedback, name='eliminar_feedback'),
    
     # PACOTES
    path('pacotes/', views.pacotes, name='pacotes'),
    path('pacotes/<int:pacote_id>/', views.pacotes, name='editar_pacote'),
    path('pacotes/eliminar/<int:pacote_id>/', views.eliminar_pacote, name='eliminar_pacote'),
    path('pacote/<int:pacote_id>/', views.pacote_detalhes, name='pacote_detalhes'),
    path("pacotes/todos/", views.pacotes_por_pais, name="pacotes_por_pais"),
    path("pacotes-por-pais/", views.pacotes_por_pais, name="pacotes_por_pais"),
    path("<int:pacote_id>/reserva/", views.reserva_pacote, name="reserva_pacote"),

]