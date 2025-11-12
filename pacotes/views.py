from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from .forms import *
from django.db.models import Q, Max
from django.db import connection, transaction, IntegrityError, ProgrammingError, DatabaseError
from django.contrib import messages
import re
from pymongo import MongoClient
from pacotes.models import Pacote, Destino, PacoteDestino


client = MongoClient("mongodb://localhost:27017/")
db = client["bd2_22598"]
banners = db["banners"]

# Create your views here.

def destinos(request):
    if request.method == "POST":
        form = DestinoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('destinos')
    else:
        form = DestinoForm()

    destinos = Destino.objects.all()
    return render(request, 'destinos.html', {
        'form': form,
        'destinos': destinos
    })

def editar_destino(request, destino_id):
    destino = get_object_or_404(Destino, destino_id=destino_id)
    
    if request.method == 'POST':
        form = DestinoForm(request.POST, instance=destino)
        if form.is_valid():
            form.save()
            messages.success(request, 'Destino atualizado com sucesso!')
            return redirect('destinos')
    else:
        form = DestinoForm(instance=destino)
    
    destinos = Destino.objects.all()
    return render(request, 'destinos.html', {
        'form': form,
        'destinos': destinos
    })

def eliminar_destino(request, destino_id):
    destino = get_object_or_404(Destino, destino_id=destino_id)
    if request.method == 'POST':
        destino.delete()
        return redirect('destinos')
    return redirect('destinos')

def feedbacks(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('feedbacks')
    else:
        form = FeedbackForm()

    # Buscar feedbacks usando a VIEW criada na BD (SQL DIRETO - SUA PARTE)
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM view_feedbacks_completos")
        columns = [col[0] for col in cursor.description]
        feedbacks = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return render(request, 'feedbacks.html', {
        'form': form,
        'feedbacks': feedbacks
    })


def feedback_estatisticas(request):
    """
    Mostra estatísticas gerais de feedbacks e avaliações de pacotes
    (SQL DIRETO - SUA PARTE - usando FUNCTIONs e VIEWs da BD)
    """
    with connection.cursor() as cursor:
        # Estatísticas gerais
        cursor.execute("SELECT * FROM get_estatisticas_feedbacks()")
        columns = [col[0] for col in cursor.description]
        result = cursor.fetchone()
        estatisticas_gerais = dict(zip(columns, result)) if result else {}
        
        # Calcular percentagens para as barras de progresso
        if estatisticas_gerais and estatisticas_gerais.get('total_feedbacks', 0) > 0:
            total = estatisticas_gerais['total_feedbacks']
            estatisticas_gerais['percentual_5_estrelas'] = round((estatisticas_gerais['total_5_estrelas'] / total) * 100, 1)
            estatisticas_gerais['percentual_4_estrelas'] = round((estatisticas_gerais['total_4_estrelas'] / total) * 100, 1)
            estatisticas_gerais['percentual_3_estrelas'] = round((estatisticas_gerais['total_3_estrelas'] / total) * 100, 1)
            estatisticas_gerais['percentual_2_estrelas'] = round((estatisticas_gerais['total_2_estrelas'] / total) * 100, 1)
            estatisticas_gerais['percentual_1_estrela'] = round((estatisticas_gerais['total_1_estrela'] / total) * 100, 1)
        else:
            estatisticas_gerais['percentual_5_estrelas'] = 0
            estatisticas_gerais['percentual_4_estrelas'] = 0
            estatisticas_gerais['percentual_3_estrelas'] = 0
            estatisticas_gerais['percentual_2_estrelas'] = 0
            estatisticas_gerais['percentual_1_estrela'] = 0
        
        # Top pacotes avaliados
        cursor.execute("SELECT * FROM get_top_pacotes_avaliados(5)")
        columns = [col[0] for col in cursor.description]
        top_pacotes = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Estatísticas por pacote
        cursor.execute("SELECT * FROM view_estatisticas_pacotes")
        columns = [col[0] for col in cursor.description]
        estatisticas_pacotes = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return render(request, 'feedback_estatisticas.html', {
        'estatisticas_gerais': estatisticas_gerais,
        'top_pacotes': top_pacotes,
        'estatisticas_pacotes': estatisticas_pacotes
    })

def voos(request, voo_id=None):
    """
    Página de gestão de voos.
    - Permite inserir e editar voos.
    - Mostra mensagens de erro vindas do trigger PostgreSQL (RAISE EXCEPTION).
    """

    voo = get_object_or_404(Voo, voo_id=voo_id) if voo_id else None

    if request.method == "POST":
        form = VooForm(request.POST, instance=voo)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                return redirect('voos')

            except (IntegrityError, ProgrammingError, DatabaseError) as e:
                erro_texto = str(e)

                if "CONTEXT" in erro_texto:
                    erro_texto = erro_texto.split("CONTEXT")[0].strip()

                erro_texto = re.sub(r"^ERROR:\s*", "", erro_texto, flags=re.IGNORECASE)
                erro_texto = erro_texto.replace("Erro do banco de dados:", "").strip()

                messages.error(request, erro_texto or "Erro ao inserir voo. Verifique os dados.")
        else:
            messages.error(request, "❌ Erro ao validar o formulário. Verifique os dados.")
    else:
        form = VooForm(instance=voo)

    # --- PESQUISA ---
    q = request.GET.get("q")
    if q:
        voos = Voo.objects.filter(
            Q(destino__nome__icontains=q) |
            Q(companhia__icontains=q)
        )
    else:
        voos = Voo.objects.all()
    # --- FIM PESQUISA ---

    return render(request, 'voos.html', {
        'form': form,
        'voos': voos,
        'voo_editar': voo,
    })

def eliminar_voo(request, voo_id):
    """
    Elimina um voo existente.
    """
    voo = get_object_or_404(Voo, voo_id=voo_id)
    if request.method == 'POST':
        voo.delete()
    return redirect('voos')


def hotel(request):
    """
    Mostra todos os hotéis (a partir da view SQL vw_hoteis)
    e permite adicionar novos hotéis via formulário.
    """
    if request.method == "POST":
        form = HotelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('hoteis')
    else:
        form = HotelForm()

    # Buscar dados diretamente da VIEW SQL
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM vw_hoteis ORDER BY nome_hotel;")  # <-- alterado aqui
        columns = [col[0] for col in cursor.description]
        hoteis = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return render(request, 'hoteis.html', {
        'form': form,
        'hoteis': hoteis
    })

def editar_hotel(request, hotel_id):
    """Editar um hotel existente"""
    hotel = get_object_or_404(Hotel, hotel_id=hotel_id)

    if request.method == "POST":
        form = HotelForm(request.POST, instance=hotel)
        if form.is_valid():
            form.save()
            return redirect('hoteis')
    else:
        form = HotelForm(instance=hotel)

    return render(request, 'editar_hotel.html', {
        'form': form,
        'hotel': hotel
    })

def eliminar_hotel(request, hotel_id):
    hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
    if request.method == 'POST':
        hotel.delete()
        return redirect('hoteis')
    return redirect('hoteis')


def pacotes(request, pacote_id=None):
    """
    Página única para gerir pacotes:
    - Mostra lista
    - Permite criar ou editar
    - Sincroniza imagens com MongoDB
    """
    from pymongo import MongoClient

    pacote = get_object_or_404(Pacote, pacote_id=pacote_id) if pacote_id else None

    if request.method == "POST":
        form = PacoteForm(request.POST, request.FILES, instance=pacote)
        if form.is_valid():
            pacote = form.save()

            # 🔹 Atualizar / criar no MongoDB
            client = MongoClient("mongodb://localhost:27017/")
            db = client["bd2_22598"]
            collection = db["banners"]

            collection.update_one(
                {"pacote_id": pacote.pacote_id},
                {"$set": {
                    "nome": pacote.nome,
                    "imagem_url": f"/media/{pacote.imagem}" if pacote.imagem else None,
                    "preco_total": float(pacote.preco_total),
                    "data_inicio": str(pacote.data_inicio),
                    "data_fim": str(pacote.data_fim),
                    "ativo": True
                }},
                upsert=True
            )
            client.close()

            return redirect('pacotes')
    else:
        form = PacoteForm(instance=pacote)

    query = request.GET.get('q', '')
    pacotes = Pacote.objects.all().order_by('pacote_id')
    if query:
        pacotes = pacotes.filter(
            Q(nome__icontains=query) | Q(destinos__nome__icontains=query)
        ).distinct()

    return render(request, 'pacotes.html', {
        'form': form,
        'pacotes': pacotes,
        'pacote_editar': pacote,  # 👈 para sabermos se estamos a editar
        'query': query,
    })


def pacote_detalhes(request, pacote_id):
    pacote = get_object_or_404(Pacote, pacote_id=pacote_id)
    
    # Busca o banner correspondente ao pacote no MongoDB
    banner = banners.find_one({"pacote_id": pacote_id, "ativo": True})
    
    # Prioridade: MongoDB banner > imagem do pacote no PostgreSQL > imagem padrão
    if banner and "imagem_url" in banner:
        imagem_url = banner["imagem_url"]
    elif pacote.imagem:
        imagem_url = f"/media/{pacote.imagem}"
    else:
        imagem_url = None
    
    return render(request, 'pacote_detalhes.html', {
        "pacote": pacote,
        "imagem_url": imagem_url
    })


def eliminar_pacote(request, pacote_id):
    pacote = get_object_or_404(Pacote, pacote_id=pacote_id)
    if request.method == 'POST':
        pacote.delete()
        return redirect('pacotes')
    return redirect('pacotes')


def pacote_detalhes(request, pacote_id):
    pacote = get_object_or_404(Pacote, pk=pacote_id)

    # Conecta ao MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["bd2_22598"]
    collection = db["banners"]

    # Tenta ir buscar o banner correspondente ao pacote
    banner = collection.find_one({"pacote_id": pacote_id, "ativo": True})

    # Se encontrar, usa a imagem do MongoDB; senão, usa a imagem padrão do modelo
    imagem_url = banner["imagem_url"] if banner else f"/media/{pacote.imagem}"

    # Divide a descrição em blocos por dia
    texto = pacote.descricao_item or ""
    partes = re.split(r"\s*\d+\s*[°º]\s*DIA\s*", texto, flags=re.IGNORECASE)
    partes = [p.strip() for p in partes if p.strip()]

    dias = []
    for i, parte in enumerate(partes, start=1):
        dias.append({
            "titulo": f"{i}º DIA",
            "texto": parte
        })

    # O return deve estar fora do ciclo
    return render(request, 'pacote_detalhes.html', {
        "pacote": pacote,
        "imagem_url": imagem_url,
        "dias": dias
    })


def pacotes_por_pais(request):
    destinos = Destino.objects.all()
    pacotes = Pacote.objects.all()

    # Filtros GET
    pais_query = request.GET.get("pais")  # 🆕 campo de pesquisa por país
    preco = request.GET.get("preco")
    mes = request.GET.get("mes")

    # 🔹 Filtro por país (usando relação com destinos)
    if pais_query:
        pacotes = pacotes.filter(destinos__pais__icontains=pais_query)

    # 🔹 Filtro por preço
    if preco:
        try:
            pacotes = pacotes.filter(preco_total__lte=float(preco))
        except ValueError:
            pass

    # 🔹 Filtro por mês
    if mes:
        pacotes = pacotes.filter(data_inicio__month=mes)

    # 🔹 Agrupar pacotes por país
    pacotes_por_pais = {}
    pacotes = pacotes.prefetch_related("destinos").distinct()

    for pacote in pacotes:
        for destino in pacote.destinos.all():
            pais = destino.pais
            if pais not in pacotes_por_pais:
                pacotes_por_pais[pais] = []
            pacotes_por_pais[pais].append(pacote)

    preco_maximo = Pacote.objects.aggregate(Max("preco_total"))["preco_total__max"] or 10000

    meses = [
        ("01", "Janeiro"), ("02", "Fevereiro"), ("03", "Março"), ("04", "Abril"),
        ("05", "Maio"), ("06", "Junho"), ("07", "Julho"), ("08", "Agosto"),
        ("09", "Setembro"), ("10", "Outubro"), ("11", "Novembro"), ("12", "Dezembro"),
    ]

    return render(request, "pacotes_por_pais.html", {
        "pacotes_por_pais": pacotes_por_pais,
        "preco_maximo": preco_maximo,
        "meses": meses,
        "pais_query": pais_query or "",
    })