from django.shortcuts import render, redirect, get_object_or_404
from .models import Utilizador, Destino, Voo, Hotel, Pacote, Feedback, Pagamento, Factura
from .forms import ClienteForm, DestinoForm,VooForm,HotelForm, PacoteForm, FeedbackForm, PagamentoForm, FaturaForm

#---------------------------------------------------------------#
def home(request):
    return render(request, 'home.html')
#---------------------------------------------------------------#

def clientes(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('clientes')
    else:
        form = ClienteForm()

    clientes = Utilizador.objects.all()
    return render(request, 'clientes.html', {
        'form': form,
        'clientes': clientes
    })

def eliminar_cliente(request, cliente_id):
    cliente = get_object_or_404(Utilizador, user_id=cliente_id)
    if request.method == 'POST':
        cliente.delete()
        return redirect('clientes')
    return redirect('clientes')

#---------------------------------------------------------------#

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

#---------------------------------------------------------------#

def voos(request):
    if request.method == "POST":
        form = VooForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('voos')
    else:
        form = VooForm()

    voos = Voo.objects.all()
    return render(request, 'voos.html', {
        'form': form,
        'voos': voos
    })

def eliminar_voo(request, voo_id):
    voo = get_object_or_404(Voo, voo_id=voo_id)
    if request.method == 'POST':
        voo.delete()
        return redirect('voos')
    return redirect('voos')

#---------------------------------------------------------------#

def hotéis(request):
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
#---------------------------------------------------------------#

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
#---------------------------------------------------------------#


def feedbacks(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('feedbacks')
    else:
        form = FeedbackForm()

    feedbacks = Feedback.objects.all()
    return render(request, 'feedbacks.html', {
        'form': form,
        'feedbacks': feedbacks
    })

#---------------------------------------------------------------#

def pagamentos(request):
    if request.method == "POST":
        form = PagamentoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pagamentos')
    else:
        form = PagamentoForm()

    pagamentos = Pagamento.objects.all()
    return render(request, 'pagamentos.html', {
        'form': form,
        'pagamentos': pagamentos
    })
#---------------------------------------------------------------#

def faturas(request):
    if request.method == "POST":
        form = FaturaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('faturas')
    else:
        form = FaturaForm()

    faturas = Factura.objects.all()
    return render(request, 'faturas.html', {
        'form': form,
        'faturas': faturas
    })

