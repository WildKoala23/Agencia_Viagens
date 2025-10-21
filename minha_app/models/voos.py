from django.db import models


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

    def __str__(self):
        return f"{self.origem} - {self.data_voo} ({self.hora_partida})"