from django.db import models


class Hotel(models.Model):
    hotel_id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=200)
    morada = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'hotel'

    def __str__(self):
        return self.nome