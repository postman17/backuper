# Generated by Django 3.2.13 on 2022-06-12 05:39

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('backup', '0007_auto_20220612_0800'),
    ]

    operations = [
        migrations.AddField(
            model_name='backupclient',
            name='status',
            field=models.CharField(choices=[('credentials_not_confirmed', 'Credentials not confirmed'), ('credentials_confirmed', 'Credentials confirmed')], default=django.utils.timezone.now, max_length=255),
            preserve_default=False,
        ),
    ]
