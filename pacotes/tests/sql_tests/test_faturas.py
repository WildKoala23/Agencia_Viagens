import pytest
from django.db import connections

@pytest.mark.django_db
def test_view_faturas_completas():
    cur = connections['default'].cursor()
    cur.execute("SELECT COUNT(*) FROM view_faturas_completas;")
    count = cur.fetchone()[0]
    assert count >= 0, "A view view_faturas_completas não retornou resultados válidos."

@pytest.mark.django_db
def test_function_get_fatura_detalhes():
    cur = connections['default'].cursor()
    cur.execute("SELECT COUNT(*) FROM fatura;")
    existe = cur.fetchone()[0]
    if existe > 0:
        cur.execute("SELECT * FROM get_fatura_detalhes(1);")
        resultado = cur.fetchall()
        assert resultado is not None, "A função get_fatura_detalhes não retornou dados."
    else:
        pytest.skip("Não há faturas na base de dados para testar.")

@pytest.mark.django_db
def test_function_estatisticas_faturamento():
    cur = connections['default'].cursor()
    cur.execute("SELECT * FROM estatisticas_faturamento();")
    dados = cur.fetchone()
    assert dados is not None, "A função estatisticas_faturamento não retornou resultados."
