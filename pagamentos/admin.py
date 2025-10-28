from django.contrib import admin
from .models import Compra, Pagamento, Factura, FacturaLinha


@admin.register(FacturaLinha)
class FacturaLinhaAdmin(admin.ModelAdmin):
    list_display = ('fatura_linha_id', 'descricao', 'quantidade', 'preco_unitario')
    search_fields = ('descricao',)


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('compra_id', 'user', 'data_compra', 'valor_total')
    search_fields = ('user__nome', 'user__email')
    list_filter = ('data_compra',)
    date_hierarchy = 'data_compra'


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('pagamento_id', 'compra', 'valor', 'estado', 'metodo', 'data_pagamento')
    search_fields = ('compra__user__nome', 'estado', 'metodo')
    list_filter = ('estado', 'metodo', 'data_pagamento')
    date_hierarchy = 'data_pagamento'


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('fatura_id', 'compra', 'pagamento', 'valor_total', 'data_emissao')
    search_fields = ('compra__user__nome',)
    list_filter = ('data_emissao',)
    readonly_fields = ('data_emissao',)
