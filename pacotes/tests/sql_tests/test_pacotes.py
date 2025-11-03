import pytest
from django.db import connections

@pytest.mark.django_db
def test_view_pacote_view():
    cur = connections['default'].cursor()
    cur.execute("SELECT COUNT(*) FROM pacote_view;")
    count = cur.fetchone()[0]
    assert count >= 0, "A view pacote_view não retornou resultados válidos."
