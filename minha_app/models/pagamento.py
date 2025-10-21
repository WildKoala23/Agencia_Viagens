from django.db import models
from .reservas import Reserva

class Pagamento(models.Model):
    pagamento_id = models.AutoField(primary_key=True)
    data_pagamento = models.DateField()
    montante = models.DecimalField(max_digits=10, decimal_places=2)  
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'pagamento'
        
    def __str__(self):
        return f"Pagamento {self.pagamento_id} - {self.montante}€ em {self.data_pagamento}"