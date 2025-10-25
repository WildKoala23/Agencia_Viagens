from django import forms
from .models import Destino, Voo, Hotel, Pacote

class DestinoForm(forms.ModelForm):
    class Meta:
        model = Destino
        fields = '__all__'

class VooForm(forms.ModelForm):
    class Meta:
        model = Voo
        fields = ['destino_id', 'companhia', 'numero_voo', 'data_saida', 'data_chegada', 'origem', 'destino', 'preco']
        labels = {
            'destino_id': 'ID do Destino',
            'companhia': 'Companhia Aérea',
            'numero_voo': 'Número do Voo',
            'data_saida': 'Data de Saída (AAAA-MM-DD)',
            'data_chegada': 'Data de Chegada (AAAA-MM-DD)',
            'origem': 'Origem',
            'destino': 'Destino',
            'preco': 'Preço (€)',
        }

class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = '__all__'
        labels = {
            'nome': 'Nome do Hotel',
            'endereco': 'Endereço',
        }

class PacoteForm(forms.ModelForm):
    fatura_linha_id = forms.IntegerField(label='ID da Linha de Fatura', required=False)
    
    class Meta:
        model = Pacote
        fields = ['nome', 'descricao_item', 'data_inicio', 'data_fim', 'preco_total', 'estado']
        labels = {
            'nome': 'Nome do Pacote',
            'descricao_item': 'Descrição',
            'data_inicio': 'Data de Início (AAAA-MM-DD)',
            'data_fim': 'Data de Fim (AAAA-MM-DD)',
            'preco_total': 'Preço Total (€)',
            'estado': 'Estado',
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('fatura_linha_id'):
            from .models import FacturaLinha
            try:
                instance.fatura_linha_id = self.cleaned_data['fatura_linha_id']
            except:
                pass
        if commit:
            instance.save()
        return instance