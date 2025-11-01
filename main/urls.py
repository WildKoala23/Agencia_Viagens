from django.urls import path
from . import views
from django.conf.urls.static import static 
from django.conf import settings
urlpatterns = [
    path("", views.home, name="home"),
      path('dashboard/', views.dashboard, name='dashboard'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)