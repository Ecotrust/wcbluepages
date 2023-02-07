"""bluepages URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import path, re_path, include
from app import urls as app_urls
from app.views import adminSuggestionReviewMenu, adminSuggestionRejection
from app.models import Contact, Region, Record, Entity

contact_dict = {
    'queryset': Contact.objects.all(),
    'date_field': 'date_modified',
}

urlpatterns = [
    path('admin/app/contactsuggestion/<int:suggestion_id>/review-suggestion/', adminSuggestionReviewMenu),
    path('admin/app/contactsuggestion/<int:suggestion_id>/reject/', adminSuggestionRejection),
    path('admin/', admin.site.urls),

    path('sitemap.xml', sitemap, {'sitemaps': {'contact': GenericSitemap(contact_dict)}}, name='django.contrib.sitemaps.views.sitemap'),

    re_path(r'', include(app_urls)),
]
