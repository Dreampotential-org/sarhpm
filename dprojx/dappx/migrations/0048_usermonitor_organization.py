# Generated by Django 2.2.16 on 2021-07-16 05:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dappx', '0047_auto_20210715_0503'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermonitor',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dappx.Organization'),
        ),
    ]