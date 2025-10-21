from django.db import models
from .pagamento import Pagamento

class Fatura(models.Model):
    fatura_id = models.AutoField(primary_key=True)
    data_emissao = models.DateField()
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)  
    pagamento = models.ForeignKey(Pagamento, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'fatura'

    def __str__(self):
        return f"Fatura {self.fatura_id} - {self.valor_total}€ ({self.data_emissao})"