from django.db import models

"""
Class para o modelo de dados Voo:

Representa um voo disponível no sistema de reservas.

Attributes:
    voo_id (AutoField): Identificador único do voo (chave primária).
    destino_id (IntegerField): Identificador do destino (deveria ser ForeignKey para Destino).
    companhia (TextField): Nome da companhia aérea.
    numero_voo (IntegerField): Número do voo.
    data_saida (DateField): Data de partida do voo.
    data_chegada (DateField): Data de chegada do voo.
    origem (TextField): Local de origem do voo.
    destino (TextField): Local de destino do voo.
    preco (DecimalField): Preço do voo com até 19 dígitos e 2 casas decimais.

Meta:
    managed (bool): False - Django não gerencia a criação/alteração da tabela.
    db_table (str): 'voo' - Nome da tabela no banco de dados PostgreSQL.

Methods:
    __str__(): Retorna uma representação em string do voo no formato 
               '{origem} -> {destino} - {companhia} {numero_voo} ({data_saida})'.
"""

class Voo(models.Model):
    voo_id = models.AutoField(primary_key=True)
    destino_id = models.IntegerField()  # Should be FK to Destino
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
        return f"{self.origem} -> {self.destino} - {self.companhia} {self.numero_voo} ({self.data_saida})"