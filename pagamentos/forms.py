from django import forms
from .models import Pagamento, Factura, FacturaLinha, Compra


class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = '__all__'
        labels = {
            'user': 'Utilizador',
            'data_compra': 'Data da Compra',
            'valor_total': 'Valor Total (€)',
        }
        widgets = {
            'data_compra': forms.DateInput(attrs={'type': 'date'}),
        }


class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = '__all__'
        labels = {
            'compra': 'Compra',
            'data_pagamento': 'Data do Pagamento',
            'valor': 'Valor (€)',
            'estado': 'Estado',
            'metodo': 'Método de Pagamento',
        }
        widgets = {
            'data_pagamento': forms.DateInput(attrs={'type': 'date'}),
            'estado': forms.Select(choices=[
                ('', 'Selecione...'),
                ('PENDENTE', 'Pendente'),
                ('PAGO', 'Pago'),
                ('CANCELADO', 'Cancelado'),
            ]),
            'metodo': forms.Select(choices=[
                ('', 'Selecione...'),
                ('CARTAO_CREDITO', 'Cartão de Crédito'),
                ('CARTAO_DEBITO', 'Cartão de Débito'),
                ('TRANSFERENCIA', 'Transferência Bancária'),
                ('MULTIBANCO', 'Multibanco'),
                ('MBWAY', 'MB WAY'),
            ]),
        }


class FacturaLinhaForm(forms.ModelForm):
    class Meta:
        model = FacturaLinha
        fields = '__all__'
        labels = {
            'descricao': 'Descrição',
            'quantidade': 'Quantidade',
            'preco_unitario': 'Preço Unitário (€)',
        }
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }


class FaturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = '__all__'
        labels = {
            'compra': 'Compra',
            'pagamento': 'Pagamento',
            'data_emissao': 'Hora de Emissão',
            'valor_total': 'Valor Total (€)',
        }
        widgets = {
            'data_emissao': forms.TimeInput(attrs={'type': 'time'}),
        }