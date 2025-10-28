from django import forms
from .models import Utilizador

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Utilizador
        fields = '__all__'
   

