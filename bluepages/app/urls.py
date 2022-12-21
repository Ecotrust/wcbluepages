"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/

"""
from django.urls import path, re_path, include
from app.views import home, regionJSON, regionPicker, wireframe, contactSuggestionMenu, contactSuggestionForm, recordSuggestionForm


urlpatterns = [
    re_path(r'^regions.json', regionJSON),
    re_path(r'^suggestion_form', contactSuggestionForm),
    path('contact_suggestion_menu/<int:contact_id>/', contactSuggestionMenu),
    path('contact_suggestion_menu/', contactSuggestionMenu),
    path('record_suggestion_form/<int:contact_id>/', recordSuggestionForm),
    re_path(r'^region_picker', regionPicker),
    re_path(r'^wireframe', wireframe),
    re_path(r'', home),
]
