from django.forms import ModelForm
from app.models import RecordSuggestion, ContactSuggestion

# https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/
class ContactSuggestionForm(ModelForm):
    class Meta:
        model = ContactSuggestion
        # exclude = ['modified_date', 'creation_date']
        fields = [
            'user', 
            'status',
            'description',
            # 'date_created', 
            # 'date_modified',
            'contact',
            'title',
            'last_name', 
            'first_name', 
            'middle_name',
            'post_title',
            'preferred_pronouns',
            'entity', 
            'other_entity_name',
            'job_title',
            'expertise',
            'email',
            'phone', 
            'fax',
            'address',
            'preferred_contact_method',
            'notes',
        ]