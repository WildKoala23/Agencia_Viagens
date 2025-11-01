from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Avg, Count
from .forms import *
from .models import *
from pacotes.models import Feedback
from pacotes.forms import FeedbackForm

# ============================================
# VIEWS DE CLIENTES
# ============================================

def clientes(request):
    """Lista e cria clientes"""
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente criado com sucesso!')
            return redirect('clientes')
    else:
        form = ClienteForm()

    clientes = Utilizador.objects.select_related('tipo_user').all()
    return render(request, 'clientes.html', {
        'form': form,
        'clientes': clientes
    })


def eliminar_cliente(request, cliente_id):
    """Elimina um cliente"""
    cliente = get_object_or_404(Utilizador, user_id=cliente_id)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, f'Cliente {cliente.nome} eliminado com sucesso!')
        return redirect('clientes')
    return redirect('clientes')


# ============================================
# VIEWS DE FEEDBACKS
# ============================================

def feedbacks(request):
    """Lista e cria feedbacks com estatísticas"""
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Feedback adicionado com sucesso!')
            return redirect('feedbacks')
    else:
        form = FeedbackForm()

    feedbacks = Feedback.objects.select_related('pacote').all().order_by('-data_feedback')
    
    # Estatísticas
    total_feedbacks = feedbacks.count()
    media_avaliacoes = feedbacks.aggregate(media=Avg('avaliacao'))['media'] or 0
    
    # Distribuição de avaliações
    distribuicao = {
        5: feedbacks.filter(avaliacao=5).count(),
        4: feedbacks.filter(avaliacao=4).count(),
        3: feedbacks.filter(avaliacao=3).count(),
        2: feedbacks.filter(avaliacao=2).count(),
        1: feedbacks.filter(avaliacao=1).count(),
    }
    
    return render(request, 'feedbacks.html', {
        'form': form,
        'feedbacks': feedbacks,
        'total_feedbacks': total_feedbacks,
        'media_avaliacoes': round(media_avaliacoes, 2),
        'distribuicao': distribuicao,
    })


def user(request):
    """Página de utilizadores"""
    data = Utilizador.objects.all()
    return render(request, 'baseUser.html', {
        'utilizadores': data
    })