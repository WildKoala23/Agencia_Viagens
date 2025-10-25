from django.db import models
"""
Class para o modelo de dados Destino:

Representa um destino de viagem disponível no sistema de reservas de voos.

Attributes:
    destino_id (AutoField): Identificador único do destino (chave primária).
    pais (TextField): País onde o destino está localizado.
    nome (TextField): Nome do destino (cidade ou localidade).

Meta:
    managed (bool): False - Django não gerencia a criação/alteração da tabela.
    db_table (str): 'destino' - Nome da tabela no banco de dados PostgreSQL.

Methods:
    __str__(): Retorna uma representação em string do destino no formato 
               '{nome}, {pais}'.
"""

class Destino(models.Model):
    destino_id = models.AutoField(primary_key=True)
    pais = models.TextField()
    nome = models.TextField()

    class Meta:
        managed = False
        db_table = 'destino'

    def __str__(self):
            return f"{self.cidade}, {self.pais}"