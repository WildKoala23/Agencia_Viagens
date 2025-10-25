from django import forms
from .models import Utilizador, Feedback

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Utilizador
        fields = '__all__'
   

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
