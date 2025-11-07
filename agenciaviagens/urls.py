from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf.urls.static import static 
from django.conf import settings
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),        
    path('pacotes/', include('pacotes.urls')), 
    path('pagamentos/', include('pagamentos.urls')),
    path('users/', include('users.urls')),
    path('users/', include('django.contrib.auth.urls')),
]
if settings.DEBUG:
 urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)