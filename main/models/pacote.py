from django.db import models
from .fatura_linha import FacturaLinha

"""
Class para o modelo de dados Pacote:

Representa um pacote de viagem disponível no sistema.

Attributes:
    pacote_id (AutoField): Identificador único do pacote (chave primária).
    fatura_linha (ForeignKey): Referência à linha de fatura associada ao pacote.
    nome (TextField): Nome do pacote de viagem.
    descricao_item (TextField): Descrição detalhada do pacote e seus serviços incluídos.
    data_inicio (DateField): Data de início do pacote de viagem.
    data_fim (DateField): Data de fim do pacote de viagem.
    preco_total (DecimalField): Preço total do pacote com até 10 dígitos e 2 casas decimais.
    estado (TextField): Estado atual do pacote (ex: 'disponível', 'esgotado', 'inativo').

Meta:
    managed (bool): False - Django não gerencia a criação/alteração da tabela.
    db_table (str): 'pacote' - Nome da tabela no banco de dados PostgreSQL.

Methods:
    __str__(): Retorna uma representação em string do pacote no formato 
               '{nome} - {preco_total}€'.
"""

class Pacote(models.Model):
    pacote_id = models.AutoField(primary_key=True)
    fatura_linha = models.ForeignKey(
        FacturaLinha, 
        on_delete=models.CASCADE,
        db_column='fatura_linha_id'
    )
    nome = models.TextField()
    descricao_item = models.TextField()
    data_inicio = models.DateField()
    data_fim = models.DateField()
    preco_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.TextField()
    
    class Meta:
        managed = False
        db_table = 'pacote'
    
    def __str__(self):
        return f"{self.nome} - {self.preco_total}€"