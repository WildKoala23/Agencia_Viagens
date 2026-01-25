from django import forms
from .models import Utilizador
from django.contrib.auth.forms import UserCreationForm


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



class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label='Email',
        max_length=150,
        widget=forms.EmailInput(attrs={'placeholder': 'Email'})
    )
    first_name = forms.CharField(
        label='Nome',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Nome'})
    )
    last_name = forms.CharField(
        label='Apelido',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Apelido'})
    )

    class Meta:
        model = Utilizador
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']

