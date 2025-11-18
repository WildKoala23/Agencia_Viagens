from django import forms
from .models import Destino, Voo, Hotel, Pacote, Feedback
from django.forms import DateTimeInput


class DestinoForm(forms.ModelForm):
    class Meta:
        model = Destino
        exclude = ['destino_id'] 

class VooForm(forms.ModelForm):
    class Meta:
        model = Voo
        fields = ['destino', 'companhia', 'numero_voo', 'data_saida', 'data_chegada', 'preco']
        labels = {
            'companhia': 'Companhia Aérea',
            'numero_voo': 'Número do Voo',
            'data_saida': 'Data de Saída (AAAA-MM-DD HH:MM)',
            'data_chegada': 'Data de Chegada (AAAA-MM-DD HH:MM)',
            'preco': 'Preço (€)',
            'destino': 'Destino',
        }
        widgets = {
            'data_saida': DateTimeInput(attrs={'type': 'datetime-local'}),
            'data_chegada': DateTimeInput(attrs={'type': 'datetime-local'}),
            'companhia': forms.TextInput(attrs={'style': 'resize:none;'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

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
    imagem = forms.ImageField(
    required=False,
    label="Imagem do Pacote",
    widget=forms.FileInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Pacote
        fields = ['nome', 'descricao_item', 'data_inicio', 'data_fim', 'preco_total', 'estado_id', 'imagem', 'destinos']
        labels = {
            'nome': 'Nome do Pacote',
            'descricao_item': 'Descrição',
            'data_inicio': 'Data de Início (AAAA-MM-DD)',
            'data_fim': 'Data de Fim (AAAA-MM-DD)',
            'preco_total': 'Preço Total (€)',
            'estado_id': 'Estado',
            'imagem': 'Imagem do Pacote',
            'destinos': 'Destinos',
        }
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
            'destinos': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['destinos'].required = True  
        self.fields['destinos'].help_text = "Selecione pelo menos um destino."


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
        self.save_m2m()

     return instance


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = '__all__'
        labels = {
            'pacote': 'Pacote',
            'avaliacao': 'Avaliação (1-5)',
            'comentario': 'Comentário',
            'data_feedback': 'Data do Feedback (AAAA-MM-DD)',
        }
