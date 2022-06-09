# Generated by Django 3.2.13 on 2022-06-09 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='entity',
            options={'ordering': ['name'], 'verbose_name_plural': 'Entities'},
        ),
        migrations.AddField(
            model_name='contact',
            name='is_test_data',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='contact',
            name='notes',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='preferred_contact_method',
            field=models.CharField(blank=True, default='', max_length=254, verbose_name='Preferred contact method(s)'),
        ),
        migrations.AddField(
            model_name='contact',
            name='show_on_entity_page',
            field=models.BooleanField(blank=True, choices=[(None, 'Inherit'), (True, 'Public'), (False, 'Private')], default=None, help_text='Public: Display contact on the entity page.<br />Private: Contact only disoverable via region/topic search.<br />Inherit: Do whatever the entity does.', null=True),
        ),
        migrations.AddField(
            model_name='entity',
            name='notes',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='entity',
            name='show_contacts',
            field=models.BooleanField(blank=True, choices=[(None, 'Inherit'), (True, 'Public'), (False, 'Private')], default=None, help_text='Public: Display all known contacts for this entity on the entity page.<br />Private: Contacts only disoverable via region/topic search.<br />Inherit: Do whatever the parent entity does.', null=True),
        ),
        migrations.AddField(
            model_name='topic',
            name='notes',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]
