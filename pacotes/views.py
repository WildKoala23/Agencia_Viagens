from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from .forms import *
from django.db.models import Q, Max
from django.db import connection, transaction, IntegrityError, ProgrammingError, DatabaseError
from django.contrib import messages
import re
from pymongo import MongoClient
from pacotes.models import Pacote, Destino, PacoteDestino, Voo, Hotel
from django.contrib import messages



client = MongoClient("mongodb://localhost:27017/")
db = client["bd2_22598"]
banners = db["banners"]

def destinos(request):
    print('HERE')
    if request.method == "POST":
        form = DestinoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('destinos')
    else:
        form = DestinoForm()

    with connection.cursor() as cursor:
        cursor.execute("SELECT json_agg FROM mv_destinos")
        data = cursor.fetchone()
        data = data[0] if (data and data[0]) else []

    return render(request, 'destinos.html', {
        'form': form,
        'destinos': data,
    })

def editar_destino(request, destino_id):
    print(f'Destino: {destino_id}')

    destino = get_object_or_404(Destino, destino_id=destino_id)
    if request.method == 'POST':
        form = DestinoForm(request.POST, instance=destino)
        if form.is_valid():
            form.save()
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
        pacote_exists = Pacote.objects.filter(destinos=destino).exists()
        voo_exists = Voo.objects.filter(destino_id=destino.destino_id).exists()
        hotel_exists = Hotel.objects.filter(destino_id=destino.destino_id).exists()

        usado = pacote_exists or voo_exists or hotel_exists

        if usado:
            reasons = []
            if pacote_exists:
                reasons.append('pacotes')
            if voo_exists:
                reasons.append('voos')
            if hotel_exists:
                reasons.append('hoteis')
            messages.error(request, 'Não é possível eliminar este destino porque está a ser utilizado em: ' + ', '.join(reasons))
            return redirect('destinos')

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


def feedbacks_por_pacote(request, pacote_id):
    """
    Página dedicada para ver todos os feedbacks de um pacote específico
    """
    # Buscar informações do pacote
    pacote = get_object_or_404(Pacote, pacote_id=pacote_id)
    
    # Buscar feedbacks do pacote
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM view_feedbacks_completos WHERE pacote_id = %s", [pacote_id])
        columns = [col[0] for col in cursor.description]
        feedbacks = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return render(request, 'feedbacks_por_pacote.html', {
        'pacote': pacote,
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
    
    # Preparar lista de distribuição para o template
    distribuicao = [
        (5, estatisticas_gerais.get('total_5_estrelas', 0), estatisticas_gerais.get('percentual_5_estrelas', 0)),
        (4, estatisticas_gerais.get('total_4_estrelas', 0), estatisticas_gerais.get('percentual_4_estrelas', 0)),
        (3, estatisticas_gerais.get('total_3_estrelas', 0), estatisticas_gerais.get('percentual_3_estrelas', 0)),
        (2, estatisticas_gerais.get('total_2_estrelas', 0), estatisticas_gerais.get('percentual_2_estrelas', 0)),
        (1, estatisticas_gerais.get('total_1_estrela', 0), estatisticas_gerais.get('percentual_1_estrela', 0)),
    ]
    
    return render(request, 'feedback_estatisticas.html', {
        'estatisticas_gerais': estatisticas_gerais,
        'top_pacotes': top_pacotes,
        'estatisticas_pacotes': estatisticas_pacotes,
        'distribuicao': distribuicao
    })

def voos(request, voo_id=None):

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
                erro_texto = erro_texto.replace("Erro da base de dados:", "").strip()

                messages.error(request, erro_texto or "Erro ao inserir voo. Verifique os dados.")
        else:
            messages.error(request, " Erro ao validar o formulário. Verifique os dados.")
    else:
        form = VooForm(instance=voo)

    with connection.cursor() as cursor:
        cursor.execute("SELECT json_agg(row_to_json(v)) FROM mv_voos v")
        data = cursor.fetchone()
        voos = data[0] if (data and data[0]) else []

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

    if request.method == "POST":
        form = HotelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Hotel adicionado com sucesso!")
            return redirect('hoteis')
    else:
        form = HotelForm()

    with connection.cursor() as cursor:
        cursor.execute("SELECT json_agg(row_to_json(h)) FROM mv_hoteis h")
        data = cursor.fetchone()
        hoteis = data[0] if (data and data[0]) else []

    return render(request, 'hoteis.html', {
        'form': form,
        'hoteis': hoteis
    })


def editar_hotel(request, hotel_id):
    """
    Editar um hotel existente.
    """
    hotel = get_object_or_404(Hotel, hotel_id=hotel_id)

    if request.method == "POST":
        form = HotelForm(request.POST, instance=hotel)
        if form.is_valid():
            form.save()
            messages.success(request, "Hotel atualizado com sucesso!")
            return redirect('hoteis')
    else:
        form = HotelForm(instance=hotel)

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM vw_hoteis ORDER BY nome_hotel;")
        columns = [col[0] for col in cursor.description]
        hoteis = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return render(request, 'hoteis.html', {
        'form': form,
        'hoteis': hoteis,
        'hotel_editar': hotel
    })


def eliminar_hotel(request, hotel_id):
    hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
    if request.method == 'POST':
        hotel.delete()
        return redirect('hoteis')
    return redirect('hoteis')

def selecionar_hotel(request, hotel_id, pacote_id):
    pacote = get_object_or_404(Pacote, pacote_id=pacote_id)
    hotel = get_object_or_404(Hotel, hotel_id=hotel_id)

    if hasattr(pacote, 'hotel'):
        pacote.hotel = hotel
        pacote.save()

    return render(request, "confirmar_hotel.html", {
        "pacote": pacote,
        "hotel": hotel,
    })
def hotel_detalhes(request, hotel_id):
    hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
    pacote_id = request.GET.get("pacote") 
    pacote = None
    if pacote_id:
        from pacotes.models import Pacote
        try:
            pacote = Pacote.objects.get(pacote_id=pacote_id)
        except Pacote.DoesNotExist:
            pacote = None

    return render(
        request,
        "hotel_detalhes.html",
        {
            "hotel": hotel,
            "pacote": pacote,  
        },
    )


def pacotes(request, pacote_id=None):

    pacote = get_object_or_404(Pacote, pacote_id=pacote_id) if pacote_id else None

    if request.method == "POST":
        form = PacoteForm(request.POST, request.FILES, instance=pacote)
        if form.is_valid():
            pacote = form.save()

            banners.update_one(
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

            if pacote_id:
                messages.success(request, "Pacote atualizado com sucesso!")
            else:
                messages.success(request, "Pacote criado com sucesso!")

            return redirect('pacotes')

    else:
        form = PacoteForm(instance=pacote)

    with connection.cursor() as cursor:
        cursor.execute("SELECT pacotesToJson()")
        data = cursor.fetchone()
        pacotes_data = data[0] if (data and data[0]) else []

    return render(request, 'pacotes.html', {
        'form': form,
        'pacote_editar': pacote,  
        'data': pacotes_data,
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

    # Tenta ir buscar o banner correspondente ao pacote
    banner = banners.find_one({"pacote_id": pacote_id, "ativo": True})

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
    # Usar a função SQL `pacotesToJson()` (que retorna os pacotes de `mv_pacotes`)
    # e agregar destinos separadamente. Isto preserva o uso das funções/materialized
    # views já existentes que pediste.
    destinos = Destino.objects.all()
    q = request.GET.get("q", "").strip()
    pais_query = request.GET.get("pais", "").strip()
    preco = request.GET.get("preco")
    mes = request.GET.get("mes")

    pacotes = []
    import json as _json
    with connection.cursor() as cursor:
        # 1) pede os pacotes via função pacotesToJson()
        try:
            cursor.execute("SELECT pacotesToJson()")
            row = cursor.fetchone()
            pacotes = row[0] if row else []
            # se o adaptador retornar string, parse
            if isinstance(pacotes, (str, bytes)):
                pacotes = _json.loads(pacotes)
        except Exception:
            pacotes = []

        # 2) agrega destinos por pacote para evitar N+1
        try:
            cursor.execute("SELECT pd.pacote_id, json_agg(json_build_object('destino_id', d.destino_id, 'nome', d.nome, 'pais', d.pais)) AS destinos FROM pacote_destino pd JOIN destino d ON d.destino_id = pd.destino_id GROUP BY pd.pacote_id")
            destinos_rows = cursor.fetchall()
            destinos_map = {row[0]: (row[1] or []) for row in destinos_rows}
        except Exception:
            destinos_map = {}

    # Anexa destinos a cada pacote
    for p in pacotes:
        pid = p.get('pacote_id')
        p['destinos'] = destinos_map.get(pid, [])

    # Aplica filtros em Python (atenção: pode ser menos eficiente que filtrar no DB)
    def matches_q(p):
        if not q:
            return True
        ql = q.lower()
        if ql in (p.get('nome') or '').lower() or ql in (p.get('descricao_item') or '').lower():
            return True
        for d in p.get('destinos', []):
            if ql in (d.get('nome') or '').lower() or ql in (d.get('pais') or '').lower():
                return True
        return False

    def matches_pais(p):
        if not pais_query:
            return True
        pq = pais_query.lower()
        for d in p.get('destinos', []):
            if pq in (d.get('pais') or '').lower():
                return True
        return False

    def matches_preco(p):
        if not preco:
            return True
        try:
            return float(p.get('preco_total') or 0) <= float(preco)
        except Exception:
            return True

    def matches_mes(p):
        if not mes:
            return True
        try:
            from datetime import datetime
            di = p.get('data_inicio')
            if not di:
                return False
            # aceita iso string
            dt = datetime.fromisoformat(di)
            return dt.month == int(mes)
        except Exception:
            return False

    pacotes = [p for p in pacotes if matches_q(p) and matches_pais(p) and matches_preco(p) and matches_mes(p)]

    # Monta imagem_url e usa banner do MongoDB quando existir
    for rec in pacotes:
        # imagem pode estar no registro retornado
        imagem_field = rec.get('imagem') or rec.get('imagem_url')
        if imagem_field:
            try:
                imagem_str = imagem_field.decode() if isinstance(imagem_field, bytes) else str(imagem_field)
            except Exception:
                imagem_str = str(imagem_field)
            rec['imagem_url'] = imagem_str if imagem_str.startswith('/') else f"/media/{imagem_str}"
        else:
            rec['imagem_url'] = None

        try:
            banner = banners.find_one({"pacote_id": rec.get('pacote_id'), "ativo": True})
            if banner and banner.get('imagem_url'):
                rec['imagem_url'] = banner.get('imagem_url')
        except Exception:
            pass

    # Agrupar pacotes por país
    pacotes_por_pais = {}
    for pacote in pacotes:
        destinos_list = pacote.get('destinos') or []
        if not destinos_list:
            pais = 'Sem país'
            pacotes_por_pais.setdefault(pais, []).append(pacote)
        else:
            for d in destinos_list:
                pais = d.get('pais') or 'Sem país'
                pacotes_por_pais.setdefault(pais, []).append(pacote)

    # Preço máximo (mantemos consulta ORM só para agregação simples)
    preco_maximo = Pacote.objects.aggregate(Max("preco_total"))["preco_total__max"] or 10000
# -------------------------------------------------------------------------------------------------------
    meses = [
        ("01", "Janeiro"), ("02", "Fevereiro"), ("03", "Março"), ("04", "Abril"),
        ("05", "Maio"), ("06", "Junho"), ("07", "Julho"), ("08", "Agosto"),
        ("09", "Setembro"), ("10", "Outubro"), ("11", "Novembro"), ("12", "Dezembro"),
    ]
 
    return render(request, "pacotes_por_pais.html", {
        "pacotes_por_pais": pacotes_por_pais,
        "preco_maximo": preco_maximo,
        "meses": meses,
        "q": q,
        "pais_query": pais_query,
    })

def reserva_pacote(request, pacote_id):

    pacote = get_object_or_404(Pacote, pacote_id=pacote_id)

    destinos_do_pacote = pacote.destinos.all()

    hoteis = Hotel.objects.filter(destino_id__in=destinos_do_pacote)

    return render(request, "reserva_pacote.html", {
        "pacote": pacote,
        "hoteis": hoteis,
    })