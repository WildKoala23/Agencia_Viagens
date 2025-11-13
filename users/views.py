from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from django.db.models import Q
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

            print(email, password)

            user = authenticate(request, email=email, password=password)

            print(user)
            if user is not None:
                login(request, user)
                
                # Redirecionamento condicional
                if user.is_staff:
                    return redirect('main:dashboard')  # staff
                else:
                    return redirect('users:user')  # usuário comum
            else:
                form.add_error(None, "Email ou senha inválidos")
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
            return redirect('users:inserir_clientes')
    else:
        form = ClienteForm()
    # Excluir o utilizador atualmente autenticado da lista exibida
    if request.user.is_authenticated:
        clientes = Utilizador.objects.exclude(user_id=request.user.user_id)
    else:
        clientes = Utilizador.objects.all()

    # Filtrar por query param 'q' (nome ou email)
    q = request.GET.get('q', '').strip()
    if q:
        clientes = clientes.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q))

    return render(request, 'clientes.html', {
        'form': form,
        'clientes': clientes
    })

def eliminar_cliente(request, cliente_id):
    cliente = get_object_or_404(Utilizador, user_id=cliente_id)
    if request.method == 'POST':
        cliente.delete()
        return redirect('users:inserir_clientes')
    return redirect('users:inserir_clientes')

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
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        telefone = request.POST.get('telefone', '')
        user.telefone = int(telefone) if telefone else None
        user.save()
        return redirect('users:perfilUser')
    
    return render(request, 'perfilUser.html', {"user": user})


def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Utilizador, user_id=cliente_id)
    # Use the edit form where password is optional
    try:
        from .forms import EditClienteForm
    except Exception:
        from .forms import ClienteForm as EditClienteForm

    if request.method == 'POST':
        form = EditClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            return redirect('users:inserir_clientes')
    else:
        form = EditClienteForm(instance=cliente)

    return render(request, 'editar_cliente.html', {'form': form, 'cliente': cliente})