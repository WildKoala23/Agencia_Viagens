from django.db import models
from .voos import Voo
from .pacote import Pacote


"""
Class para o modelo de dados PacoteVoo:

Representa a relação many-to-many entre Pacotes e Voos.

Attributes:
    voo_id (ForeignKey): Referência ao voo incluído no pacote (parte da chave primária composta).
    pacote_id (ForeignKey): Referência ao pacote que inclui o voo (parte da chave primária composta).

Meta:
    managed (bool): False - Django não gerencia a criação/alteração da tabela.
    db_table (str): 'pacote_voo' - Nome da tabela no banco de dados PostgreSQL.
    unique_together (tuple): Define a chave primária composta (pacote_id, voo_id).

Methods:
    __str__(): Retorna uma representação em string da relação no formato 
               'Pacote {pacote_id} -> Voo {voo_id}'.
"""

class PacoteVoo(models.Model):
    voo_id = models.ForeignKey(
        Voo,
        on_delete=models.CASCADE,
        db_column='voo_id'
    )
    pacote_id = models.ForeignKey(
        Pacote,
        on_delete=models.CASCADE,
        db_column='pacote_id'
    )
   
    class Meta:
        managed = False
        db_table = 'pacote_voo'
        unique_together = (('pacote_id', 'voo_id'),)  # Composite primary key
    
    def __str__(self):
        return f"Pacote {self.pacote_id.pacote_id} -> Voo {self.voo_id.numero_voo}"