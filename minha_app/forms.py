from django import forms
from .models import Cliente, Destino, Voo, Hotel,Pacote, Feedback, Reserva, Pagamento,Fatura

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
   
   
class DestinoForm(forms.ModelForm):
    class Meta:
        model = Destino
        fields = '__all__'

class VooForm(forms.ModelForm):
    class Meta:
        model = Voo
        fields = '__all__'
        labels = {
            'data_voo': 'Data do Voo (0000-00-00)',
            'hora_partida': 'Hora de Partida(00:00)',
            'hora_chegada': 'Hora de Chegada(00:00)',
            'duracao': 'Duração',
            'origem': 'Local de Origem',
            'porta_embarque': 'Porta de Embarque',
        }


class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel 
        fields = '__all__'
        labels = {
            'nome': 'Nome do Hotel',
            'morada': 'Morada',
        }


class PacoteForm(forms.ModelForm):
    class Meta:
        model = Pacote
        fields = '__all__'
        labels = {
            'preco': 'Preço',
            'descricao': 'Descrição',
            'destino': 'Destino',
            'voo': 'Voo',
            'hotel': 'Hotel',
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = '__all__'
        labels = {
            'data_feedback': 'Data do Feedback (0000-00-00)',
            'avaliacao': 'Avaliação de 0 a 5',
            'comentario': 'Comentário',
            'cliente': 'Cliente',
            'pacote': 'Pacote',
        }

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = '__all__'
        labels = {
            'data_inicio': 'Data de Início (0000-00-00)',
            'data_fim': 'Data de Fim (0000-00-00)',
            'cliente': 'Cliente',
            'pacote': 'Pacote',
        }

        

class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = '__all__'
        labels = {
            'data_pagamento': 'Data do Pagamento(0000-00-00)',
            'montante': 'Montante (€)',
            'reserva': 'Reserva',
        }

class FaturaForm(forms.ModelForm):
    class Meta:
        model = Fatura
        fields = '__all__'
        labels = {
            'data_emissao': 'Data de Emissão(0000-00-00)',
            'valor_total': 'Valor Total (€)',
            'pagamento': 'Pagamento',
        }