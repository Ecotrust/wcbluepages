from django.contrib.auth.models import User
from django.forms import ModelForm
from app.models import RecordSuggestion, ContactSuggestion, Contact, Record

# https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/
class ContactSuggestionForm(ModelForm):
    class Meta:
        model = ContactSuggestion
        exclude = ['date_created', 'date_modified']


class RecordSuggestionForm(ModelForm):
    class Meta:
        model = RecordSuggestion
        # fields = '__all__'
        exclude = ['date_created', 'date_modified']

class UserProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class ContactForm(ModelForm):
    class Meta:
        model = Contact
        exclude = ['date_create', 'date_modified']

class RecordForm(ModelForm):
    class Meta:
        model = Record
        exclude = ['date_create', 'date_modified']

