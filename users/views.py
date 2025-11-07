from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from pymongo import MongoClient
from django.core import serializers
from django.contrib.auth import authenticate, login
from .forms import *
from django.contrib.auth import get_user_model

Utilizador = get_user_model()

client = MongoClient("mongodb://localhost:27017/")
db = client["bdII_25170"]
userData = db["dadosUser"]

def loginUser(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                print(request.user)
                return redirect('main:home')  # Redireciona para homepage
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
            # Criar novo utilizador com os campos atualizados
            user = form.save(commit=False)
            # Garantir que o password é definido corretamente
            if 'password' in form.cleaned_data:
                user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('inserir_clientes')
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
    data = userData.find_one({"Id_User": req.user.user_id})
    # data = list(userData.find())
    print(data)
    return render(req, 'dashboardUser.html', {"data": data})
   

def comprasUser(req):
    user = get_object_or_404(Utilizador, user_id=req.user.user_id)
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM comprasUtilizador(%s)", [req.user.user_id])
        data = cursor.fetchall()
    return render(req, 'comprasUser.html', {"data": data, "user": user})

def feedbacksUser(request):
    user = get_object_or_404(Utilizador, user_id=request.user.user_id)
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM comprasUtilizador(%s)", [request.user.user_id])
        compras = cursor.fetchall()
    
    return render(request, 'feedbacksUser.html', {"compras": compras, "user": user})

def perfilUser(request):
    user = get_object_or_404(Utilizador, user_id=request.user.user_id)

    if request.method == "POST":
        # Atualizar dados do perfil
        full_name = request.POST.get('first_name', '')
        name_parts = full_name.strip().split(' ', 1)
        user.first_name = name_parts[0] if name_parts else ''
        user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        user.email = request.POST.get('email', user.email)
        telefone = request.POST.get('telefone', '')
        user.telefone = int(telefone) if telefone else None
        user.save()
        return redirect('perfilUser')
    
    return render(request, 'perfilUser.html', {"user": user})