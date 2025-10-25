from django.db import models
from .destino import Destino
from .pacote import Pacote

"""
Class para o modelo de dados PacoteDestino:

Representa a relação many-to-many entre Pacotes e Destinos.

Attributes:
    destino_id (ForeignKey): Referência ao destino associado (parte da chave primária composta).
    pacote_id (ForeignKey): Referência ao pacote associado (parte da chave primária composta).

Meta:
    managed (bool): False - Django não gerencia a criação/alteração da tabela.
    db_table (str): 'pacote_destino' - Nome da tabela no banco de dados PostgreSQL.
    unique_together (tuple): Define a chave primária composta (pacote_id, destino_id).

Methods:
    __str__(): Retorna uma representação em string da relação no formato 
               'Pacote {pacote_id} -> Destino {destino_id}'.
"""
class PacoteDestino(models.Model):
    destino_id = models.ForeignKey(
        Destino, 
        on_delete=models.CASCADE,
        db_column='destino_id'
    )
    pacote_id = models.ForeignKey(
        Pacote, 
        on_delete=models.CASCADE,
        db_column='pacote_id'
    )
    
    class Meta:
        managed = False
        db_table = 'pacote_destino'
        unique_together = (('pacote_id', 'destino_id'),)  # Composite primary key
       
    def __str__(self):
        return f"Pacote {self.pacote.pacote_id} -> Destino {self.destino.nome}"