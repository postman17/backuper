from django.contrib import admin

from backup.models import Backup
from helpers.admin import CreatedAtAndUpdatedAtAdminMixin


@admin.register(Backup)
class BackupAdmin(CreatedAtAndUpdatedAtAdminMixin, admin.ModelAdmin):
    list_display = ("id", "name", "status", "owner", "is_active", "updated_at", "created_at")
    filter_horizontal = ('services', "backups", "clients", "files")
    raw_id_fields = ('periodic_task', )
