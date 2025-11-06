from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from django.core import serializers
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
    # Por enquanto user_id = 1 (depois integrar autenticação)
    user_id = 1
    user = get_object_or_404(Utilizador, user_id=user_id)
    
    # Buscar dados para a dashboard
    with connection.cursor() as cursor:
        # Buscar compras/reservas do utilizador
        cursor.execute("SELECT * FROM comprasUtilizador(%s)", [user_id])
        compras = cursor.fetchall()
        
        # Debug: imprimir primeira compra para ver a estrutura
        if compras:
            print("DEBUG - Estrutura da compra:", compras[0])
    
    # Calcular estatísticas
    total_reservas = len([c for c in compras if c[5] != 'Cancelado']) if compras else 0
    total_viagens = len([c for c in compras if c[5] == 'Confirmado']) if compras else 0
    total_feedbacks = 0  # Pode buscar da tabela de feedbacks
    
    # Calcular valor total (índice 6 é o preço)
    valor_total = 0
    if compras:
        for c in compras:
            if c[5] != 'Cancelado':
                try:
                    # c[6] deve ser o preço
                    valor_total += float(c[6])
                except (ValueError, TypeError):
                    pass
    
    # Próximas viagens (não canceladas)
    proximas_viagens = [c for c in compras if c[5] != 'Cancelado'][:3] if compras else []
    
    context = {
        'user': user,
        'total_reservas': total_reservas,
        'total_viagens': total_viagens,
        'total_feedbacks': total_feedbacks,
        'valor_total': f"{valor_total:.2f}",
        'proximas_viagens': proximas_viagens,
        'atividades': []  # Pode adicionar atividades depois
    }
    
    return render(req, 'dashboardUser.html', context)

def comprasUser(req):
    # Por enquanto user_id = 1 (depois integrar autenticação)
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
    
    return render(request, 'feedbacksUser.html', {"compras": compras, "user": user})

def perfilUser(request):
    # Por enquanto user_id = 1 (depois integrar autenticação)
    user_id = 1
    
    # Buscar dados do utilizador
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