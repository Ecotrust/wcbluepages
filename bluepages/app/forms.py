from django.forms import ModelForm
from app.models import RecordSuggestion, ContactSuggestion

class ContactSuggestionForm(ModelForm):
    class Meta:
        model = ContactSuggestion
        exclude = ['modified_date', 'creation_date']