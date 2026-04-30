"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/

"""

from django.urls import path, re_path, include
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from app.views import (
    home,
    regionJSON,
    regionPicker,
    wireframe,
    getSuggestionMenu,
    contactMenu,
    contactSuggestionMenu,
    contactSuggestionForm,
    recordSuggestionForm,
    recordContactForm,
    deleteRecord,
    deleteContact,
    deleteSuggestedContact,
    deleteSuggestedRecord,
    getProfile,
    editProfile,
    changePassword,
    filterContactsRequest,
    contactList,
    contactDetail,
    contactDetailHTML,
    getContactJsonLd,
    exportCSVList,
    entityList,
    entityDetail,
    entityDetailHTML,
    exploreEntitiesPage,
    exploreEntitiesEmbedded,
    entityDetailEmbedded,
    contactDetailEmbedded,
    contactForm,
)


urlpatterns = [
    path("filter_contacts", filterContactsRequest),
    path(
        "explore/entities/embedded/",
        exploreEntitiesEmbedded,
        name="explore_entities_embedded",
    ),
    path("explore/entities/", exploreEntitiesPage, name="explore_entities"),
    re_path(r"^regions.json", regionJSON),
    path("get_suggestion_menu/", getSuggestionMenu, name="get_suggestion_menu"),
    path("suggestion_form/<int:contact_id>/", contactSuggestionForm, name="contact_suggestion_form"),
    re_path(r"^suggestion_form", contactSuggestionForm, name="contact_suggestion_form"),
    path("contact_form/<int:contact_id>/", contactForm, name="contact_form"),
    re_path(r"^contact_form", contactForm, name="contact_form"),
    path("contacts/", contactList, name="contact_list"),
    path("contacts/<int:contact_id>/", contactDetailHTML, name="contact_detail_html"),
    path(
        "contacts/<int:contact_id>/embedded/",
        contactDetailEmbedded,
        name="contact_detail_embedded",
    ),
    path("contacts/api/<int:contact_id>/", contactDetail, name="contact_detail"),
    path("contacts/json_ld/<int:contact>/", getContactJsonLd, name="contact_json_ld"),
    path("entities/", entityList, name="entity_list"),
    path("entities/<int:id>/", entityDetailHTML, name="entity_detail_html"),
    path(
        "entities/<int:id>/embedded/", entityDetailEmbedded, name="entity_detail_html"
    ),
    path("entities/api/<int:id>/", entityDetail, name="entity_detail_embedded"),
    path("contact_suggestion_menu/<int:contact_id>/", contactSuggestionMenu),
    path("contact_suggestion_menu/", contactSuggestionMenu),
    path("contact_menu/<int:contact_id>/", contactMenu, name="contact_menu"),
    path("contact_menu/", contactMenu, name="contact_menu"),
    path(
        "record_suggestion_form/<int:contact_id>/<int:record_id>/", recordSuggestionForm, name="record_suggestion_form"
    ),
    path("record_suggestion_form/<int:contact_id>/", recordSuggestionForm, name="record_suggestion_form"),
    path("contact_record_form/<int:contact_id>/<int:record_id>/", recordContactForm, name="record_contact_form"),
    path("contact_record_form/<int:contact_id>/", recordContactForm, name="record_contact_form"),
    path("delete_suggested_contact/<int:contact_id>/", deleteSuggestedContact),
    path("delete_suggested_record/<int:record_id>/", deleteSuggestedRecord),
    path("delete_record/<int:contact_id>/<int:record_id>/", deleteRecord, name="delete_record"),
    path("delete_contact/<int:contact_id>/", deleteContact, name="delete_contact"),
    path(
        "profile/password_change/",
        changePassword.as_view(
            template_name="generic_form.html",
            extra_context={
                "action": "/profile/password_change/",
                "form_id": "password-form",
                "submit_function": "app.submitPasswordChangeForm()",
                "generic_form_header": "Update Your Password",
            },
        ),
    ),
    path(
        "profile/edit/",
        editProfile.as_view(
            template_name="generic_form.html",
            extra_context={
                "action": "/profile/edit/",
                "form_id": "profile-form",
                "submit_function": "app.submitProfileForm()",
                "generic_form_header": "Update Your Profile",
                "generic_form_description": "Update your name and email address. This is the information about your user account, not the information in your contact information in the Blue Pages directory.",
            },
        ),
    ),
    path("profile/", getProfile),
    path(
        "accounts/reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="bluepages_registration/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "accounts/reset/done/",
        PasswordResetCompleteView.as_view(
            template_name="bluepages_registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path(
        "accounts/forgot/",
        PasswordResetView.as_view(
            template_name="generic_form.html",
            extra_context={
                "action": "/accounts/forgot/",
                "form_id": "password-reset-form",
                "submit_function": "app.submitPasswordReset()",
                "generic_form_header": "Reset your password:",
            },
        ),
    ),
    path("accounts/", include("django_registration.backends.one_step.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("export/csv/", exportCSVList, name="export_csv"),
    re_path(r"^region_picker", regionPicker),
    re_path(r"^wireframe", wireframe),
    re_path(r"^$", home),
]
