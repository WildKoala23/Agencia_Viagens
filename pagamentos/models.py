from django.db import models
from users.models import Utilizador

# Create your models here.
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
        'pacotes.Pacote', 
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