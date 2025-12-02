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
from django.http import HttpResponse, Http404
from bson.objectid import ObjectId
from django.urls import reverse


client = MongoClient("mongodb://localhost:27017/")
db = client["bd2_22598"]
banners = db["banners"]
capa_hotel = db["capa_hotel"]
detalhes_hotel = db["detalhes_hotel"]

def destinos(request):
    if request.method == "POST":
        form = DestinoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('destinos')
    else:
        form = DestinoForm()

    with connection.cursor() as cursor:
        cursor.execute("SELECT json_agg(row_to_json(d)) FROM mv_destinos d")
        data = cursor.fetchone()
        data = data[0] if (data and data[0]) else []

    return render(request, 'destinos.html', {
        'form': form,
        'destinos': data,
    })

def editar_destino(request, destino_id):
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
        form = HotelForm(request.POST, request.FILES)
        if form.is_valid():
            hotel_obj = form.save()
            
            # Salvar imagem de capa no MongoDB se foi enviada
            imagem = request.FILES.get('imagem')
            if imagem:
                # Ler o conteúdo da imagem
                imagem_data = imagem.read()
                
                # Salvar ou atualizar no MongoDB
                capa_hotel.update_one(
                    {'hotel_id': hotel_obj.hotel_id},
                    {
                        '$set': {
                            'hotel_id': hotel_obj.hotel_id,
                            'nome_hotel': hotel_obj.nome,
                            'imagem': imagem_data,
                            'content_type': imagem.content_type,
                            'filename': imagem.name
                        }
                    },
                    upsert=True
                )
            
            # Salvar múltiplas imagens de detalhes no MongoDB
            imagens_detalhes = request.FILES.getlist('imagens_detalhes')
            if imagens_detalhes:
                # Remover imagens antigas se existirem
                detalhes_hotel.delete_many({'hotel_id': hotel_obj.hotel_id})
                
                # Salvar cada imagem
                for idx, img in enumerate(imagens_detalhes):
                    imagem_data = img.read()
                    detalhes_hotel.insert_one({
                        'hotel_id': hotel_obj.hotel_id,
                        'nome_hotel': hotel_obj.nome,
                        'imagem': imagem_data,
                        'content_type': img.content_type,
                        'filename': img.name,
                        'ordem': idx
                    })
            
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
        form = HotelForm(request.POST, request.FILES, instance=hotel)
        if form.is_valid():
            hotel_obj = form.save()
            
            # Salvar imagem de capa no MongoDB se foi enviada
            imagem = request.FILES.get('imagem')
            if imagem:
                # Ler o conteúdo da imagem
                imagem_data = imagem.read()
                
                # Salvar ou atualizar no MongoDB
                capa_hotel.update_one(
                    {'hotel_id': hotel_obj.hotel_id},
                    {
                        '$set': {
                            'hotel_id': hotel_obj.hotel_id,
                            'nome_hotel': hotel_obj.nome,
                            'imagem': imagem_data,
                            'content_type': imagem.content_type,
                            'filename': imagem.name
                        }
                    },
                    upsert=True
                )
            
            # Salvar múltiplas imagens de detalhes no MongoDB
            imagens_detalhes = request.FILES.getlist('imagens_detalhes')
            if imagens_detalhes:
                # Remover imagens antigas
                detalhes_hotel.delete_many({'hotel_id': hotel_obj.hotel_id})
                
                # Salvar cada nova imagem
                for idx, img in enumerate(imagens_detalhes):
                    imagem_data = img.read()
                    detalhes_hotel.insert_one({
                        'hotel_id': hotel_obj.hotel_id,
                        'nome_hotel': hotel_obj.nome,
                        'imagem': imagem_data,
                        'content_type': img.content_type,
                        'filename': img.name,
                        'ordem': idx
                    })
            
            messages.success(request, "Hotel atualizado com sucesso!")
            return redirect('hoteis')
    else:
        form = HotelForm(instance=hotel)

    # Buscar imagem de capa do MongoDB
    imagem_capa_url = None
    imagem_capa_doc = capa_hotel.find_one({'hotel_id': hotel_id})
    if imagem_capa_doc:
        
        imagem_capa_url = reverse('hotel_imagem', args=[hotel_id])
    
    # Buscar imagens de detalhes do MongoDB
    imagens_detalhes_raw = list(detalhes_hotel.find({'hotel_id': hotel_id}).sort('ordem', 1))
    imagens_detalhes_existentes = []
    for img in imagens_detalhes_raw:
        img['id'] = str(img['_id'])
        imagens_detalhes_existentes.append(img)

    with connection.cursor() as cursor:
        cursor.execute("SELECT json_agg(row_to_json(h)) FROM mv_hoteis h")
        data = cursor.fetchone()
        hoteis = data[0] if (data and data[0]) else []

    return render(request, 'hoteis.html', {
        'form': form,
        'hoteis': hoteis,
        'hotel_editar': hotel,
        'imagem_capa_url': imagem_capa_url,
        'imagens_detalhes_existentes': imagens_detalhes_existentes,
    })


def eliminar_hotel(request, hotel_id):
    hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                # Chamar a função SQL para eliminar
                cursor.execute("SELECT eliminar_hotel(%s)", [hotel_id])
                
            # Eliminar a imagem do MongoDB
            capa_hotel.delete_one({'hotel_id': hotel_id})
            
            # Eliminar imagens de detalhes do MongoDB
            detalhes_hotel.delete_many({'hotel_id': hotel_id})
            
            messages.success(request, "Hotel eliminado com sucesso!")
            
        except DatabaseError as e:
            # Capturar erro da função SQL
            erro_texto = str(e)
            
            # Limpar mensagem de erro
            if "CONTEXT" in erro_texto:
                erro_texto = erro_texto.split("CONTEXT")[0].strip()
            
            erro_texto = re.sub(r"^ERROR:\s*", "", erro_texto, flags=re.IGNORECASE)
            erro_texto = erro_texto.replace("Erro da base de dados:", "").strip()
            
            messages.error(request, erro_texto or "Erro ao eliminar hotel.")
        
        return redirect('hoteis')
    
    return redirect('hoteis')


def eliminar_feedback(request, feedback_id):
    """
    Elimina um feedback existente. Apenas aceita POST para prevenir exclusões via GET.
    Redireciona para a página de feedbacks do pacote correspondente.
    """
    from pacotes.models import Feedback

    feedback = get_object_or_404(Feedback, feedback_id=feedback_id)
    pacote_id = feedback.pacote.pacote_id if feedback.pacote else None

    if request.method == 'POST':
        feedback.delete()
        if pacote_id:
            return redirect('feedbacks_por_pacote', pacote_id=pacote_id)
        return redirect('feedbacks')

    # If reached by GET, redirect back safely
    if pacote_id:
        return redirect('feedbacks_por_pacote', pacote_id=pacote_id)
    return redirect('feedbacks')

def selecionar_hotel(request, hotel_id, pacote_id):
    pacote = get_object_or_404(Pacote, pacote_id=pacote_id)
    hotel = get_object_or_404(Hotel, hotel_id=hotel_id)

    if hasattr(pacote, 'hotel'):
        pacote.hotel = hotel
        pacote.save()

    # Redirecionar para a seleção de voos
    return redirect('selecionar_voo', pacote_id=pacote_id, hotel_id=hotel_id)
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

    # Buscar imagens de detalhes do MongoDB
    imagens_detalhes_raw = list(detalhes_hotel.find({'hotel_id': hotel_id}).sort('ordem', 1))
    
    # Converter _id para id (sem underscore) para uso no template
    imagens_detalhes = []
    for img in imagens_detalhes_raw:
        img['id'] = str(img['_id'])
        imagens_detalhes.append(img)
    
    return render(
        request,
        "hotel_detalhes.html",
        {
            "hotel": hotel,
            "pacote": pacote,
            "imagens_detalhes": imagens_detalhes,
        },
    )


def pacotes(request, pacote_id=None):

    pacote = get_object_or_404(Pacote, pacote_id=pacote_id) if pacote_id else None

    if request.method == "POST":
        form = PacoteForm(request.POST, request.FILES, instance=pacote)
        if form.is_valid():
            # Coletar descrições dos dias do POST
            dias_descricao = []
            i = 1
            while f'dia_{i}' in request.POST:
                dias_descricao.append(request.POST[f'dia_{i}'])
                i += 1
            
            pacote = form.save(commit=False, dias_descricao=dias_descricao)
            pacote.save()
            form.save_m2m()

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

            if pacote_id:
                messages.success(request, "Pacote atualizado com sucesso!")
            else:
                messages.success(request, "Pacote criado com sucesso!")

            return redirect('pacotes')

    else:
        form = PacoteForm(instance=pacote)

    # Processar dias existentes se estiver editando
    dias_existentes = []
    if pacote and pacote.descricao_item:
        import re
        # Dividir por qualquer formato de dia (1ºDIA, 1º DIA, 1DIA, etc.)
        partes = re.split(r'\s*(\d+)\s*[°º]?\s*DIA\s*:?\s*', pacote.descricao_item, flags=re.IGNORECASE)
        
        for i in range(1, len(partes), 2):
            if i + 1 < len(partes):
                descricao = partes[i + 1].strip()
                if descricao:
                    dias_existentes.append(descricao)

    with connection.cursor() as cursor:
        cursor.execute("SELECT pacotesToJson()")
        data = cursor.fetchone()
        pacotes_data = data[0] if (data and data[0]) else []

    return render(request, 'pacotes.html', {
        'form': form,
        'pacote_editar': pacote,  
        'data': pacotes_data,
        'pacotes': Pacote.objects.all(),
        'dias_existentes': dias_existentes,
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
    partes = re.split(r"\s*\d+\s*[°º]\s*DIA\s*:?\s*", texto, flags=re.IGNORECASE)
    partes = [p.strip().lstrip(':').strip() for p in partes if p.strip()]

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
    # Usar a materialized view mv_pacotes_full com filtros SQL diretos para aproveitar os índices
    destinos = Destino.objects.all()
    q = request.GET.get("q", "").strip()
    pais_query = request.GET.get("pais", "").strip()
    preco = request.GET.get("preco")
    mes = request.GET.get("mes")

    pacotes = []
    import json as _json
    
    sql_query = "SELECT row_to_json(p) FROM mv_pacotes_full p WHERE 1=1"
    params = []
    
    # Filtro de pesquisa de texto
    if q:
        sql_query += " AND to_tsvector('portuguese', coalesce(p.nome,'') || ' ' || coalesce(p.descricao_item,'')) @@ plainto_tsquery('portuguese', %s)"
        params.append(q)
    
    # Filtro de país 
    if pais_query:
        sql_query += " AND p.destinos @> %s::jsonb"
        params.append(_json.dumps([{"pais": pais_query}]))
    
    # Filtro de preço 
    if preco:
        sql_query += " AND p.preco_total <= %s"
        params.append(float(preco))
    
    # Filtro de mês
    if mes:
        sql_query += " AND EXTRACT(MONTH FROM p.data_inicio) = %s"
        params.append(int(mes))
    
    with connection.cursor() as cursor:
        try:
            cursor.execute(sql_query, params)
            rows = cursor.fetchall()
            pacotes = [row[0] for row in rows]
            # se o adaptador retornar string, parse
            if pacotes and isinstance(pacotes[0], (str, bytes)):
                pacotes = [_json.loads(p) if isinstance(p, (str, bytes)) else p for p in pacotes]
        except Exception as e:
            pacotes = []

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

    # Buscar imagens dos hotéis do MongoDB
    hoteis_com_imagem = []
    for hotel in hoteis:
        hotel_dict = {
            'hotel_id': hotel.hotel_id,
            'nome': hotel.nome,
            'endereco': hotel.endereco,
            'preco_diario': hotel.preco_diario,
            'descricao_item': hotel.descricao_item,
            'tem_imagem': False
        }
        
        # Verificar se existe imagem no MongoDB
        imagem_doc = capa_hotel.find_one({'hotel_id': hotel.hotel_id})
        if imagem_doc:
            hotel_dict['tem_imagem'] = True
        
        hoteis_com_imagem.append(hotel_dict)

    return render(request, "reserva_pacote.html", {
        "pacote": pacote,
        "hoteis": hoteis_com_imagem,
    })


def hotel_imagem(request, hotel_id):
    """
    Serve a imagem de capa do hotel armazenada no MongoDB.
    """
    from django.http import HttpResponse, Http404
    
    # Buscar a imagem no MongoDB
    imagem_doc = capa_hotel.find_one({'hotel_id': hotel_id})
    
    if not imagem_doc or 'imagem' not in imagem_doc:
        raise Http404("Imagem não encontrada")
    
    # Retornar a imagem com o content type correto
    response = HttpResponse(imagem_doc['imagem'], content_type=imagem_doc.get('content_type', 'image/jpeg'))
    return response


def hotel_imagem_detalhe(request, hotel_id, imagem_id):
    """
    Serve uma imagem de detalhe do hotel armazenada no MongoDB.
    """
    # Buscar a imagem no MongoDB usando o _id
    try:
        imagem_doc = detalhes_hotel.find_one({'_id': ObjectId(imagem_id), 'hotel_id': hotel_id})
    except:
        raise Http404("Imagem não encontrada")
    
    if not imagem_doc or 'imagem' not in imagem_doc:
        raise Http404("Imagem não encontrada")
    
    # Retornar a imagem com o content type correto
    response = HttpResponse(imagem_doc['imagem'], content_type=imagem_doc.get('content_type', 'image/jpeg'))
    return response


def selecionar_voo_view(request, pacote_id, hotel_id):
    """
    Exibe a lista de voos disponíveis para o pacote selecionado.
    """
    pacote = get_object_or_404(Pacote, pacote_id=pacote_id)
    hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
    
    # Buscar destinos do pacote
    destinos_do_pacote = pacote.destinos.all()
    
    # Buscar voos para os destinos do pacote
    voos = Voo.objects.filter(destino__in=destinos_do_pacote)
    
    return render(request, "selecionar_voo.html", {
        "pacote": pacote,
        "hotel": hotel,
        "voos": voos,
    })


def confirmar_voo(request, voo_id, pacote_id, hotel_id):
    """
    Processa a seleção do voo e redireciona para a confirmação final.
    """
    pacote = get_object_or_404(Pacote, pacote_id=pacote_id)
    voo = get_object_or_404(Voo, voo_id=voo_id)
    hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
    
    # Calcular número de noites
    num_noites = (pacote.data_fim - pacote.data_inicio).days
    
    # Calcular preços
    preco_hotel_total = hotel.preco_diario * num_noites
    preco_voo_total = voo.preco
    preco_base_pacote = pacote.preco_total
    
    # Calcular preço total final
    preco_total_final = preco_base_pacote + preco_hotel_total + preco_voo_total
    
    # Aqui você pode salvar a escolha do voo na sessão ou em um modelo
    # Por exemplo: request.session['voo_selecionado'] = voo_id
    
    # Por enquanto, vamos apenas renderizar uma página de confirmação
    # ou redirecionar para a próxima etapa do processo de reserva
    
    return render(request, "confirmacao_pacote.html", {
        "pacote": pacote,
        "voo": voo,
        "hotel": hotel,
        "num_noites": num_noites,
        "preco_hotel_total": preco_hotel_total,
        "preco_voo_total": preco_voo_total,
        "preco_base_pacote": preco_base_pacote,
        "preco_total_final": preco_total_final,
    })