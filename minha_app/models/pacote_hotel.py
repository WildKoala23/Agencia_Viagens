from django.db import models
from .hotel import Hotel
from .pacote import Pacote

"""
Class para o modelo de dados PacoteHotel:

Representa a relação many-to-many entre Pacotes e Hotéis.

Attributes:
    hotel_id (ForeignKey): Referência ao hotel incluído no pacote (parte da chave primária composta).
    pacote_id (ForeignKey): Referência ao pacote que inclui o hotel (parte da chave primária composta).

Meta:
    managed (bool): False - Django não gerencia a criação/alteração da tabela.
    db_table (str): 'pacote_hotel' - Nome da tabela no banco de dados PostgreSQL.
    unique_together (tuple): Define a chave primária composta (pacote_id, hotel_id).

Methods:
    __str__(): Retorna uma representação em string da relação no formato 
               'Pacote {pacote_id} -> Hotel {hotel_id}'.
"""

class PacoteHotel(models.Model):
    hotel_id = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        db_column='hotel_id'
    )
    pacote_id = models.ForeignKey(
        Pacote,
        on_delete=models.CASCADE,
        db_column='pacote_id'
    )
    
    class Meta:
        managed = False
        db_table = 'pacote_hotel'
        unique_together = (('pacote_id', 'hotel_id'),)  # Composite primary key
    
    def __str__(self):
        return f"Pacote {self.pacote_id.pacote_id} -> Hotel {self.hotel_id.nome}"