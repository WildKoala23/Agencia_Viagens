from django.db import models

"""
Class para o modelo de dados Pagamento:

Representa um pagamento realizado no sistema de reservas.

Attributes:
    pagamento_id (AutoField): Identificador único do pagamento (chave primária).
    compra_id (IntegerField): Identificador da compra associada ao pagamento (deveria ser ForeignKey).
    data_pagamento (DateField): Data em que o pagamento foi realizado.
    valor (DecimalField): Valor do pagamento com até 10 dígitos e 2 casas decimais.
    estado (TextField): Estado do pagamento (ex: 'pendente', 'aprovado', 'rejeitado', 'cancelado').
    metodo (TextField): Método de pagamento utilizado (ex: 'cartão de crédito', 'MBWay', 'transferência').

Meta:
    managed (bool): False - Django não gerencia a criação/alteração da tabela.
    db_table (str): 'pagamento' - Nome da tabela no banco de dados PostgreSQL.

Methods:
    __str__(): Retorna uma representação em string do pagamento no formato 
               'Pagamento {pagamento_id} - {valor}€ em {data_pagamento}'.
"""

class Pagamento(models.Model):
    pagamento_id = models.AutoField(primary_key=True)
    compra_id = models.IntegerField()  # Should be FK to Compra
    data_pagamento = models.DateField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)  
    estado = models.TextField()
    metodo = models.TextField()
    
    class Meta:
        managed = False
        db_table = 'pagamento'
       
    def __str__(self):
        return f"Pagamento {self.pagamento_id} - {self.valor}€ em {self.data_pagamento}"