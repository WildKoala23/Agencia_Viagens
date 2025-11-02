from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
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



def user(req):

    return render(req, 'baseUser.html')

def comprasUser(req):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM comprasUtilizador(1)")
        rows = cursor.fetchall()
        print(rows)
    return render(req, 'comprasUser.html')