from django import forms
from django.contrib import admin
from app.models import Region, Topic, Entity, Contact, Record
from reversion.admin import VersionAdmin

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
    pass

class TopicAdmin(VersionAdmin):
    pass

class EntityAdmin(VersionAdmin):
    pass

class RecordAdmin(VersionAdmin):
    list_display = ('topic', 'contact')
    form = RecordForm

class ContactAdmin(VersionAdmin):
    list_display = ('last_name','first_name','entity','job_title')
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
                ('email','phone','address'),
            )
        }),
    )

    inlines = [
        RecordInline
    ]

# Register your models here.
admin.site.register(Region, RegionAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Entity, EntityAdmin)
admin.site.register(Record, RecordAdmin)
admin.site.register(Contact, ContactAdmin)