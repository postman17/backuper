# Generated by Django 3.2.13 on 2022-06-04 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backup', '0003_auto_20220604_0839'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backupclient',
            name='config',
            field=models.JSONField(verbose_name='Config'),
        ),
    ]
