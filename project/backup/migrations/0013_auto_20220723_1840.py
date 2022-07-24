# Generated by Django 3.2.13 on 2022-07-23 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_fileobject_owner'),
        ('backup', '0012_auto_20220612_0929'),
    ]

    operations = [
        migrations.AddField(
            model_name='backup',
            name='status_logs',
            field=models.ManyToManyField(blank=True, to='core.StatusChangeLog', verbose_name='Status change logs'),
        ),
        migrations.AddField(
            model_name='backupclient',
            name='status_logs',
            field=models.ManyToManyField(blank=True, to='core.StatusChangeLog', verbose_name='Status change logs'),
        ),
        migrations.AddField(
            model_name='backupclienttemporarystate',
            name='status_logs',
            field=models.ManyToManyField(blank=True, to='core.StatusChangeLog', verbose_name='Status change logs'),
        ),
        migrations.AddField(
            model_name='serviceforbackup',
            name='status_logs',
            field=models.ManyToManyField(blank=True, to='core.StatusChangeLog', verbose_name='Status change logs'),
        ),
    ]
