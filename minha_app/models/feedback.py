from django.db import models
from .destination import Destino
from .flights import Voo
from .hotel import Hotel
from .clients import Cliente
from .package import Pacote

class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    data_feedback = models.DateField()
    avaliacao = models.IntegerField()
    comentario = models.TextField(null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    pacote = models.ForeignKey(Pacote, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'feedback'

    def __str__(self):
        return f"Feedback de {self.cliente} sobre {self.pacote} - {self.avaliacao}/5"