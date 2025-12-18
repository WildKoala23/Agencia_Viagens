import logging
import os
from typing import Dict

from django.db.models import Count, Sum
from django.utils import timezone
from pymongo import MongoClient
from pacotes.models import Pacote

logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "bdii_25971")

def _get_mongo_db():
    """Abre uma ligação simples ao MongoDB e valida com um ping."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    db = client[MONGO_DB_NAME]
    # Validação rápida para falhas imediatas de ligação
    db.command("ping")
    return db

def _count_pacotes_por_estado() -> Dict[str, int]:
    
    ativos = cancelados = esgotados = 0
    # Conta por descrição do estado (mais robusto que assumir ids fixos)
    for row in Pacote.objects.values("estado_id__desc", "estado_id").annotate(total=Count("pacote_id")):
        desc = (row.get("estado_id__desc") or "").lower()
        total = int(row.get("total") or 0)
        if "cancel" in desc:
            cancelados += total
        elif "esgot" in desc or "sold" in desc:
            esgotados += total
        elif "ativ" in desc or "activ" in desc or "active" in desc or "dispon" in desc:
            ativos += total

    # Fallback para ids mais comuns se não encontrarmos pelo nome
    if ativos == 0:
        ativos = Pacote.objects.filter(estado_id_id=1).count()
    if cancelados == 0:
        cancelados = Pacote.objects.filter(estado_id_id=2).count()
    if esgotados == 0:
        esgotados = Pacote.objects.filter(estado_id_id=3).count()

    return {
        "NumPacotesAtivos": int(ativos),
        "NumPacotesCancelados": int(cancelados),
        "NumPacotesEsgotados": int(esgotados),
    }

def _count_feedbacks() -> Dict[str, int]:
    from pacotes.models import Feedback

    ratings = {str(i): 0 for i in range(1, 6)}
    for row in Feedback.objects.values("avaliacao").annotate(total=Count("feedback_id")):
        avaliacao = row.get("avaliacao")
        total = int(row.get("total") or 0)
        if avaliacao in (1, 2, 3, 4, 5):
            ratings[str(avaliacao)] = total
    return {
        "NumAval1": ratings.get("1", 0),
        "NumAval2": ratings.get("2", 0),
        "NumAval3": ratings.get("3", 0),
        "NumAval4": ratings.get("4", 0),
        "NumAval5": ratings.get("5", 0),
    }

def _count_pacotes_por_pais() -> Dict[str, int]:
    from pacotes.models import PacoteDestino

    pais_counts: Dict[str, int] = {}
    for row in (
        PacoteDestino.objects.values("destino_id__pais")
        .annotate(total=Count("pacote_id", distinct=True))
    ):
        pais = row.get("destino_id__pais") or "Sem pais"
        pais_counts[pais] = pais_counts.get(pais, 0) + int(row.get("total") or 0)
    return pais_counts

def sync_admin_charts_to_mongo() -> None:
    """Calcula e envia estatísticas para o MongoDB no arranque."""
    try:
        mongodb = _get_mongo_db()
    except Exception as exc:  # pragma: no cover - falha externa
        logger.warning("MongoDB indisponivel, ignorando sync inicial: %s", exc)
        return

    from users.models import Utilizador
    from pagamentos.models import Compra, Pagamento

    pacotes_estado = _count_pacotes_por_estado()
    ratings = _count_feedbacks()
    pacotes_por_pais = _count_pacotes_por_pais()

    total_clientes = Utilizador.objects.count()
    total_compras = Compra.objects.count()
    total_feedbacks = sum(ratings.values())

    pagamento_sum = Pagamento.objects.aggregate(total=Sum("valor"))
    lucro_total = float(pagamento_sum.get("total") or 0)
    if lucro_total == 0:
        compra_sum = Compra.objects.aggregate(total=Sum("valor_total"))
        lucro_total = float(compra_sum.get("total") or 0)

    stats_doc = {
        "total_clientes": int(total_clientes),
        "total_compras": int(total_compras),
        "lucro_total": float(lucro_total),
        "total_feedbacks": int(total_feedbacks),
        "updated_at": timezone.now(),
    }

    data_admin_doc = {
        **pacotes_estado,
        **ratings,
        "updated_at": timezone.now(),
    }

    try:
        mongodb.dashboard_stats.replace_one({}, stats_doc, upsert=True)
    except Exception as exc:  # pragma: no cover - falha externa
        logger.warning("Nao foi possivel atualizar dashboard_stats no MongoDB: %s", exc)

    try:
        mongodb.dataAdmin.replace_one({}, data_admin_doc, upsert=True)
    except Exception as exc:  # pragma: no cover - falha externa
        logger.warning("Nao foi possivel atualizar dataAdmin no MongoDB: %s", exc)

    try:
        mongodb.dataAdminPais.replace_one({}, pacotes_por_pais, upsert=True)
    except Exception as exc:  # pragma: no cover - falha externa
        logger.warning("Nao foi possivel atualizar dataAdminPais no MongoDB: %s", exc)
