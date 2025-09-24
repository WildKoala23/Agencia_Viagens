from django.db import models

class Cliente(models.Model):
    cliente_id = models.AutoField(primary_key=True)   # deixa o Postgres gerar
    nome = models.TextField()
    idade = models.IntegerField(null=True, blank=True)
    nif = models.IntegerField(unique=True, null=True, blank=True)
    morada = models.TextField(null=True, blank=True)
    email = models.TextField(unique=True, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'cliente'


class Destino(models.Model):
    destino_id = models.IntegerField(primary_key=True)
    pais = models.TextField()
    cidade = models.TextField()
    descricao = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'destino'


class Voo(models.Model):
    voo_id = models.AutoField(primary_key=True)
    data_voo = models.DateField()
    hora_partida = models.TimeField()
    hora_chegada = models.TimeField()
    duracao = models.DurationField(null=True, blank=True)
    origem = models.CharField(max_length=100)
    porta_embarque = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'voo'


class Hotel(models.Model):
    hotel_id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=200)
    morada = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'hotel'


class Pacote(models.Model):
    pacote_id = models.AutoField(primary_key=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)  # MONEY → Decimal
    descricao = models.TextField(null=True, blank=True)
    destino = models.ForeignKey(Destino, on_delete=models.CASCADE)
    voo = models.ForeignKey(Voo, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'pacote'


class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    data_feedback = models.DateField()
    avaliacao = models.IntegerField()
    comentario = models.TextField(null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    pacote = models.ForeignKey(Pacote, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'feedback'


class Reserva(models.Model):
    reserva_id = models.AutoField(primary_key=True)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    pacote = models.ForeignKey(Pacote, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'reserva'


class Pagamento(models.Model):
    pagamento_id = models.AutoField(primary_key=True)
    data_pagamento = models.DateField()
    montante = models.DecimalField(max_digits=10, decimal_places=2)  # MONEY → Decimal
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'pagamento'


class Fatura(models.Model):
    fatura_id = models.AutoField(primary_key=True)
    data_emissao = models.DateField()
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)  # MONEY → Decimal
    pagamento = models.ForeignKey(Pagamento, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'fatura'
