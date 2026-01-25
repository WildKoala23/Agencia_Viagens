from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from django.db.models import Q
from pymongo import MongoClient
from django.http import JsonResponse
from django.core import serializers
from django.db.models import Sum
from django.contrib.auth import authenticate, login
from django.contrib import messages
import json
from datetime import datetime
from .forms import *
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
Utilizador = get_user_model()

client = MongoClient("mongodb://localhost:27017/")
db = client["bdii_25971"]
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
                    # usuários comuns redirecionam para a dashboard do cliente
                    return redirect('users:user')
            else:
                form.add_error(None, "Email ou senha inválidos")
    else:
        form = LoginForm()
    return render(request, 'registration/login.html')


def registerUser(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Usar a procedure para registar com validações
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            firstname = form.cleaned_data.get('first_name', '')
            lastname = form.cleaned_data.get('last_name', '')
            
            # Hash da password usando Django
            from django.contrib.auth.hashers import make_password
            password_hash = make_password(password)
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM registar_utilizador_validado_wrapper(%s, %s, %s, %s, NULL)
                """, [email, password_hash, firstname, lastname])
                
                result = cursor.fetchone()
                if result:
                    sucesso, user_id, mensagem = result
                    
                    if sucesso:
                        # Login automático
                        user = authenticate(request, email=email, password=password)
                        if user is not None:
                            login(request, user)
                            messages.success(request, mensagem)
                            return redirect('users:user')
                    else:
                        messages.error(request, mensagem)
                        return render(request, 'registration/register.html', {'form': form})
            
            # Fallback: se procedure não existir, usar método antigo
            user = form.save()
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('users:user')
            else:
                return redirect('users:login')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

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
    from pacotes.models import Feedback, Pacote
    from pagamentos.models import Compra
    from datetime import datetime, timedelta
    
    user_id = req.user.user_id
    
    # Dados básicos do MongoDB (mantém compatibilidade)
    data = userData.find_one({"Id_User": user_id})
    if not data:
        data = {}
    
    # Buscar compras/viagens do usuário
    with connection.cursor() as cursor:
        # Próximas viagens (futuras)
        cursor.execute("""
            SELECT 
                c.compra_id,
                p.nome as pacote_nome,
                p.data_inicio,
                p.data_fim,
                c.valor_total,
                d.nome as destino_nome,
                d.pais
            FROM compra c
            JOIN pacote p ON c.pacote_id = p.pacote_id
            LEFT JOIN pacote_destino pd ON p.pacote_id = pd.pacote_id
            LEFT JOIN destino d ON pd.destino_id = d.destino_id
            WHERE c.user_id = %s 
            AND p.data_inicio > CURRENT_DATE
            ORDER BY p.data_inicio
            LIMIT 3
        """, [user_id])
        proximas_viagens = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
        
        # Viagens passadas (para histórico)
        cursor.execute("""
            SELECT 
                c.compra_id,
                p.nome as pacote_nome,
                p.data_inicio,
                p.data_fim,
                c.valor_total,
                d.nome as destino_nome
            FROM compra c
            JOIN pacote p ON c.pacote_id = p.pacote_id
            LEFT JOIN pacote_destino pd ON p.pacote_id = pd.pacote_id
            LEFT JOIN destino d ON pd.destino_id = d.destino_id
            WHERE c.user_id = %s 
            AND p.data_fim < CURRENT_DATE
            ORDER BY p.data_fim DESC
            LIMIT 3
        """, [user_id])
        viagens_passadas = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
        
        # Estatísticas de gastos por mês (últimos 6 meses)
        cursor.execute("""
            SELECT 
                TO_CHAR(c.data_compra, 'Mon') as mes,
                EXTRACT(MONTH FROM c.data_compra) as mes_num,
                SUM(c.valor_total) as total
            FROM compra c
            WHERE c.user_id = %s 
            AND c.data_compra >= CURRENT_DATE - INTERVAL '6 months'
            GROUP BY TO_CHAR(c.data_compra, 'Mon'), EXTRACT(MONTH FROM c.data_compra)
            ORDER BY mes_num
        """, [user_id])
        gastos_mensais = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    
    # Feedbacks recentes do usuário
    feedbacks_recentes = Feedback.objects.filter(user_id=user_id).select_related('pacote').order_by('-data_feedback')[:3]
    
    # Estatísticas gerais
    total_compras = Compra.objects.filter(user_id=user_id).count()
    total_gasto = Compra.objects.filter(user_id=user_id).aggregate(total=Sum('valor_total'))['total'] or 0
    total_feedbacks = Feedback.objects.filter(user_id=user_id).count()
    
    # Recomendações: pacotes de países não visitados
    destinos_visitados = Compra.objects.filter(
        user_id=user_id,
        pacote__data_fim__lt=datetime.now().date()
    ).values_list('pacote__destinos__pais', flat=True).distinct()
    
    pacotes_recomendados = Pacote.objects.filter(
        estado_id=1
    ).exclude(
        destinos__pais__in=destinos_visitados
    ).distinct()[:3]
    
    context = {
        "data": data,
        "brand_name": "Atlas Gateways",
        "proximas_viagens": proximas_viagens,
        "viagens_passadas": viagens_passadas,
        "gastos_mensais": gastos_mensais,
        "feedbacks_recentes": feedbacks_recentes,
        "total_compras": total_compras,
        "total_gasto": total_gasto,
        "total_feedbacks": total_feedbacks,
        "pacotes_recomendados": pacotes_recomendados,
    }
    
    return render(req, 'dashboardUser.html', context)


def comprasUser(req):
    user = get_object_or_404(Utilizador, user_id=req.user.user_id)

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM comprasUtilizador(%s)", [req.user.user_id])
        data = cursor.fetchall()
    return render(req, 'comprasUser.html', {"data": data, "user": user})

def cancelar_reserva(request, compra_id):
    """Cancela uma reserva usando a procedure cancelar_reserva_utilizador"""
    if request.method == 'POST':
        user_id = request.user.user_id
        
        try:
            with connection.cursor() as cursor:
                # Chamar a função wrapper que executa a procedure
                cursor.execute(
                    "SELECT * FROM fn_cancelar_reserva_utilizador(%s, %s)",
                    [compra_id, user_id]
                )
                result = cursor.fetchone()
                
                if result:
                    sucesso, mensagem, reembolso = result
                    
                    if sucesso:
                        messages.success(request, mensagem)
                    else:
                        messages.error(request, mensagem)
                else:
                    messages.error(request, "Erro ao processar cancelamento")
        except Exception as e:
            messages.error(request, f"Erro ao cancelar reserva: {str(e)}")
            print(f"ERRO CANCELAMENTO: {str(e)}")  # Debug
        
        return redirect('users:comprasUser')
    
    # Se não for POST, redirecionar
    return redirect('users:comprasUser')

def feedbacksUser(request):
    user = get_object_or_404(Utilizador, user_id=request.user.user_id)

    if request.method == 'POST':
        # Processar novo feedback usando a procedure validada
        reserva_id = request.POST.get('reserva_id')
        avaliacao = request.POST.get('avaliacao')
        titulo = request.POST.get('titulo')
        comentario = request.POST.get('comentario')
        
        print(f"DEBUG - Dados recebidos: user_id={request.user.user_id}, reserva_id={reserva_id}, avaliacao={avaliacao}, titulo={titulo}")
        
        try:
            with connection.cursor() as cursor:
                # Usar função wrapper que chama a procedure com validações
                cursor.execute("""
                    SELECT * FROM executar_inserir_feedback(%s, %s, %s, %s, %s)
                """, [request.user.user_id, reserva_id, avaliacao, titulo, comentario])
                
                result = cursor.fetchone()
                print(f"DEBUG - Resultado da função: {result}")
                
                if result:
                    sucesso, feedback_id, mensagem = result
                    print(f"DEBUG - Sucesso: {sucesso}, ID: {feedback_id}, Mensagem: {mensagem}")
                    if sucesso:
                        messages.success(request, mensagem)
                    else:
                        messages.error(request, mensagem)
                else:
                    messages.error(request, "Nenhum resultado retornado da função")
        except Exception as e:
            print(f"DEBUG - Erro: {str(e)}")
            messages.error(request, f"Erro ao processar feedback: {str(e)}")
        
        return redirect('users:feedbacksUser')
    
    # Buscar compras do usuário para o dropdown
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM comprasUtilizador(%s)", [request.user.user_id])
        compras = cursor.fetchall()
    
    # Buscar feedbacks anteriores do usuário
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                f.feedback_id,
                f.titulo,
                f.avaliacao,
                f.comentario,
                f.data_feedback,
                p.nome as pacote_nome
            FROM feedback f
            JOIN pacote p ON f.pacote_id = p.pacote_id
            WHERE f.user_id = %s
            ORDER BY f.data_feedback DESC
        """, [request.user.user_id])
        
        columns = [col[0] for col in cursor.description]
        feedbacks = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return render(request, 'feedbacksUser.html', {
        "compras": compras, 
        "user": user,
        "feedbacks": feedbacks
    })

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


def dashboard(request):
    from pacotes.models import Pacote, Feedback
    from pagamentos.models import Pagamento, Compra
    from users.models import Utilizador

    mongodb = globals().get('db')
    pacotes = Pacote.objects.filter(estado_id=1)[:3]

#Por alterar--------------------------------------------------#
    total_clientes = Utilizador.objects.count()
    total_compras = Compra.objects.count()
    pagamento_sum = Pagamento.objects.aggregate(total=Sum('valor'))['total']
    if pagamento_sum is None:
        lucro_total = Compra.objects.aggregate(total=Sum('valor_total'))['total'] or 0
    else:
        lucro_total = pagamento_sum

    total_feedbacks = Feedback.objects.count()

    try:
        if mongodb is not None:
            if 'dashboard_stats' in mongodb.list_collection_names():
                doc = mongodb.dashboard_stats.find_one(sort=[('updated_at', -1)]) or mongodb.dashboard_stats.find_one()
                if doc:
                    total_clientes = doc.get('total_clientes', total_clientes)
                    total_compras = doc.get('total_compras', total_compras) or doc.get('total_reservas', total_compras)
                    lucro_total = doc.get('lucro_total', float(lucro_total))
                    total_feedbacks = doc.get('total_feedbacks', total_feedbacks) or doc.get('feedbacks', total_feedbacks)
            else:
                if 'utilizadores' in mongodb.list_collection_names():
                    try:
                        total_clientes = mongodb.utilizadores.count_documents({})
                    except Exception:
                        pass
                if 'compras' in mongodb.list_collection_names():
                    try:
                        total_compras = mongodb.compras.count_documents({})
                    except Exception:
                        pass
                if 'pagamentos' in mongodb.list_collection_names():
                    try:
                        agg = list(mongodb.pagamentos.aggregate([{'$group': {'_id': None, 'sum': {'$sum': '$valor'}}}]))
                        if agg:
                            lucro_total = agg[0].get('sum', float(lucro_total))
                    except Exception:
                        pass
                if 'feedbacks' in mongodb.list_collection_names():
                    try:
                        total_feedbacks = mongodb.feedbacks.count_documents({})
                    except Exception:
                        pass
    except Exception:
        pass
#---------------------------------------------------------------#
    pacotes_ativos = None
    pacotes_cancelados = None
    pacotes_esgotados = None
    try:
        if mongodb is not None and 'dataAdmin' in mongodb.list_collection_names():
            try:
                doc = mongodb.dataAdmin.find_one()
                if doc:
                    try:
                        pacotes_ativos = int(doc.get('NumPacotesAtivos', 0))
                    except Exception:
                        pacotes_ativos = None
                    try:
                        pacotes_cancelados = int(doc.get('NumPacotesCancelados', 0))
                    except Exception:
                        pacotes_cancelados = None
                    try:
                        pacotes_esgotados = int(doc.get('NumPacotesEsgotados', 0))
                    except Exception:
                        pacotes_esgotados = None
            except Exception:
                pass
    except Exception:
        pass

    aval1 = aval2 = aval3 = aval4 = aval5 = 0
    try:
        if mongodb is not None and 'dataAdmin' in mongodb.list_collection_names():
            try:
                rdoc = mongodb.dataAdmin.find_one({'NumAval1': {'$exists': True}})
                if not rdoc:
                    rdoc = mongodb.dataAdmin.find_one()
                if rdoc:
                    try:
                        aval1 = int(rdoc.get('NumAval1', 0))
                    except Exception:
                        aval1 = 0
                    try:
                        aval2 = int(rdoc.get('NumAval2', 0))
                    except Exception:
                        aval2 = 0
                    try:
                        aval3 = int(rdoc.get('NumAval3', 0))
                    except Exception:
                        aval3 = 0
                    try:
                        aval4 = int(rdoc.get('NumAval4', 0))
                    except Exception:
                        aval4 = 0
                    try:
                        aval5 = int(rdoc.get('NumAval5', 0))
                    except Exception:
                        aval5 = 0
            except Exception:
                pass
    except Exception:
        pass

    context = {
        'total_clientes': total_clientes,
        'total_compras': total_compras,
        'lucro_total': lucro_total,
        'total_feedbacks': total_feedbacks,
        'pacotes': pacotes,
        'pacotes_ativos': pacotes_ativos,
        'pacotes_cancelados': pacotes_cancelados,
        'pacotes_esgotados': pacotes_esgotados,
        'aval1': aval1,
        'aval2': aval2,
        'aval3': aval3,
        'aval4': aval4,
        'aval5': aval5,
    }
    
    # Buscar estatísticas de preços usando a VIEW SQL
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM vw_estatisticas_precos")
            columns = [col[0] for col in cursor.description]
            estatisticas_precos = [dict(zip(columns, row)) for row in cursor.fetchall()]
            context['estatisticas_precos'] = estatisticas_precos
    except Exception:
        context['estatisticas_precos'] = []
    
    return render(request, 'dashboard.html', context)

def api_pacotes_por_pais(request):
    try:
        mongodb = globals().get('db')
        if mongodb is not None and 'dataAdminPais' in mongodb.list_collection_names():
            cursor = mongodb.dataAdminPais.find()
            response_data = {}
            for document in cursor:
                for key, value in document.items():
                    if key in ('_id', 'updated_at'):
                        continue
                    # ensure numeric type (DB may store strings)
                    try:
                        num = int(value)
                    except Exception:
                        try:
                            num = int(float(value))
                        except Exception:
                            num = 0
                    response_data[key] = response_data.get(key, 0) + num
            return JsonResponse(response_data)
    except Exception as e:
        print(f"Error fetching data: {e}")
    return JsonResponse({}, status=500)