from django.db import models
# Create your models here.

class TipoUser(models.Model):
    tipo_user_id = models.AutoField(primary_key=True)
    descricao_item = models.TextField()
    
    class Meta:
        managed = False
        db_table = 'tipo_user'
    
    def __str__(self):
        return self.descricao_item 
    
class Utilizador(models.Model):
    user_id = models.AutoField(primary_key=True)
    tipo_user = models.ForeignKey(
        TipoUser, 
        on_delete=models.CASCADE,
        db_column='tipo_user_id'
    )
    nome = models.TextField()
    email = models.TextField()
    endereco = models.TextField()
    telefone = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'utilizador'
    
    def __str__(self):
        return self.nome
       
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
        managed = False
        db_table = 'feedback'
    
    def __str__(self):
        return f"Feedback sobre {self.pacote} - {self.avaliacao}/5"