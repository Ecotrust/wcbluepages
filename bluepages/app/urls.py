"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/

"""
from django.urls import path, re_path, include
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView
from app.views import (
    home, regionJSON, regionPicker, wireframe, getSuggestionMenu, contactSuggestionMenu, contactSuggestionForm, 
    recordSuggestionForm, deleteSuggestedContact, deleteSuggestedRecord, getProfile, editProfile, changePassword, 
    filterContactsRequest, contactList, contactDetail, contactDetailHTML, getContactJsonLd, exportCSVList,
    entityList, #entityDetail, entityDetailHTML, getEntityJsonLd,
)


urlpatterns = [
    path('filter_contacts', filterContactsRequest),
    re_path(r'^regions.json', regionJSON),
    path('get_suggestion_menu/', getSuggestionMenu),
    path('suggestion_form/<int:contact_id>/', contactSuggestionForm),
    re_path(r'^suggestion_form', contactSuggestionForm),
    path('contacts/', contactList, name='contact_list'),
    path('contacts/<int:contact_id>/', contactDetailHTML, name='contact_detail_html'),
    path('contacts/api/<int:contact_id>/', contactDetail, name='contact_detail'),
    path('contacts/json_ld/<int:contact>/', getContactJsonLd, name='contact_json_ld'),
    path('entities/', entityList, name='entity_list'),
    # path('entities/<int:id>/', entityDetailHTML, name='entity_detail_html'),
    # path('entities/api/<int:id>/', entityDetail, name='entity_detail'),
    # path('entities/json_ld/<int:id>/', getEntityJsonLd, name='entity_json_ld'),
    path('contact_suggestion_menu/<int:contact_id>/', contactSuggestionMenu),
    path('contact_suggestion_menu/', contactSuggestionMenu),
    path('record_suggestion_form/<int:contact_id>/<int:record_id>/', recordSuggestionForm),
    path('record_suggestion_form/<int:contact_id>/', recordSuggestionForm),
    path('delete_suggested_contact/<int:contact_id>/', deleteSuggestedContact),
    path('delete_suggested_record/<int:record_id>/', deleteSuggestedRecord),
    path('profile/password_change/', changePassword.as_view(template_name='generic_form.html', extra_context={
        'action': '/profile/password_change/',
        'form_id': 'password-form',
        'submit_function': 'app.submitPasswordChangeForm()',
        'generic_form_header': 'Update Your Password',
    })), 
    path('profile/edit/', editProfile.as_view(template_name='generic_form.html', extra_context={
        'action': '/profile/edit/',
        'form_id': 'profile-form',
        'submit_function': 'app.submitProfileForm()',
        'generic_form_header': 'Update Your Profile', 
    })),
    path('profile/', getProfile),
    path('accounts/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name = 'bluepages_registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('accounts/reset/done/', PasswordResetCompleteView.as_view(template_name = 'bluepages_registration/password_reset_complete.html'), name='password_reset_complete'),
    path('accounts/forgot/', PasswordResetView.as_view(template_name='generic_form.html', extra_context={
        'action': '/accounts/forgot/',
        'form_id': 'password-reset-form',
        'submit_function': 'app.submitPasswordReset()',
        'generic_form_header': 'Reset your password:'
    })),
    path('accounts/', include('django_registration.backends.one_step.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

    path('export/csv/', exportCSVList, name='export_csv'),
    
    re_path(r'^region_picker', regionPicker),
    re_path(r'^wireframe', wireframe),
    re_path(r'^$', home),
]
