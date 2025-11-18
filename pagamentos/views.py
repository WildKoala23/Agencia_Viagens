from django.shortcuts import render, redirect, get_object_or_404  
from django.db import connection
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

    # Buscar faturas usando a VIEW criada na BD (SQL DIRETO - SUA PARTE)
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM view_faturas_completas")
        columns = [col[0] for col in cursor.description]
        faturas = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return render(request, 'faturas.html', {
        'form': form,
        'faturas': faturas
    })


# def fatura_detalhes(request, fatura_id):
#     """
#     Mostra os detalhes completos de uma fatura incluindo todas as suas linhas
#     (SQL DIRETO - SUA PARTE - usando FUNCTIONs da BD)
#     """
#     with connection.cursor() as cursor:
#         # Buscar informações da fatura usando FUNCTION
#         cursor.execute("SELECT * FROM get_fatura_detalhes(%s)", [fatura_id])
#         columns = [col[0] for col in cursor.description]
#         result = cursor.fetchone()
        
#         if not result:
#             return render(request, 'fatura_detalhes.html', {
#                 'error': 'Fatura não encontrada'
#             })
        
#         fatura = dict(zip(columns, result))
        
#         # Buscar linhas da fatura usando FUNCTION
#         cursor.execute("SELECT * FROM get_fatura_linhas(%s)", [fatura_id])
#         columns = [col[0] for col in cursor.description]
#         linhas = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
#     return render(request, 'fatura_detalhes.html', {
#         'fatura': fatura,
#         'linhas': linhas
#     })

