from django.shortcuts import render, redirect, get_object_or_404
from .forms import *

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



def voos(request, voo_id=None):
    # Se for edição, carrega o voo
    if voo_id:
        voo = get_object_or_404(Voo, voo_id=voo_id)
    else:
        voo = None

    if request.method == "POST":
        form = VooForm(request.POST, instance=voo)
        if form.is_valid():
            form.save()
            return redirect('voos')
    else:
        form = VooForm(instance=voo)

    voos = Voo.objects.all()
    return render(request, 'voos.html', {
        'form': form,
        'voos': voos,
        'voo_editar': voo
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