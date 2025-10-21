from django.db import models

"""
Class para o modelo de dados TipoUser:

Representa os diferentes tipos/perfis de utilizadores no sistema.

Attributes:
    tipo_user_id (AutoField): Identificador único do tipo de utilizador (chave primária).
    descricao_item (TextField): Descrição do tipo de utilizador (ex: 'admin', 'cliente', 'gestor').

Meta:
    managed (bool): False - Django não gerencia a criação/alteração da tabela.
    db_table (str): 'tipo_user' - Nome da tabela no banco de dados PostgreSQL.

Methods:
    __str__(): Retorna uma representação em string do tipo de utilizador no formato 
               '{tipo_user_id}: {descricao_item}'.
"""

class TipoUser(models.Model):
    tipo_user_id = models.AutoField(primary_key=True)
    descricao_item = models.TextField()  # Consider renaming to 'descricao' or 'nome'
    
    class Meta:
        managed = False
        db_table = 'tipo_user'
    
    def __str__(self):
        return self.descricao_item  # Simplified - just return the description