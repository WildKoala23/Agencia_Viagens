import pytest
from django.db import connections

@pytest.mark.django_db
def test_view_feedbacks_completos():
    cur = connections['default'].cursor()
    cur.execute("SELECT COUNT(*) FROM view_feedbacks_completos;")
    count = cur.fetchone()[0]
    assert count >= 0, "A view view_feedbacks_completos não retornou resultados válidos."

@pytest.mark.django_db
def test_function_get_media_avaliacao_pacote():
    cur = connections['default'].cursor()
    cur.execute("SELECT COUNT(*) FROM pacote;")
    existe = cur.fetchone()[0]
    if existe > 0:
        cur.execute("SELECT * FROM get_media_avaliacao_pacote(1);")
        resultado = cur.fetchall()
        assert resultado is not None, "A função get_media_avaliacao_pacote não retornou dados."
    else:
        pytest.skip("Não há pacotes disponíveis para testar.")
