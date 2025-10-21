from django.db import models


class Cliente(models.Model):
    cliente_id = models.AutoField(primary_key=True)
    nome = models.TextField()
    idade = models.IntegerField(null=True, blank=True)
    nif = models.IntegerField(unique=True, null=True, blank=True)
    morada = models.TextField(null=True, blank=True)
    email = models.TextField(unique=True, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'cliente'
    
    def __str__(self):
        return self.nome