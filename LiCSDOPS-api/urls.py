"""LiCSDOPS-api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from api import views

urlpatterns = [
    path('api/admin', admin.site.urls),
    path('', views.root),
    path('api/coughs', views.Coughs.as_view(), name='coughs'),
    path('api/cough', views.Cough.as_view(), name='cough'),
    path('api/music/generate', views.MusicGenerate.as_view(), name='music_generate'),
    path('api/musics', views.Musics.as_view(), name='music'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
