from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from .models import *

# Create your views here.
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

def user(req):
    data = Utilizador.objects.all()
    print(data)
    return render(req, 'baseUser.html')

# def comprasUser(req, id):

#     return render(req, 'comprasUser.html')