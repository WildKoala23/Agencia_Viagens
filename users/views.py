from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from .forms import *
from .models import *

# Create your views here.
def inserir_clientes(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            tipo_user_id = form.cleaned_data['tipo_user'].tipo_user_id
            nome = form.cleaned_data['nome']
            email = form.cleaned_data['email']
            endereco = form.cleaned_data['endereco']
            telefone = form.cleaned_data['telefone']

            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "CALL sp_inserir_utilizador(%s, %s, %s, %s, %s);",
                        [tipo_user_id, nome, email, endereco, telefone]
                    )
                return redirect('inserir_clientes')
            except Exception as e:
                mensagem_principal = str(e).splitlines()[0]
                form.add_error(None, mensagem_principal)
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
        return redirect('inserir_clientes')
    return redirect('inserir_clientes')



def user(req):

    return render(req, 'baseUser.html')

def comprasUser(req):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM comprasUtilizador(1)")
        rows = cursor.fetchall()
        print(rows)
    return render(req, 'comprasUser.html')