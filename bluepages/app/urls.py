"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/

"""
from django.urls import path, re_path, include
from app.views import home, regionJSON, regionPicker, wireframe, suggestionForm


urlpatterns = [
    re_path(r'regions.json', regionJSON),
    re_path(r'suggestion_form', suggestionForm),
    re_path(r'region_picker', regionPicker),
    re_path(r'wireframe', wireframe),
    re_path(r'', home),
]
