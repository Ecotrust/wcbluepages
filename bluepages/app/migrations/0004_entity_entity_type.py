# Generated by Django 3.2.13 on 2022-08-04 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20220705_1349'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='entity_type',
            field=models.CharField(blank=True, choices=[(None, 'Unspecified'), ('Tribal', 'Tribal'), ('Federal', 'Federal'), ('State', 'State')], default=None, max_length=15, null=True, verbose_name='Type of Entity'),
        ),
    ]
