"""
URL configuration for appPrincipal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
#from django.contrib.auth import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
urlpatterns = [
    path('reportes/admin/', admin.site.urls),
    path('reportes/', include('login.urls')),
    path('reportes/', include('reportesRobert.urls')),
    path('reportes/accounts/', include('django.contrib.auth.urls')),
    #path('login/', views.LoginView.as_view(template_name='login.html'), name='login'),
    #path('logout/', views.LogoutView.as_view(next_page='/'), name='logout'),
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)