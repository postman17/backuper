# Generated by Django 4.0.4 on 2022-05-02 15:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import helpers.utils
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StatusChangeLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated at')),
                ('old_status', models.CharField(max_length=255, verbose_name='Old status')),
                ('new_status', models.CharField(max_length=255, verbose_name='New status')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('initiator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='status_changes', to=settings.AUTH_USER_MODEL, verbose_name='Initiator')),
            ],
            options={
                'verbose_name': 'Status change log',
                'verbose_name_plural': 'Status changes logs',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='FileObject',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated at')),
                ('name', models.TextField(blank=True, verbose_name='Name')),
                ('file', models.FileField(upload_to=helpers.utils.generate_file_path, verbose_name='File')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Owner')),
            ],
            options={
                'verbose_name': 'File object',
                'verbose_name_plural': 'File objects',
                'ordering': ('-created_at',),
            },
        ),
    ]
