from django import forms
from .models import Pagamento, Factura


class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = '__all__'
        labels = {
            'compra_id': 'ID da Compra',
            'data_pagamento': 'Data do Pagamento (AAAA-MM-DD)',
            'valor': 'Valor (€)',
            'estado': 'Estado',
            'metodo': 'Método de Pagamento',
        }

class FaturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = '__all__'
        labels = {
            'compra_id': 'ID da Compra',
            'pagamento_id': 'ID do Pagamento',
            'data_emissao': 'Data/Hora de Emissão',
            'valor_total': 'Valor Total (€)',
        }