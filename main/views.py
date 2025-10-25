from django.shortcuts import render, redirect, get_object_or_404
from pacotes.models import *
from pacotes.forms import *
from pagamentos.models import *
from pagamentos.models import *
from users.models import *
from users.models import *

#---------------------------------------------------------------#
def home(request):
    slides = [
        {"image": "https://images.unsplash.com/photo-1506744038136-46273834b3fb",
         "title": "Aventura nas montanhas",
         "text": "Descubra paisagens incríveis ao redor do mundo"},
        {"image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e",
         "title": "Viva o verão",
         "text": "Encontre as melhores praias para relaxar"},
        {"image": "https://images.unsplash.com/photo-1493558103817-58b2924bce98",
         "title": "Explore novos destinos",
         "text": "Momentos inesquecíveis esperam por si"},
    ]
    return render(request, "home.html", {"slides": slides})


def dashboard(request):
    # Buscar pacotes populares
    pacotes = Pacote.objects.all()[:6]  # ou .order_by('-data_inicio')[:6] se quiseres ordenar
    
    context = {
        'proxima_reserva': 'Lisboa 2025',   # depois substituis por dados reais
        'total_reservas': 15,               # idem
        'saldo_creditos': 200.50,
        'ultimas_atividades': 3,
        'pacotes': pacotes,
    }

    return render(request, 'dashboard.html', context)