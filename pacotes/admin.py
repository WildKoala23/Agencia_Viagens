from django.contrib import admin
from .models import (
    Destino, Voo, Hotel, Pacote, Feedback, Reserva,
    PacoteDestino, PacoteHotel, PacoteVoo
)

@admin.register(Destino)
class DestinoAdmin(admin.ModelAdmin):
    list_display = ('destino_id', 'nome', 'pais')
    search_fields = ('nome', 'pais')
    list_filter = ('pais',)


@admin.register(Voo)
class VooAdmin(admin.ModelAdmin):
    list_display = ('voo_id', 'companhia', 'numero_voo', 'origem', 'destino_nome', 'data_saida', 'preco')
    search_fields = ('companhia', 'numero_voo', 'origem', 'destino_nome')
    list_filter = ('companhia', 'data_saida')
    date_hierarchy = 'data_saida'


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('hotel_id', 'nome', 'destino', 'preco_diario')
    search_fields = ('nome', 'endereco')
    list_filter = ('destino',)


@admin.register(Pacote)
class PacoteAdmin(admin.ModelAdmin):
    list_display = ('pacote_id', 'nome', 'data_inicio', 'data_fim', 'preco_total', 'estado')
    search_fields = ('nome', 'descricao_item')
    list_filter = ('estado', 'data_inicio')
    date_hierarchy = 'data_inicio'


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('feedback_id', 'pacote', 'avaliacao', 'data_feedback')
    search_fields = ('comentario', 'pacote__nome')
    list_filter = ('avaliacao', 'data_feedback')
    date_hierarchy = 'data_feedback'
    readonly_fields = ('data_feedback',)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('reserva_id', 'cliente', 'pacote', 'data_inicio', 'data_fim')
    search_fields = ('cliente__nome', 'pacote__nome')
    list_filter = ('data_inicio', 'data_fim')
    date_hierarchy = 'data_inicio'


# Tabelas de relacionamento Many-to-Many
admin.register(PacoteDestino)
admin.register(PacoteHotel)
admin.register(PacoteVoo)
