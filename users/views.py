from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from pymongo import MongoClient
from django.core import serializers
from django.contrib.auth import authenticate, login
from .forms import *
from django.contrib.auth import get_user_model

Utilizador = get_user_model()

client = MongoClient("mongodb://localhost:27017/")
db = client["bd2_22598"]
userData = db["dadosUser"]

def loginUser(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, email=email, password=password)

            print(user)
            if user is not None:
                login(request, user)
                return redirect('main:home')
            else:
                form.add_error(None, "Invalid email or password")  # adds non-field error
    else:
        form = LoginForm()
    return render(request, 'registration/login.html')



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
    data = userData.find_one({"Id_User": 1})
    # data = list(userData.find())
    print(data)
    return render(req, 'dashboardUser.html', {"data": data})
   

def comprasUser(req):
    user_id = 1
    user = get_object_or_404(Utilizador, user_id=user_id)
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM comprasUtilizador(1)")
        data = cursor.fetchall()
        print(data)
    return render(req, 'comprasUser.html', {"data": data, "user": user})

def feedbacksUser(request):
    # Por enquanto vamos usar user_id = 1 (depois podes integrar com autenticação)
    user_id = 1
    user = get_object_or_404(Utilizador, user_id=user_id)
    
    with connection.cursor() as cursor:
        # Buscar compras do utilizador para poder avaliar
        cursor.execute("SELECT * FROM comprasUtilizador(%s)", [user_id])
        compras = cursor.fetchall()
    
    return render(request, 'feedbacksUser.html', {"compras": compras})


def perfilUser(request):
    # Por enquanto user_id = 1 (depois integrar autenticação)
    user_id = 1

    #Buscar dados do utilizador
    user = get_object_or_404(Utilizador, user_id=user_id)

    if request.method == "POST":
        # Atualizar dados do perfil
        user.nome = request.POST.get('nome', user.nome)
        user.email = request.POST.get('email', user.email)
        user.telefone = request.POST.get('telefone', user.telefone)
        user.endereco = request.POST.get('endereco', user.endereco)
        user.save()
        return redirect('perfilUser')

    return render(request, 'perfilUser.html', {"user": user})