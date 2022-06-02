from django import forms
from django.contrib import admin
from app.models import Region, Topic, Entity, Contact, Record

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

class RecordAdmin(admin.ModelAdmin):
    list_display = ('topic', 'contact')
    form = RecordForm

class ContactAdmin(admin.ModelAdmin):
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
admin.site.register(Region)
admin.site.register(Topic)
admin.site.register(Entity)
admin.site.register(Record, RecordAdmin)
admin.site.register(Contact, ContactAdmin)