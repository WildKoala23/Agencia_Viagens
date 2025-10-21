from django.db import models


class Destino(models.Model):
    destino_id = models.AutoField(primary_key=True)
    descricao = models.TextField(null=True, blank=True)
    pais = models.TextField()
    cidade = models.TextField()
    descricao = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'destino'

    def __str__(self):
            return f"{self.cidade}, {self.pais}"