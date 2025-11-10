from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Utilizador
from django.contrib.admin.sites import AdminSite

class DebugAdminSite(AdminSite):
    def login(self, request, extra_context=None):
        print("ADMIN DEBUG: Request POST:", request.POST)
        return super().login(request, extra_context)

admin_site = DebugAdminSite()
# Register your models here.
admin.site.register(Utilizador)