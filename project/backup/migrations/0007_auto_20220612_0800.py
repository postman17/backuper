# Generated by Django 3.2.13 on 2022-06-12 05:00

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('backup', '0006_oauthtemporarystate'),
    ]

    operations = [
        migrations.AddField(
            model_name='oauthtemporarystate',
            name='status',
            field=models.CharField(choices=[('in_awaiting', 'In awaiting'), ('expired', 'Expired'), ('success', 'Success')], default=django.utils.timezone.now, max_length=255),
            preserve_default=False,
        ),
        migrations.AddIndex(
            model_name='oauthtemporarystate',
            index=models.Index(fields=['state'], name='backup_oaut_state_37f1c5_idx'),
        ),
    ]
