from django.db import models
from .pacote import Pacote

"""
Class para o modelo de dados Feedback:

Representa um feedback/avaliação deixado por um cliente sobre um pacote.

Attributes:
    feedback_id (AutoField): Identificador único do feedback (chave primária).
    pacote (ForeignKey): Referência ao pacote que está sendo avaliado.
    avaliacao (IntegerField): Nota de avaliação do pacote (geralmente de 1 a 5).
    comentario (TextField): Comentário textual do cliente sobre o pacote.
    data_feedback (DateField): Data em que o feedback foi registado.

Meta:
    managed (bool): False - Django não gerencia a criação/alteração da tabela.
    db_table (str): 'feedback' - Nome da tabela no banco de dados PostgreSQL.

Methods:
    __str__(): Retorna uma representação em string do feedback no formato 
               'Feedback sobre {pacote} - {avaliacao}/5'.
"""


class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    pacote = models.ForeignKey(
        Pacote, 
        on_delete=models.CASCADE,
        db_column='pacote_id'
    )
    avaliacao = models.IntegerField()
    comentario = models.TextField()
    data_feedback = models.DateField()
    
    class Meta:
        managed = False
        db_table = 'feedback'
    
    def __str__(self):
        return f"Feedback sobre {self.pacote} - {self.avaliacao}/5"