# Generated by Django 3.2.16 on 2023-04-06 20:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_auto_20230406_1151'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contact',
            name='address',
        ),
        migrations.RemoveField(
            model_name='contactsuggestion',
            name='address',
        ),
        migrations.RemoveField(
            model_name='entity',
            name='address',
        ),
    ]