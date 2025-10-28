from django.db import models


class FacturaLinha(models.Model):
    fatura_linha_id = models.AutoField(primary_key=True)
    descricao = models.TextField(blank=True, null=True, db_column='descricao')
    quantidade = models.IntegerField(blank=True, null=True)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    class Meta:
        db_table = 'fatura_linha'
       
    def __str__(self):
        return f"Linha {self.fatura_linha_id} - {self.descricao}: {self.preco_unitario}€"


class Compra(models.Model):
    compra_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        'users.Utilizador', 
        on_delete=models.CASCADE,
        db_column='user_id'
    )
    data_compra = models.DateField()
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'compra'
    
    def __str__(self):
        return f"Compra {self.compra_id} - {self.user.nome} - {self.valor_total}€"


class Pagamento(models.Model):
    pagamento_id = models.AutoField(primary_key=True)
    compra = models.ForeignKey(
        Compra,
        on_delete=models.CASCADE,
        db_column='compra_id'
    )
    data_pagamento = models.DateField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)  
    estado = models.TextField(blank=True, null=True)
    metodo = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'pagamento'
       
    def __str__(self):
        return f"Pagamento {self.pagamento_id} - {self.valor}€ - {self.estado}"


class Factura(models.Model):
    fatura_id = models.AutoField(primary_key=True)
    compra = models.ForeignKey(
        Compra,
        on_delete=models.CASCADE,
        db_column='compra_id'
    )
    pagamento = models.ForeignKey(
        Pagamento,
        on_delete=models.CASCADE,
        db_column='pagamento_id'
    )
    data_emissao = models.TimeField()
    valor_total = models.DecimalField(max_digits=10, decimal_places=2) 

    class Meta:
        db_table = 'fatura'

    def __str__(self):
        return f'Factura: {self.fatura_id} - {self.valor_total}€'
