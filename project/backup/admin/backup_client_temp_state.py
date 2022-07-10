from django.contrib import admin

from backup.models import BackupClientTemporaryState
from helpers.admin import CreatedAtAndUpdatedAtAdminMixin


@admin.register(BackupClientTemporaryState)
class BackupClientTemporaryStateAdmin(CreatedAtAndUpdatedAtAdminMixin, admin.ModelAdmin):
    list_display = ("id", "client", "status", "owner", "status", "updated_at", "created_at")

    def has_add_permission(self, request):
        return False
