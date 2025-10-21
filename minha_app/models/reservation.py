from django.db import models
from .clients import Cliente
from .package import Pacote


class Reserva(models.Model):
    reserva_id = models.AutoField(primary_key=True)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    pacote = models.ForeignKey(Pacote, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'reserva'

    def __str__(self):
        return f"Reserva {self.reserva_id} - {self.cliente.nome} ({self.data_inicio} a {self.data_fim})"