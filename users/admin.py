from django.contrib import admin
from .models import TipoUser, Utilizador


@admin.register(TipoUser)
class TipoUserAdmin(admin.ModelAdmin):
    list_display = ('tipo_user_id', 'descricao_item')
    search_fields = ('descricao_item',)


@admin.register(Utilizador)
class UtilizadorAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'nome', 'email', 'tipo_user', 'telefone')
    search_fields = ('nome', 'email')
    list_filter = ('tipo_user',)
