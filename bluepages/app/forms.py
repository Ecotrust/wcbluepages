from django.contrib.auth.models import User
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, HTML
from app.models import RecordSuggestion, ContactSuggestion, Contact, Record


# https://docs.djangoproject.com/en/5.2/topics/forms/modelforms/
class ContactSuggestionForm(ModelForm):
    class Meta:
        model = ContactSuggestion
        exclude = ["date_created", "date_modified"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "contact-suggestion-form"
        self.helper.form_method = "post"
        self.helper.form_show_errors = True
        self.helper.form_show_labels = True
        self.helper.form_tag = False
        self.helper.layout = Layout(
            HTML(
                "<p>Your suggestions will be made available to the Blue Pages administrators to decide whether to include in the database. You can use these suggestions to recommend adding new contacts or to recommend updates to existing contacts in Blue Pages.</p><hr />"
            ),
            Fieldset(
                "Contact Person",
                Row(
                    Column("contact", css_class="col-md-6"),
                    Column("self_suggestion", css_class="col-md-6 align-self-end"),
                ),
                Row("show_on_entity_page", css_class="col-md-6"),
                HTML("<hr />"),
                Row(
                    Column("title", css_class="col-md-2"),
                ),
                Row(
                    Column("first_name", css_class="col-md-4"),
                    Column("middle_name", css_class="col-md-4"),
                    Column("last_name", css_class="col-md-4"),
                ),
                Row(
                    Column("post_title", css_class="col-md-6"),
                    Column("pronouns", css_class="col-md-6"),
                ),
                css_class="well",
            ),
            Fieldset(
                "Job/Role",
                Row(
                    Column("entity", css_class="col-md-6"),
                    Column("other_entity_name", css_class="col-md-6"),
                ),
                Row(
                    Column("sub_entity_name", css_class="col-md-6"),
                    Column("job_title", css_class="col-md-6"),
                ),
                "expertise",
                css_class="well",
            ),
            Fieldset(
                "Contact Info",
                Row(
                    Column("email", css_class="col-md-4"),
                    Column("phone", css_class="col-md-4"),
                    Column("mobile_phone", css_class="col-md-4"),
                ),
                Row(
                    Column("office_phone", css_class="col-md-6"),
                    Column("fax", css_class="col-md-6"),
                ),
                HTML("<hr /><h5>Mailing Address:</h5>"),
                "line_1",
                "line_2",
                Row(
                    Column("city", css_class="col-md-3"),
                    Column("state", css_class="col-md-3"),
                    Column("country", css_class="col-md-3"),
                    Column("zip_code", css_class="col-md-3"),
                ),
                HTML("<hr />"),
                "preferred_contact_method",
                css_class="well",
            ),
            Fieldset(
                "Additional Information", "description", "notes", css_class="well"
            ),
        )


class RecordSuggestionForm(ModelForm):
    class Meta:
        model = RecordSuggestion
        # fields = '__all__'
        exclude = ["date_created", "date_modified"]


class UserProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]


class ContactForm(ModelForm):
    class Meta:
        model = Contact
        exclude = ["date_create", "date_modified"]


class RecordForm(ModelForm):
    class Meta:
        model = Record
        exclude = ["date_create", "date_modified"]
