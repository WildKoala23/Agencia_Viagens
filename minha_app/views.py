from django.shortcuts import render, redirect
from .models import Cliente, Destino, Voo, Hotel, Pacote, Feedback,Reserva, Pagamento, Fatura
from .forms import ClienteForm, DestinoForm,VooForm,HotelForm, PacoteForm, FeedbackForm, ReservaForm, PagamentoForm, FaturaForm

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

    clientes = Cliente.objects.all()
    return render(request, 'clientes.html', {
        'form': form,
        'clientes': clientes
    })

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

    pacotes = Pacote.objects.all()
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

def reservas(request):
    if request.method == "POST":
        form = ReservaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('reservas')
    else:
        form = ReservaForm()

    reservas = Reserva.objects.all()
    return render(request, 'reservas.html', {
        'form': form,
        'reservas': reservas
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

    faturas = Fatura.objects.all()
    return render(request, 'faturas.html', {
        'form': form,
        'faturas': faturas
    })

#-----------------Eliminar----------------------------------------------#
from django.shortcuts import get_object_or_404

def eliminar_destino(request, destino_id):
    destino = get_object_or_404(Destino, pk=destino_id)
    destino.delete()
    return redirect('destinos')

def eliminar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    cliente.delete()
    return redirect('clientes')
#---------------------------------------------------------------#

