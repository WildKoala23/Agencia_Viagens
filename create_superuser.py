import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agenciaviagens.settings')
django.setup()

from users.models import Utilizador

# Criar superuser
email = input('Email: ')
password = input('Password: ')

# Verificar se já existe
if Utilizador.objects.filter(email=email).exists():
    print(f'Usuário {email} já existe!')
else:
    user = Utilizador.objects.create(
        email=email,
        username=email,  # Usar email como username
        is_superuser=True,
        is_staff=True,
        is_active=True
    )
    user.set_password(password)
    user.save()
    print(f'\n✓ Superuser criado com sucesso!')
    print(f'Email: {email}')
