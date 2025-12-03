from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from django.db.models import Q
from pymongo import MongoClient
from django.http import JsonResponse
from django.core import serializers
from django.db.models import Sum
from django.contrib.auth import authenticate, login
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
                    # usuários comuns redirecionam para a página pública 'home'
                    return redirect('main:home')
            else:
                form.add_error(None, "Email ou senha inválidos")
    else:
        form = LoginForm()
    return render(request, 'registration/login.html')


def registerUser(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user = authenticate(request, email=email, password=password)
            form.save()
            return redirect('main:dashboard')
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
    data = userData.find_one({"Id_User": req.user.user_id})
    # data = list(userData.find())
    print(data)
    return render(req, 'dashboardUser.html', {"data": data, "brand_name": "Atlas Gateways"})


def comprasUser(req):
    user = get_object_or_404(Utilizador, user_id=req.user.user_id)

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM comprasUtilizador(%s)", [req.user.user_id])
        data = cursor.fetchall()
    return render(req, 'comprasUser.html', {"data": data, "user": user})

def feedbacksUser(request):
    user = get_object_or_404(Utilizador, user_id=request.user.user_id)

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM comprasUtilizador(%s)", [request.user.user_id])
        compras = cursor.fetchall()

    return render(request, 'feedbacksUser.html', {"compras": compras, "user": user})

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
                    if key != '_id':
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