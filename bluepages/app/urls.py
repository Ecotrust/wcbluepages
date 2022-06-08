"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/

"""

from django.urls import path, re_path, include
from app.views import home

urlpatterns = [
    
    re_path(r'', home),
]
