from django import forms
from .models import Pagamento, Factura


METODOS_PAGAMENTO = [
    ('mbway', 'MBWay'),
    ('cartao_credito', 'Cartão de Crédito'),
]


class MetodoPagamentoForm(forms.Form):
    metodo = forms.ChoiceField(
        choices=METODOS_PAGAMENTO,
        widget=forms.RadioSelect,
        label='Selecione o método de pagamento',
        required=True
    )
    
    # Campos específicos para cada método
    # MBWay
    mbway_telefone = forms.CharField(
        max_length=9,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': '912345678',
            'class': 'form-control'
        }),
        label='Número de telemóvel'
    )
    
    # Cartão de Crédito
    cartao_numero = forms.CharField(
        max_length=16,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': '1234 5678 9012 3456',
            'class': 'form-control'
        }),
        label='Número do cartão'
    )
    cartao_nome = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nome como aparece no cartão',
            'class': 'form-control'
        }),
        label='Nome no cartão'
    )
    cartao_validade = forms.CharField(
        max_length=5,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'MM/AA',
            'class': 'form-control'
        }),
        label='Data de validade'
    )
    cartao_cvv = forms.CharField(
        max_length=3,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': '123',
            'class': 'form-control',
            'type': 'password'
        }),
        label='CVV'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        metodo = cleaned_data.get('metodo')
        
        # Validar campos específicos baseado no método escolhido(ver se da para usar com views)
        if metodo == 'mbway':
            telefone = cleaned_data.get('mbway_telefone')
            if telefone:
                # Apenas valida se foi preenchido
                if len(telefone) != 9 or not telefone.isdigit():
                    self.add_error('mbway_telefone', 'Número de telemóvel deve ter 9 dígitos')
        
        elif metodo == 'cartao_credito':
            # Validar apenas se foi preenchido
            numero = cleaned_data.get('cartao_numero')
            if numero and (len(numero.replace(' ', '')) < 13 or len(numero.replace(' ', '')) > 19):
                self.add_error('cartao_numero', 'Número de cartão inválido')
            
            cvv = cleaned_data.get('cartao_cvv')
            if cvv and (len(cvv) < 3 or len(cvv) > 4):
                self.add_error('cartao_cvv', 'CVV deve ter 3 ou 4 dígitos')
        
        return cleaned_data


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