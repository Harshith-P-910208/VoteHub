"""
URL configuration for college_voting project.

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
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.views.static import serve
from accounts import views as account_views
import os

urlpatterns = [
    path('student/login/', account_views.login_view, name='login'),
    path('admin/login/', account_views.admin_login_view, name='admin_login'),
    path('accounts/student/login/', lambda request: redirect('login')),
    path('accounts/admin/login/', lambda request: redirect('admin_login')),
    path('accounts/', include('accounts.urls')),
    path('', include('voting.urls')),
    path('admin/', admin.site.urls),
    # SEO files
    path('robots.txt', lambda request: serve(request, 'robots.txt', document_root=os.path.join(settings.BASE_DIR, 'static'))),
    path('sitemap.xml', lambda request: serve(request, 'sitemap.xml', document_root=os.path.join(settings.BASE_DIR, 'static'))),
    path('', account_views.landing, name='landing'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

