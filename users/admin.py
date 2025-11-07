from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Utilizador

# Register your models here.
admin.site.register(Utilizador)