from django.db import models


class Voo(models.Model):
    voo_id = models.AutoField(primary_key=True)
    destino_id = models.IntegerField()
    companhia = models.TextField()
    numero_voo = models.IntegerField()
    data_saida = models.DateField()
    data_chegada = models.DateField()
    origem = models.TextField()
    destino = models.TextField()
    preco = models.DecimalField(max_digits=19, decimal_places=2, db_column='preco')

    class Meta:
        managed = False
        db_table = 'voo'

    def __str__(self):
        return f"{self.origem} - {self.data_saida} ({self.data_chegada})"