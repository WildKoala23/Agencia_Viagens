from django.db import models


class Destino(models.Model):
    destino_id = models.AutoField(primary_key=True)
    pais = models.TextField()
    nome = models.TextField()
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'destino'

    def __str__(self):
        return f"{self.nome}, {self.pais}"


class Voo(models.Model):
    voo_id = models.AutoField(primary_key=True)
    destino = models.ForeignKey(
        Destino, 
        on_delete=models.CASCADE,
        db_column='destino_id'
    )
    companhia = models.TextField()
    numero_voo = models.IntegerField()
    data_saida = models.DateField()
    data_chegada = models.DateField()
    origem = models.TextField()
    destino_nome = models.TextField(db_column='destino')
    preco = models.DecimalField(max_digits=19, decimal_places=2)
    
    class Meta:
        db_table = 'voo'
    
    def __str__(self):
        return f"{self.origem} -> {self.destino_nome} - {self.companhia} {self.numero_voo}"


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
    descricao_item = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'hotel'
    
    def __str__(self):
        return self.nome


class Pacote(models.Model):
    pacote_id = models.AutoField(primary_key=True)
    nome = models.TextField()
    descricao_item = models.TextField(blank=True, null=True)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    preco_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'pacote'
    
    def __str__(self):
        return f"{self.nome} - {self.preco_total}€"
    
class PacoteDestino(models.Model):
    destino = models.ForeignKey(
        Destino, 
        on_delete=models.CASCADE,
        db_column='destino_id'
    )
    pacote = models.ForeignKey(
        Pacote, 
        on_delete=models.CASCADE,
        db_column='pacote_id'
    )
    
    class Meta:
        db_table = 'pacote_destino'
        unique_together = (('pacote', 'destino'),)
       
    def __str__(self):
        return f"Pacote {self.pacote.nome} -> Destino {self.destino.nome}"
    

class PacoteHotel(models.Model):
    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        db_column='hotel_id'
    )
    pacote = models.ForeignKey(
        Pacote,
        on_delete=models.CASCADE,
        db_column='pacote_id'
    )
    
    class Meta:
        db_table = 'pacote_hotel'
        unique_together = (('pacote', 'hotel'),)
    
    def __str__(self):
        return f"Pacote {self.pacote.nome} -> Hotel {self.hotel.nome}"
    

class PacoteVoo(models.Model):
    voo = models.ForeignKey(
        Voo,
        on_delete=models.CASCADE,
        db_column='voo_id'
    )
    pacote = models.ForeignKey(
        Pacote,
        on_delete=models.CASCADE,
        db_column='pacote_id'
    )
   
    class Meta:
        db_table = 'pacote_voo'
        unique_together = (('pacote', 'voo'),)
    
    def __str__(self):
        return f"Pacote {self.pacote.nome} -> Voo {self.voo.numero_voo}"
    

class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    pacote = models.ForeignKey(
        Pacote, 
        on_delete=models.CASCADE,
        db_column='pacote_id'
    )
    avaliacao = models.IntegerField()
    comentario = models.TextField(blank=True, null=True)
    data_feedback = models.DateField()
    
    class Meta:
        db_table = 'feedback'
    
    def __str__(self):
        return f"Feedback sobre {self.pacote} - {self.avaliacao}/5"


class Reserva(models.Model):
    reserva_id = models.AutoField(primary_key=True)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    cliente = models.ForeignKey(
        'users.Utilizador',
        on_delete=models.CASCADE,
        db_column='cliente_id'
    )
    pacote = models.ForeignKey(
        Pacote,
        on_delete=models.CASCADE,
        db_column='pacote_id'
    )
    
    class Meta:
        db_table = 'reserva'
    
    def __str__(self):
        return f"Reserva {self.reserva_id} - {self.cliente.nome} - {self.pacote.nome}"

