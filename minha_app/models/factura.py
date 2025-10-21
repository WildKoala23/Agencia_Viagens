from django.db import models

"""
Class para o modelo de dados Factura:

Representa uma fatura emitida no sistema de reservas de voos.

Attributes:
    fatura_id (AutoField): Identificador único da fatura (chave primária).
    compra_id (IntegerField): Identificador da compra associada à fatura.
    pagamento_id (IntegerField): Identificador do pagamento associado à fatura.
    data_emissao (TimeField): Data e hora de emissão da fatura.
    valor_total (DecimalField): Valor total da fatura com até 10 dígitos e 2 casas decimais.

Meta:
    managed (bool): False - Django não gerencia a criação/alteração da tabela.
    db_table (str): 'fatura' - Nome da tabela no banco de dados PostgreSQL.

Methods:
    __str__(): Retorna uma representação em string da fatura no formato 
               'Factura: {id} -> {data_emissao}'.
"""
class Factura(models.Model):
    fatura_id = models.AutoField(primary_key=True)
    compra_id = models.IntegerField()
    pagamento_id = models.IntegerField()
    data_emissao = models.TimeField()
    valor_total = models.DecimalField(max_digits=10, decimal_places=2) 

    class Meta:
        managed = False
        db_table = 'fatura'

    def __str__(self):
        return f'Factura: {self.fatura_id} -> {self.data_emissao}'