from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
# Create your models here.

class UtilizadorManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser deve ter is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

    
class Utilizador(AbstractUser):
    username = None  # Remove username field completely
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=100, unique=True)
    telefone = models.IntegerField(null=True, blank=True)
    firstname = models.CharField(max_length=150)
    lastname = models.CharField(max_length=150)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname']
    
    objects = UtilizadorManager() 
    
    class Meta:
        db_table = 'utilizador'
    
    def __str__(self):
        return self.email 
    
    def save(self, *args, **kwargs):
        # Only hash if the password does not start with a Django hash prefix
        if self.password and not self.password.startswith('pbkdf2_'):
            self.set_password(self.password)
        super().save(*args, **kwargs)
