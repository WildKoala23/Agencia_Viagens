from django.db import models
from .tipo_user import TipoUser

"""
Class para o modelo de dados Utilizador:

Representa um utilizador registado no sistema de reservas.

Attributes:
    user_id (AutoField): Identificador único do utilizador (chave primária).
    tipo_user (ForeignKey): Referência ao tipo de utilizador (perfil/role).
    nome (TextField): Nome completo do utilizador.
    email (TextField): Email do utilizador.
    endereco (TextField): Endereço/morada do utilizador.
    telefone (IntegerField): Número de telefone do utilizador.

Meta:
    managed (bool): False - Django não gerencia a criação/alteração da tabela.
    db_table (str): 'utilizador' - Nome da tabela no banco de dados PostgreSQL.

Methods:
    __str__(): Retorna o nome do utilizador como representação em string.
"""

class Utilizador(models.Model):
    user_id = models.AutoField(primary_key=True)
    tipo_user = models.ForeignKey(
        TipoUser, 
        on_delete=models.CASCADE,
        db_column='tipo_user_id'
    )
    nome = models.TextField()
    email = models.TextField()
    endereco = models.TextField()
    telefone = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'utilizador'
    
    def __str__(self):
        return self.nome