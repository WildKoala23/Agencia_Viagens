import pytest
from django.db import connections

@pytest.mark.django_db
def test_procedure_inserir_utilizador():
    cur = connections['default'].cursor()
    cur.execute("BEGIN;")
    try:
        cur.execute("""
            CALL sp_inserir_utilizador(1, 'Teste Pytest', 'pytest_user@example.com', 'Rua Teste', 912345678);
        """)
        cur.execute("SELECT COUNT(*) FROM utilizador WHERE email = 'pytest_user@example.com';")
        count = cur.fetchone()[0]
        assert count == 1, "A procedure sp_inserir_utilizador não inseriu o utilizador corretamente."
    finally:
        cur.execute("ROLLBACK;")

@pytest.mark.django_db
def test_trigger_check_telefone_invalido():
    cur = connections['default'].cursor()
    cur.execute("BEGIN;")
    try:
        with pytest.raises(Exception):
            cur.execute("""
                INSERT INTO utilizador(tipo_user_id, nome, email, endereco, telefone)
                VALUES (1, 'Teste Telefone', 'invalido@example.com', 'Rua A', 123);
            """)
    finally:
        cur.execute("ROLLBACK;")
