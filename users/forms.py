from django import forms
from .models import Utilizador

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Utilizador
        fields = '__all__'
   
class LoginForm(forms.ModelForm):
    email = forms.CharField(label='User email', max_length=150)
    password = forms.CharField(label='Password', max_length=50, widget=forms.PasswordInput)

    class Meta:
        model = Utilizador
        fields = ['email', 'password']
