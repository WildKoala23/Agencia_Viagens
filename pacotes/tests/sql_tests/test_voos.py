import pytest
from django.db import connections

@pytest.mark.django_db
def test_trigger_verificar_voo_valida_dados():
    cur = connections['default'].cursor()
    cur.execute("BEGIN;")
    try:
        with pytest.raises(Exception):
            cur.execute("""
                INSERT INTO voo (companhia, numero_voo, destino_id, data_saida, data_chegada, preco)
                VALUES ('', NULL, NULL, NOW(), NOW(), -10);
            """)
    finally:
        cur.execute("ROLLBACK;")
