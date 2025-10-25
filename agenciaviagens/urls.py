from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),        
    path('pacotes/', include('pacotes.urls')), 
    path('pagamentos/', include('pagamentos.urls')),
    path('users/', include('users.urls')),
]