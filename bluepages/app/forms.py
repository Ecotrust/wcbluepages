from django.forms import ModelForm
from app.models import RecordSuggestion, ContactSuggestion

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