from django.urls import path
from . import views 
from django.conf.urls.static import static 
from django.conf import settings
from django.urls import path, include
app_name = 'main' # Enables namespace to use in other apps

urlpatterns = [
    path("", views.home, name="home"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("", include("pacotes.urls")), 
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)