from django import forms
from .models import Utilizador

class ClienteForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=True, label='Password')
    
    class Meta:
        model = Utilizador
        fields = ['email', 'first_name', 'last_name', 'telefone', 'password']
        labels = {
            'email': 'Email',
            'first_name': 'Primeiro Nome',
            'last_name': 'Último Nome',
            'telefone': 'Telefone',
        }
   
class EditClienteForm(forms.ModelForm):
    # Do not include password in the edit form — password cannot be changed here
    class Meta:
        model = Utilizador
        fields = ['email', 'first_name', 'last_name', 'telefone']
        labels = {
            'email': 'Email',
            'first_name': 'Primeiro Nome',
            'last_name': 'Último Nome',
            'telefone': 'Telefone',
        }
   
class LoginForm(forms.Form):
    email = forms.CharField(label='User email', max_length=150)
    password = forms.CharField(label='Password', max_length=50, widget=forms.PasswordInput)

    class Meta:
        model = Utilizador
        fields = ['email', 'password']
