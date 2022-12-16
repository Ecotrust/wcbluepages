# Generated by Django 3.2.16 on 2022-12-16 00:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0008_auto_20221215_1355'),
    ]

    operations = [
        migrations.AddField(
            model_name='recordsuggestion',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recordsuggestion',
            name='date_modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='recordsuggestion',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Declined', 'Declined')], default='Pending', help_text='Has suggestion been approved or declined?', max_length=20, verbose_name='Suggestion status'),
        ),
        migrations.AddField(
            model_name='recordsuggestion',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='auth.user', verbose_name='User proposing this change'),
            preserve_default=False,
        ),
    ]
