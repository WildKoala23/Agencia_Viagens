from django import forms
from .models import Destino, Voo, Hotel, Pacote

class DestinoForm(forms.ModelForm):
    class Meta:
        model = Destino
        fields = '__all__'

class VooForm(forms.ModelForm):
    destino_nome = forms.ModelChoiceField(
        queryset=Destino.objects.all(),
        label="Destino",
        empty_label="Selecione um destino",
        to_field_name="nome",
    )

    class Meta:
        model = Voo
        fields = ['destino_nome','companhia','numero_voo','data_saida','data_chegada','origem','destino','preco']
        labels = {
            'companhia': 'Companhia Aérea',
            'numero_voo': 'Número do Voo',
            'data_saida': 'Data de Saída (AAAA-MM-DD)',
            'data_chegada': 'Data de Chegada (AAAA-MM-DD)',
            'origem': 'Origem (Aeroporto de Partida)',
            'destino': 'Destino (Aeroporto de Chegada)',
            'preco': 'Preço (€)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and getattr(self.instance, "destino_id", None):
            try:
                self.fields["destino_nome"].initial = Destino.objects.get(pk=self.instance.destino_id)
            except Destino.DoesNotExist:
                pass 

    def save(self, commit=True):
        voo = super().save(commit=False)
        destino_selecionado = self.cleaned_data.get('destino_nome')
        if destino_selecionado:
            voo.destino_id = destino_selecionado.pk
        if commit:
            voo.save()
        return voo
     
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