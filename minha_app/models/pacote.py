from django.db import models
from .destino import Destino
from .voos import Voo
from .hotel import Hotel

class Pacote(models.Model):
    pacote_id = models.AutoField(primary_key=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2) 
    descricao = models.TextField(null=True, blank=True)
    destino = models.ForeignKey(Destino, on_delete=models.CASCADE)
    voo = models.ForeignKey(Voo, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'pacote'

    def __str__(self):
        return f"Pacote {self.destino} - {self.preco}€"