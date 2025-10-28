from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count, Avg
from pacotes.models import *
from pacotes.forms import *
from pagamentos.models import *
from users.models import *

#---------------------------------------------------------------#
def home(request):
    slides = [
        {"image": "https://images.unsplash.com/photo-1506744038136-46273834b3fb",
         "title": "Aventura nas montanhas",
         "text": "Descubra paisagens incríveis ao redor do mundo"},
        {"image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e",
         "title": "Viva o verão",
         "text": "Encontre as melhores praias para relaxar"},
        {"image": "https://images.unsplash.com/photo-1493558103817-58b2924bce98",
         "title": "Explore novos destinos",
         "text": "Momentos inesquecíveis esperam por si"},
    ]
    return render(request, "home.html", {"slides": slides})


def dashboard(request):
    """
    Dashboard melhorado com estatísticas dos managers customizados.
    """
    # Pacotes
    pacotes = Pacote.objects.all()[:6]
    
    # Estatísticas de Feedback usando os managers customizados
    total_feedbacks = Feedback.objects.count()
    top_pacotes = Feedback.objects.top_pacotes_por_avaliacao(min_feedbacks=1)[:5]
    feedbacks_recentes = Feedback.objects.feedbacks_recentes(dias=7)[:5]
    
    # Média geral de avaliações
    media_geral = Feedback.objects.aggregate(media=Avg('avaliacao'))['media'] or 0
    
    # Estatísticas de Faturas usando os managers customizados
    total_faturas = Factura.objects.count()
    facturas_pendentes = Factura.objects.facturas_pendentes().count()
    facturas_pagas = Factura.objects.facturas_pagas().count()
    
    # Total faturado (apenas facturas pagas)
    total_faturado = Factura.objects.facturas_pagas().aggregate(
        total=Sum('valor_total')
    )['total'] or 0
    
    # Top 5 clientes que mais gastaram
    top_clientes = Factura.objects.facturas_por_cliente()[:5]
    
    context = {
        # Métricas gerais
        'visita_site': '2345',  
        'total_reservas': Compra.objects.count(),
        'lucro_total': float(total_faturado),
        
        # Feedbacks
        'total_feedbacks': total_feedbacks,
        'ultimos_feeds': total_feedbacks,
        'top_pacotes': top_pacotes,
        'feedbacks_recentes': feedbacks_recentes,
        'media_avaliacoes': round(media_geral, 2),
        
        # Faturas
        'total_faturas': total_faturas,
        'facturas_pendentes': facturas_pendentes,
        'facturas_pagas': facturas_pagas,
        'total_faturado': total_faturado,
        'top_clientes': top_clientes,
        
        # Pacotes
        'pacotes': pacotes,
    }
    return render(request, 'dashboard.html', context)
