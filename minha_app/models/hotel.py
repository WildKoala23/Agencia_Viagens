from django.db import models
from .destino import Destino

"""
Class para o modelo de dados Hotel:

Representa um hotel disponível num destino específico.

Attributes:
    hotel_id (AutoField): Identificador único do hotel (chave primária).
    destino (ForeignKey): Referência ao destino onde o hotel está localizado.
    nome (CharField): Nome do hotel (máximo 200 caracteres).
    endereco (TextField): Endereço/morada do hotel (opcional).
    preco_diario (DecimalField): Preço diário do hotel com até 10 dígitos e 2 casas decimais.
    descricao_item (TextField): Descrição detalhada do hotel e suas amenidades.

Meta:
    managed (bool): False - Django não gerencia a criação/alteração da tabela.
    db_table (str): 'hotel' - Nome da tabela no banco de dados PostgreSQL.

Methods:
    __str__(): Retorna o nome do hotel como representação em string.
"""

class Hotel(models.Model):
    hotel_id = models.AutoField(primary_key=True)
    destino = models.ForeignKey(
        Destino, 
        on_delete=models.CASCADE,
        db_column='destino_id'
    )
    nome = models.CharField(max_length=200)
    endereco = models.TextField(null=True, blank=True)
    preco_diario = models.DecimalField(max_digits=10, decimal_places=2)
    descricao_item = models.TextField()
    
    class Meta:
        managed = False
        db_table = 'hotel'
    
    def __str__(self):
        return self.nome