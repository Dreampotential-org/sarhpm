# Generated by Django 2.2.13 on 2021-07-20 02:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dappx', '0049_remove_usermonitor_organization'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationmembermonitor',
            name='client',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='organizationmembermonitor_requests_created', to=settings.AUTH_USER_MODEL),
        ),
    ]
