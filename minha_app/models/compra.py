from django.db import models
from .utilizador import Utilizador
from .pacote import Pacote

"""
Class para o modelo de dados Compra:

Representa uma compra realizada por um utilizador no sistema de reservas.

Attributes:
    compra_id (AutoField): Identificador único da compra (chave primária).
    pagamento_id (IntegerField): Identificador do pagamento associado à compra.
    fatura_id (IntegerField): Identificador da fatura associada à compra.
    user_id (ForeignKey): Referência ao utilizador que realizou a compra.
    pacote_id (ForeignKey): Referência ao pacote adquirido na compra.
    data_compra (DateField): Data em que a compra foi realizada.
    valor_total (DecimalField): Valor total da compra com até 10 dígitos e 2 casas decimais.
    estado (TextField): Estado atual da compra (ex: 'pendente', 'confirmada', 'cancelada').

Meta:
    managed (bool): False - Django não gerencia a criação/alteração da tabela.
    db_table (str): 'compra' - Nome da tabela no banco de dados PostgreSQL.

Methods:
    __str__(): Retorna uma representação em string da compra no formato 
               'Compra {compra_id} - {utilizador} - {valor_total}€'.
"""
class Compra(models.Model):
    compra_id = models.AutoField(primary_key=True)
    pagamento_id = models.IntegerField()
    fatura_id = models.IntegerField()
    user = models.ForeignKey(
        Utilizador, 
        on_delete=models.CASCADE,
        db_column='user_id'
    )
    pacote = models.ForeignKey(
        Pacote, 
        on_delete=models.CASCADE,
        db_column='pacote_id'
    )
    data_compra = models.DateField()
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.TextField()
    
    class Meta:
        managed = False
        db_table = 'compra'
    
    def __str__(self):
        return f"Compra {self.compra_id} - {self.user.username} - {self.valor_total}€"