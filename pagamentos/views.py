from django.shortcuts import render, redirect, get_object_or_404  
from .forms import *

# Create your views here.
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

    faturas = Factura.objects.all()
    return render(request, 'faturas.html', {
        'form': form,
        'faturas': faturas
    })

