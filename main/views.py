from django.shortcuts import render, redirect, get_object_or_404
from pacotes.models import *
from pacotes.forms import *
from pagamentos.models import *
from users.models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

#---------------------------------------------------------------#
def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('main:dashboard')  # Admin dashboard
        elif Group.objects.filter(name='Users', user=request.user).exists():
            return redirect('users:dashboardUser')  # User dashboard
    return render(request, "home.html", {  # Visitor
        "slides": [
            {"image": "https://images.unsplash.com/photo-1506744038136-46273834b3fb",
             "title": "Aventura nas montanhas",
             "text": "Descubra paisagens incríveis ao redor do mundo"},
            {"image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e",
             "title": "Viva o verão",
             "text": "Encontre as melhores praias para relaxar"},
            {"image": "https://images.unsplash.com/photo-1493558103817-58b2924bce98",
             "title": "Explore novos destinos",
             "text": "Momentos inesquecíveis esperam por si"},
        ],
        "pacotes": Pacote.objects.filter(estado_id=1),
    })

