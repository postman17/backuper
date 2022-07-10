from django.contrib import admin

from helpers.admin import CreatedAtAdminMixin, UpdatedAtAdminMixin

from .models import FileObject, StatusChangeLog


@admin.register(FileObject)
class FileObjectAdmin(UpdatedAtAdminMixin, CreatedAtAdminMixin, admin.ModelAdmin):
    list_display = ("id", "name", "file", "owner", "updated_at", "created_at")


@admin.register(StatusChangeLog)
class StatusChangeLogAdmin(UpdatedAtAdminMixin, CreatedAtAdminMixin, admin.ModelAdmin):
    list_display = ("id", "initiator", "old_status", "new_status", "updated_at", "created_at")
