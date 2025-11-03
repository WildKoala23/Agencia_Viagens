from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from .forms import *
from django.db.models import Q

# Create your views here.

def destinos(request):
    if request.method == "POST":
        form = DestinoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('destinos')
    else:
        form = DestinoForm()

    destinos = Destino.objects.all()
    return render(request, 'destinos.html', {
        'form': form,
        'destinos': destinos
    })

def eliminar_destino(request, destino_id):
    destino = get_object_or_404(Destino, destino_id=destino_id)
    if request.method == 'POST':
        destino.delete()
        return redirect('destinos')
    return redirect('destinos')

def feedbacks(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('feedbacks')
    else:
        form = FeedbackForm()

    # Buscar feedbacks usando a VIEW criada na BD (SQL DIRETO - SUA PARTE)
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM view_feedbacks_completos")
        columns = [col[0] for col in cursor.description]
        feedbacks = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return render(request, 'feedbacks.html', {
        'form': form,
        'feedbacks': feedbacks
    })


def feedback_estatisticas(request):
    """
    Mostra estatísticas gerais de feedbacks e avaliações de pacotes
    (SQL DIRETO - SUA PARTE - usando FUNCTIONs e VIEWs da BD)
    """
    with connection.cursor() as cursor:
        # Estatísticas gerais
        cursor.execute("SELECT * FROM get_estatisticas_feedbacks()")
        columns = [col[0] for col in cursor.description]
        result = cursor.fetchone()
        estatisticas_gerais = dict(zip(columns, result)) if result else {}
        
        # Calcular percentagens para as barras de progresso
        if estatisticas_gerais and estatisticas_gerais.get('total_feedbacks', 0) > 0:
            total = estatisticas_gerais['total_feedbacks']
            estatisticas_gerais['percentual_5_estrelas'] = round((estatisticas_gerais['total_5_estrelas'] / total) * 100, 1)
            estatisticas_gerais['percentual_4_estrelas'] = round((estatisticas_gerais['total_4_estrelas'] / total) * 100, 1)
            estatisticas_gerais['percentual_3_estrelas'] = round((estatisticas_gerais['total_3_estrelas'] / total) * 100, 1)
            estatisticas_gerais['percentual_2_estrelas'] = round((estatisticas_gerais['total_2_estrelas'] / total) * 100, 1)
            estatisticas_gerais['percentual_1_estrela'] = round((estatisticas_gerais['total_1_estrela'] / total) * 100, 1)
        else:
            estatisticas_gerais['percentual_5_estrelas'] = 0
            estatisticas_gerais['percentual_4_estrelas'] = 0
            estatisticas_gerais['percentual_3_estrelas'] = 0
            estatisticas_gerais['percentual_2_estrelas'] = 0
            estatisticas_gerais['percentual_1_estrela'] = 0
        
        # Top pacotes avaliados
        cursor.execute("SELECT * FROM get_top_pacotes_avaliados(10)")
        columns = [col[0] for col in cursor.description]
        top_pacotes = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Estatísticas por pacote
        cursor.execute("SELECT * FROM view_estatisticas_pacotes")
        columns = [col[0] for col in cursor.description]
        estatisticas_pacotes = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return render(request, 'feedback_estatisticas.html', {
        'estatisticas_gerais': estatisticas_gerais,
        'top_pacotes': top_pacotes,
        'estatisticas_pacotes': estatisticas_pacotes
    })


def voos(request, voo_id=None):
    # Se for edição, carrega o voo
    if voo_id:
        voo = get_object_or_404(Voo, voo_id=voo_id)
    else:
        voo = None

    # Guardar voo (POST)
    if request.method == "POST":
        form = VooForm(request.POST, instance=voo)
        if form.is_valid():
            form.save()
            return redirect('voos')
    else:
        form = VooForm(instance=voo)

    # ---  PESQUISA ---
    if q := request.GET.get("q"):
        voos = Voo.objects.filter(
            Q(destino__nome__icontains=q) |
            Q(companhia__icontains=q)
        )
    else:
        voos = Voo.objects.all()
    # ---  FIM DA PESQUISA ---

    return render(request, 'voos.html', {
        'form': form,
        'voos': voos,
        'voo_editar': voo,
    })


def eliminar_voo(request, voo_id):
    voo = get_object_or_404(Voo, voo_id=voo_id)
    if request.method == 'POST':
        voo.delete()
    return redirect('voos')

def hotel(request):
    if request.method == "POST":
        form = HotelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('hoteis')
    else:
        form = HotelForm()

    hoteis = Hotel.objects.all()
    return render(request, 'hoteis.html', {
        'form': form,
        'hoteis': hoteis
    })

def editar_hotel(request, hotel_id):
    """Editar um hotel existente"""
    hotel = get_object_or_404(Hotel, hotel_id=hotel_id)

    if request.method == "POST":
        form = HotelForm(request.POST, instance=hotel)
        if form.is_valid():
            form.save()
            return redirect('hoteis')
    else:
        form = HotelForm(instance=hotel)

    return render(request, 'editar_hotel.html', {
        'form': form,
        'hotel': hotel
    })

def eliminar_hotel(request, hotel_id):
    hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
    if request.method == 'POST':
        hotel.delete()
        return redirect('hoteis')
    return redirect('hoteis')


def pacotes(request):
    if request.method == "POST":
        form = PacoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pacotes')
    else:
        form = PacoteForm()

    # Buscar pacotes sem select_related para evitar problemas de cursor
    pacotes = list(Pacote.objects.all().values(
        'pacote_id', 'nome', 'descricao_item', 
        'data_inicio', 'data_fim', 'preco_total', 'estado'
    ))
    
    return render(request, 'pacotes.html', {
        'form': form,
        'pacotes': pacotes
    })