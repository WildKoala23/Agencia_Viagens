from django.db import models
# Create your models here.

class TipoUser(models.Model):
    tipo_user_id = models.AutoField(primary_key=True)
    descricao_item = models.TextField()
    
    class Meta:
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
    password = models.TextField()
    
    class Meta:
        db_table = 'utilizador'
    
    def __str__(self):
        return self.nome
       
