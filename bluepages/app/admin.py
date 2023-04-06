from django import forms
from django.contrib import admin
from django.db.models import Value
from django.db.models.functions import Concat
from app.models import RegionState, Region, Topic, Entity, Contact, Record, ContactSuggestion, RecordSuggestion
from reversion.admin import VersionAdmin

# This is dumb, but to be able to search with Django's default tool, only field names are allowed: no properties, and no functions.
# The below code allows us to search via entity hierarchy up to 10 levels. If an entity is deeper than that.... oof.
def get_entity_hierarchy_alias(prefix='entity__'):
    return Concat(
        f"{prefix}name", Value(" "),
        f"{prefix}parent__name", Value(" "),
        f"{prefix}parent__parent__name", Value(" "),
        f"{prefix}parent__parent__parent__name", Value(" "),
        f"{prefix}parent__parent__parent__parent__name", Value(" "),
        f"{prefix}parent__parent__parent__parent__parent__name", Value(" "),
        f"{prefix}parent__parent__parent__parent__parent__parent__name", Value(" "),
        f"{prefix}parent__parent__parent__parent__parent__parent__parent__name", Value(" "),
        f"{prefix}parent__parent__parent__parent__parent__parent__parent__parent__name", Value(" "),
        f"{prefix}parent__parent__parent__parent__parent__parent__parent__parent__parent__name", Value(" "),
        f"{prefix}parent__parent__parent__parent__parent__parent__parent__parent__parent__parent__name", Value(" "),
    )

def get_address_components_alias(prefix=''):
    return Concat(
        f"{prefix}line_1", Value(" "),
        f"{prefix}line_2", Value(" "),
        f"{prefix}city", Value(" "),
        f"{prefix}state", Value(" "),
        # f"{prefix}city__state__postal_code", Value(" "),
        f"{prefix}zip_code", Value(" "),
    )

class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        widgets = {
            'regions': admin.widgets.FilteredSelectMultiple('Region', False)
        }
        fields = '__all__'

class RecordInline(admin.TabularInline):
    model = Record
    form = RecordForm
    verbose_name = 'Contact Topic-Region Association'
    verbose_name_plural = 'Topic-Region Associations'

class RecordSuggestionForm(forms.ModelForm):
    class Meta:
        model = RecordSuggestion
        widgets = {
            'regions': admin.widgets.FilteredSelectMultiple('Region', False)
        }
        fields = '__all__'

class RecordSuggestionInline(admin.TabularInline):
    model = RecordSuggestion
    form = RecordSuggestionForm
    verbose_name = 'Contact Suggestion Topic-Region Association'
    verbose_name_plural = 'Suggested Topic-Region Associations'

class RegionStateAdmin(VersionAdmin):
    list_display = ('name', 'postal_code', 'country')

class RegionAdmin(VersionAdmin):
    search_fields = ['name', 'id', 'depth_type', 'states__postal_code', 'states__name', 'states__country__name']
    list_display = ('id', 'name', 'depth_type')

class TopicAdmin(VersionAdmin):
    search_fields = ['name',]

class EntityAdmin(VersionAdmin):
    list_display = ('name', 'parent', 'address')
    search_fields = ['name', 'entity_hierarchy', 'address_components']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.alias(
            entity_hierarchy=get_entity_hierarchy_alias(''),
            address_components=get_address_components_alias('address__')
        )
        return qs

class RecordAdmin(VersionAdmin):
    list_display = ('topic', 'contact')
    search_fields = ('topic__name', 'contact__last_name', 'contact__first_name', 'contact__email', 'entity_hierarchy')
    form = RecordForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.alias(
            entity_hierarchy=get_entity_hierarchy_alias(prefix='contact__entity__')
        )
        return qs

class ContactAdmin(VersionAdmin):
    list_display = ('last_name','first_name','entity','job_title')
    search_fields = ['last_name','first_name','job_title','expertise','email', 'entity_hierarchy']
    fieldsets = (
        ('Name', {
            'fields': (
                'title',
                ('last_name', 'first_name', 'middle_name'),
                'post_title',
                'pronouns'
            )
        }),
        ('Position', {
            'fields': (
                ('entity','job_title','expertise'),
            )
        }),
        ('Contact Information', {
            'fields': (
                'email',
                (
                    'phone', 
                    'mobile_phone',
                    'office_phone',
                    'fax', 
                ),
                'address',
                'preferred_contact_method',
                'show_on_entity_page',
                'is_test_data'
            )
        }),
        ('Additional Information', {
            'fields': (
                'notes',
            )
        })
    )

    inlines = [
        RecordInline
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.alias(
            entity_hierarchy=get_entity_hierarchy_alias('entity__')
        )
        return qs

class ContactSuggestionAdmin(VersionAdmin):
    list_display = ('status', 'user', 'contact_name', 'date_created', 'description')
    search_fields = ['status', 'last_name','first_name','job_title','expertise','email', 'entity_hierarchy']
    readonly_fields = ('user', 'status', 'date_created', 'date_modified')
    fieldsets = (
        ('Request', {
            'fields': (
                ('user', 'status'),
                'description',
                ('date_created', 'date_modified',)
            )
        }),
        ('Contact', {
            'fields': (
                'contact',
                'self_suggestion'
            )
        }),
        ('Name', {
            'fields': (
                'title',
                ('last_name', 'first_name', 'middle_name'),
                'post_title',
                'pronouns'
            )
        }),
        ('Position', {
            'fields': (
                ('entity', 'other_entity_name', 'sub_entity_name'),
                ('job_title','expertise'),
            )
        }),
        ('Contact Information', {
            'fields': (
                'email',
                (
                    'phone', 
                    'mobile_phone',
                    'office_phone',
                    'fax', 
                ),
                'address',
                ('address_line_1', 'address_line_2',),
                ('address_city', 'address_state', 'address_country'),
                'address_zip_code',
                'preferred_contact_method',
                'show_on_entity_page'
            )
        }),
        ('Additional Information', {
            'fields': (
                'notes',
            )
        })
    )

    inlines = [
        RecordSuggestionInline
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.alias(
            entity_hierarchy=get_entity_hierarchy_alias('entity__')
        )
        return qs

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        obj.save()

class RecordSuggestionAdmin(VersionAdmin):
    list_display = ('status', 'user', 'topic', 'contact_suggestion')
    search_fields = ('status', 'user', 'topic__name', 'contact_suggestion__last_name', 'contact_suggestion__first_name', 'contact_suggestion__email', 'entity_hierarchy')
    form = RecordSuggestionForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.alias(
            entity_hierarchy=get_entity_hierarchy_alias(prefix='contact_suggestion__entity__')
        )
        return qs

# Register your models here.
admin.site.register(RegionState, RegionStateAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Entity, EntityAdmin)
admin.site.register(Record, RecordAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(ContactSuggestion, ContactSuggestionAdmin)
admin.site.register(RecordSuggestion, RecordSuggestionAdmin)