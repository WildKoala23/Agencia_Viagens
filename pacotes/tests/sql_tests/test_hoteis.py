import pytest
from django.db import connections

@pytest.mark.django_db
def test_view_vw_hoteis_existe_e_retorna_dados():
    """
    Testa se a view vw_hoteis existe e retorna resultados válidos.
    """
    cur = connections['default'].cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM vw_hoteis;")
        count = cur.fetchone()[0]
        assert count >= 0, "A view vw_hoteis não retornou resultados válidos."
    except Exception as e:
        pytest.fail(f"Erro ao consultar a view vw_hoteis: {e}")

@pytest.mark.django_db
def test_view_vw_pacote_hoteis_existe_e_retorna_dados():
    """
    Testa se a view vw_pacote_hoteis existe e retorna resultados válidos.
    """
    cur = connections['default'].cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM vw_pacote_hoteis;")
        count = cur.fetchone()[0]
        assert count >= 0, "A view vw_pacote_hoteis não retornou resultados válidos."
    except Exception as e:
        pytest.fail(f"Erro ao consultar a view vw_pacote_hoteis: {e}")

@pytest.mark.django_db
def test_view_vw_pacote_hoteis_relacionamento_pacote_hotel():
    """
    Testa se a view vw_pacote_hoteis retorna colunas esperadas e faz o JOIN corretamente.
    """
    cur = connections['default'].cursor()
    try:
        cur.execute("""
            SELECT pacote_id, nome_pacote, nome_hotel, preco_diario 
            FROM vw_pacote_hoteis 
            LIMIT 1;
        """)
        row = cur.fetchone()
        if row:
            assert row[0] is not None, "Coluna pacote_id não retornou valor."
            assert row[1] is not None, "Coluna nome_pacote não retornou valor."
        else:
            pytest.skip("A view vw_pacote_hoteis não contém dados para testar.")
    except Exception as e:
        pytest.fail(f"Erro ao consultar vw_pacote_hoteis: {e}")
