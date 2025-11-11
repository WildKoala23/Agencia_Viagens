from django.db import models

class Pacote(models.Model):
    pacote_id = models.AutoField(primary_key=True)
    nome = models.TextField()
    descricao_item = models.TextField()
    data_inicio = models.DateField()
    data_fim = models.DateField()
    preco_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.TextField()
    imagem = models.ImageField(upload_to='pacotes/', blank=True, null=True)
    destinos = models.ManyToManyField('Destino', through='PacoteDestino', related_name='pacotes')

    class Meta:
        db_table = 'pacote'

    def __str__(self):
        return f"{self.nome} - {self.preco_total}€"

    
class PacoteView(models.Model):
    pacote_id = models.AutoField(primary_key=True)
    nome = models.TextField()
    descricao_item = models.TextField()
    data_inicio = models.DateField()
    data_fim = models.DateField()
    preco_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.TextField()
    imagem = models.TextField()

    class Meta:
        managed = False
        db_table = 'pacote_view'

    def __str__(self):
        return f"{self.nome} - {self.preco_total}€"
    

class Destino(models.Model):
    destino_id = models.AutoField(primary_key=True)
    pais = models.TextField()
    nome = models.TextField()

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
    data_saida = models.DateTimeField()
    data_chegada = models.DateTimeField()
    preco = models.DecimalField(max_digits=19, decimal_places=2, db_column='preco')
    
    class Meta:
        db_table = 'voo'
    
    def __str__(self):
        return f"{self.origem} -> {self.destino} - {self.companhia} {self.numero_voo} ({self.data_saida})"


class Hotel(models.Model):
    hotel_id = models.AutoField(primary_key=True)
    destino_id = models.ForeignKey(
        Destino, 
        on_delete=models.CASCADE,
        db_column='destino_id'
    )
    nome = models.CharField(max_length=200)
    endereco = models.TextField(null=True, blank=True)
    preco_diario = models.DecimalField(max_digits=10, decimal_places=2)
    descricao_item = models.TextField()
    
    class Meta:
        db_table = 'hotel'
    
    def __str__(self):
        return self.nome
    

class PacoteDestino(models.Model):
    destino_id = models.ForeignKey(
        Destino, 
        on_delete=models.CASCADE,
        db_column='destino_id',
        primary_key=True
    )
    pacote_id = models.ForeignKey(
        Pacote, 
        on_delete=models.CASCADE,
        db_column='pacote_id'
    )
    
    class Meta:
        db_table = 'pacote_destino'
        unique_together = (('pacote_id', 'destino_id'),)
        managed = False
       
    def __str__(self):
        return f"Pacote {self.pacote_id.pacote_id} -> Destino {self.destino_id.nome}"

    

class PacoteHotel(models.Model):
    hotel_id = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        db_column='hotel_id',
        primary_key=True
    )
    pacote_id = models.ForeignKey(
        Pacote,
        on_delete=models.CASCADE,
        db_column='pacote_id'
    )
    
    class Meta:
        db_table = 'pacote_hotel'
        unique_together = (('pacote_id', 'hotel_id'),)  # Composite primary key
        managed = False
    
    def __str__(self):
        return f"Pacote {self.pacote_id.pacote_id} -> Hotel {self.hotel_id.nome}"
    
class PacoteVoo(models.Model):
    voo_id = models.ForeignKey(
        Voo,
        on_delete=models.CASCADE,
        db_column='voo_id',
        primary_key=True
    )
    pacote_id = models.ForeignKey(
        Pacote,
        on_delete=models.CASCADE,
        db_column='pacote_id'
    )
   
    class Meta:
        
        db_table = 'pacote_voo'
        unique_together = (('pacote_id', 'voo_id'),)  # Composite primary key
        managed = False
    
    def __str__(self):
        return f"Pacote {self.pacote_id.pacote_id} -> Voo {self.voo_id.numero_voo}"
    
class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    pacote = models.ForeignKey(
        'pacotes.Pacote', 
        on_delete=models.CASCADE,
        db_column='pacote_id'
    )
    avaliacao = models.IntegerField()
    comentario = models.TextField()
    data_feedback = models.DateField()
    
    class Meta:
        db_table = 'feedback'
    
    def __str__(self):
        return f"Feedback sobre {self.pacote} - {self.avaliacao}/5"
    
