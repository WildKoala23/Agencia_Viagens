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

    # 🔹 Busca todos os pacotes ativos
    pacotes = Pacote.objects.filter(estado="Ativo")

    context = {
        "slides": slides,
        "pacotes": pacotes,
    }

    return render(request, "home.html", context)


def dashboard(request):
    pacotes = Pacote.objects.all()
    total_feedbacks = Feedback.objects.count()

    context = {
        'visita_site': '2345',  
        'total_reservas': 15,
        'lucro_total': 200.50,
        'ultimos_feeds': total_feedbacks, 
        'pacotes': pacotes,
    }
    return render(request, 'dashboard.html', context)
