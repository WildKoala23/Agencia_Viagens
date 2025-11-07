from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class TipoUser(models.Model):
    tipo_user_id = models.AutoField(primary_key=True)
    descricao_item = models.TextField()
    
    class Meta:
        db_table = 'tipo_user'
    
    def __str__(self):
        return self.descricao_item 
    
class Utilizador(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, blank=True, null=True)  # Tornar username opcional
    email = models.EmailField(max_length=100, unique=True)
    telefone = models.IntegerField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Remover username dos campos obrigatórios
    
    class Meta:
        db_table = 'utilizador'
    
    def __str__(self):
        return str(self.user_id)
    
    # Override save method to hash password
    def save(self, *args, **kwargs):
        # Only hash password if it is not already hashed
        if self.pk is None or not self.password.startswith('pbkdf2_'):
            self.set_password(self.password)
        super().save(*args, **kwargs)
       
