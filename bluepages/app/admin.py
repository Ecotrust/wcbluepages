from django import forms
from django.contrib import admin
from django.db.models import Value
from django.db.models.functions import Concat
from app.models import Region, Topic, Entity, Contact, Record
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
        f"{prefix}city__name", Value(" "),
        f"{prefix}city__state__name", Value(" "),
        f"{prefix}city__state__postal_code", Value(" "),
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
                'preferred_pronouns'
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
                ('phone', 'fax'), 
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


# Register your models here.
admin.site.register(Region, RegionAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Entity, EntityAdmin)
admin.site.register(Record, RecordAdmin)
admin.site.register(Contact, ContactAdmin)