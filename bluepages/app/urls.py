"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/

"""
from django.urls import path, re_path, include
from django.contrib.auth.views import PasswordResetView
from app.views import home, regionJSON, regionPicker, wireframe, getSuggestionMenu, contactSuggestionMenu, contactSuggestionForm, recordSuggestionForm, deleteSuggestedContact, deleteSuggestedRecord, getProfile, editProfile


urlpatterns = [
    re_path(r'^regions.json', regionJSON),
    path('get_suggestion_menu/', getSuggestionMenu),
    path('suggestion_form/<int:contact_id>/', contactSuggestionForm),
    re_path(r'^suggestion_form', contactSuggestionForm),
    path('contact_suggestion_menu/<int:contact_id>/', contactSuggestionMenu),
    path('contact_suggestion_menu/', contactSuggestionMenu),
    path('record_suggestion_form/<int:contact_id>/<int:record_id>/', recordSuggestionForm),
    path('record_suggestion_form/<int:contact_id>/', recordSuggestionForm),
    path('delete_suggested_contact/<int:contact_id>/', deleteSuggestedContact),
    path('delete_suggested_record/<int:record_id>/', deleteSuggestedRecord),
    path('profile/edit/', editProfile.as_view(template_name='generic_form.html', extra_context={
        'action': '/profile/edit/',
        'form_id': 'profile-form',
        'submit_function': 'app.submitProfileForm()',
        'generic_form_header': 'Update Your Profile', 
    })),
    path('profile/', getProfile),
    path('accounts/forgot/', PasswordResetView.as_view(template_name='generic_form.html', extra_context={
        'action': '/accounts/forgot/',
        'form_id': 'password-reset-form',
        'submit_function': 'app.submitPasswordReset()',
        'generic_form_header': 'Reset your password:'
    })),
    path('accounts/', include('django_registration.backends.one_step.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    
    re_path(r'^region_picker', regionPicker),
    re_path(r'^wireframe', wireframe),
    re_path(r'^$', home),
]
