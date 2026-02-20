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
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import path, re_path, include
from app import urls as app_urls
from app.views import adminSuggestionReviewMenu, adminSuggestionRejection
from app.models import Contact


class ContactSitemap(Sitemap):
    """Lazy sitemap that only queries database when accessed, not at import time."""

    def items(self):
        return [
            contact
            for contact in Contact.objects.filter(is_test_data=False)
            if contact.public
        ]

    def lastmod(self, obj):
        return obj.date_modified


urlpatterns = [
    path(
        "admin/app/contactsuggestion/<int:suggestion_id>/review-suggestion/",
        adminSuggestionReviewMenu,
    ),
    path(
        "admin/app/contactsuggestion/<int:suggestion_id>/reject/",
        adminSuggestionRejection,
    ),
    path("admin/", admin.site.urls),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": {"contact": ContactSitemap}},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    re_path(r"", include(app_urls)),
]
