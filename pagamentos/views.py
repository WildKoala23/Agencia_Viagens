from django.shortcuts import render, redirect, get_object_or_404  
from django.contrib import messages
from django.db.models import Sum, Count
from .forms import *
from .models import *

# ============================================
# VIEWS DE PAGAMENTO
# ============================================

def pagamentos(request):
    """Lista e cria pagamentos"""
    if request.method == "POST":
        form = PagamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pagamento criado com sucesso!')
            return redirect('pagamentos')
    else:
        form = PagamentoForm()

    pagamentos = Pagamento.objects.select_related('compra', 'compra__user').all()
    
    # Estatísticas
    total_pagamentos = pagamentos.count()
    pagamentos_pendentes = pagamentos.filter(estado='PENDENTE').count()
    pagamentos_pagos = pagamentos.filter(estado='PAGO').count()
    total_valor = pagamentos.filter(estado='PAGO').aggregate(total=Sum('valor'))['total'] or 0
    
    return render(request, 'pagamentos.html', {
        'form': form,
        'pagamentos': pagamentos,
        'total_pagamentos': total_pagamentos,
        'pagamentos_pendentes': pagamentos_pendentes,
        'pagamentos_pagos': pagamentos_pagos,
        'total_valor': total_valor,
    })


# ============================================
# VIEWS DE FATURA
# ============================================

def faturas(request):
    """Lista e cria faturas"""
    if request.method == "POST":
        form = FaturaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fatura criada com sucesso!')
            return redirect('faturas')
    else:
        form = FaturaForm()

    faturas = Factura.objects.select_related('compra', 'pagamento', 'compra__user').all()
    
    # Estatísticas
    total_faturas = faturas.count()
    total_faturado = faturas.aggregate(total=Sum('valor_total'))['total'] or 0
    
    return render(request, 'faturas.html', {
        'form': form,
        'faturas': faturas,
        'total_faturas': total_faturas,
        'total_faturado': total_faturado,
    })

