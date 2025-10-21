from django.db import models
from .factura import Factura

"""
Class para o modelo de dados FacturaLinha:

Representa uma linha individual de uma fatura, contendo detalhes de um item.

Attributes:
    fatura_linha_id (AutoField): Identificador único da linha de fatura (chave primária).
    fatura (ForeignKey): Referência à fatura à qual esta linha pertence.
    descricao_item (TextField): Descrição do item/serviço na linha da fatura.
    preco (DecimalField): Preço unitário do item com até 10 dígitos e 2 casas decimais.
    subtotal (DecimalField): Subtotal da linha (preço × quantidade) com até 10 dígitos e 2 casas decimais.

Meta:
    managed (bool): False - Django não gerencia a criação/alteração da tabela.
    db_table (str): 'fatura_linha' - Nome da tabela no banco de dados PostgreSQL.

Methods:
    __str__(): Retorna uma representação em string da linha de fatura no formato 
               'Fatura {fatura_id} - {descricao_item}: {subtotal}€'.
"""

class FacturaLinha(models.Model):
    fatura_linha_id = models.AutoField(primary_key=True)
    fatura = models.ForeignKey(
        Factura, 
        on_delete=models.CASCADE,
        db_column='fatura_id'
    )
    descricao_item = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        managed = False
        db_table = 'fatura_linha'
       
    def __str__(self):
        return f"Fatura {self.fatura.fatura_id} - {self.descricao_item}: {self.subtotal}€"