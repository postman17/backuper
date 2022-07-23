import datetime

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from django.utils import timezone

from django_celery_beat.models import PeriodicTask

from backup.enums import BackupClientNameEnum, BackupStatusEnum, BackupClientTemporaryStateEnum, BackupClientStatusEnum
from core.models import FilesAbstract
from helpers.models import CreatedAtAbstract, OwnerAbstract, UpdatedAtAbstract
from helpers.utils import get_uuid_hex_state


class BackupClient(OwnerAbstract, CreatedAtAbstract, UpdatedAtAbstract):
    """Represent a client for backup storage."""

    storage_name = models.CharField(_("Storage name"), unique=True, max_length=settings.DEFAULT_CHARFIELD_MAXLENGTH)
    client_name = models.CharField(
        max_length=settings.DEFAULT_CHARFIELD_MAXLENGTH,
        choices=BackupClientNameEnum.choices,
    )
    config = models.JSONField(_("Config"))
    status = models.CharField(
        max_length=settings.DEFAULT_CHARFIELD_MAXLENGTH,
        choices=BackupClientStatusEnum.choices,
        default=BackupClientStatusEnum.CREDENTIALS_NOT_CONFIRMED,
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Backup client")
        verbose_name_plural = _("Backup clients")

    def __str__(self):
        return f"{self.storage_name}"

    def __repr__(self):
        return (
            f"BackupClient id {self.id}: "
            f"storage name - {self.storage_name}, "
            f"client name - {self.client_name}, "
            f"status - {self.get_status_display()}"
        )

    def set_credentials_confirmed(self):
        self.status = BackupClientStatusEnum.CREDENTIALS_CONFIRMED
        self.save(update_fields=['status'])


class BackupClientTemporaryState(OwnerAbstract, CreatedAtAbstract, UpdatedAtAbstract):
    """Keep temporary state for backup client checking."""

    client = models.ForeignKey(
        BackupClient,
        on_delete=models.CASCADE,
        verbose_name=_("Backup client"),
        related_name="temporary_states",
    )
    state = models.CharField(
        _("State"),
        max_length=settings.DEFAULT_CHARFIELD_MAXLENGTH,
        default=get_uuid_hex_state
    )
    status = models.CharField(
        max_length=settings.DEFAULT_CHARFIELD_MAXLENGTH,
        choices=BackupClientTemporaryStateEnum.choices,
        default=BackupClientTemporaryStateEnum.IN_AWAITING,
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Backup client temp state")
        verbose_name_plural = _("Backup clients temp states")
        indexes = [
            models.Index(fields=["state"]),
        ]

    def __str__(self):
        return self.client.storage_name

    def __repr__(self):
        return (
            f"BackupClientTemporaryState id {self.id}: "
            f"client name - {self.client.name}, "
            f"state - {self.get_state_display()}, "
            f"status - {self.get_status_display()}"
        )

    def save(self, *args, **kwargs):
        super(BackupClientTemporaryState, self).save(*args, **kwargs)

        if self.status == BackupClientTemporaryStateEnum.IN_AWAITING:
            cache.set(self.state, self.client.client_name)
        else:
            cache.delete(self.state)

    def is_expired(self):
        now = timezone.now()
        expired_time = self.created_at + datetime.timedelta(
            seconds=settings.BACKUP_CLIENT_TEMP_STATE_LIFETIME_SECONDS
        )
        if expired_time < now:
            return True

        return False

    def set_expired(self):
        self.status = BackupClientTemporaryStateEnum.EXPIRED
        self.save(update_fields=['status'])

    def set_success(self):
        self.status = BackupClientTemporaryStateEnum.SUCCESS
        self.save(update_fields=['status'])

    @classmethod
    def set_expired_to_all(cls):
        expired_records = cls.objects.filter(status=BackupClientTemporaryStateEnum.IN_AWAITING)
        for record in expired_records:
            if record.is_expired():
                record.set_expired()


class ServiceForBackup(OwnerAbstract, CreatedAtAbstract, UpdatedAtAbstract):
    """Represent a service for backup."""

    service_name = models.CharField(_("Service name"), unique=True, max_length=settings.DEFAULT_CHARFIELD_MAXLENGTH)
    source_folder = models.TextField(_("Service files source folder"))

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Service for backup")
        verbose_name_plural = _("Services for backups")

    def __str__(self):
        return f"{self.service_name}"

    def __repr__(self):
        return (
            f"ServiceForBackup id {self.id}: "
            f"service name - {self.service_name}, "
            f"source folder - {self.source_folder}"
        )


class Backup(OwnerAbstract, CreatedAtAbstract, UpdatedAtAbstract, FilesAbstract):
    """Represent a backup."""

    name = models.CharField(_("Backup name"), unique=True, max_length=settings.DEFAULT_CHARFIELD_MAXLENGTH)
    status = models.CharField(
        max_length=50,
        choices=BackupStatusEnum.choices,
        default=BackupStatusEnum.NEW,
    )
    services = models.ManyToManyField(ServiceForBackup, verbose_name=_("Services for backups"))
    backups = models.ManyToManyField(
        "self", verbose_name=_("Children backups"), related_name="parent_backups", symmetrical=False, blank=True
    )
    clients = models.ManyToManyField(BackupClient, verbose_name=_("Backup clients"), related_name="backups", blank=True)
    is_active = models.BooleanField(_("Is backup active"), default=False)
    periodic_task = models.ForeignKey(
        PeriodicTask,
        verbose_name=_("Periodic task"),
        related_name="backups",
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Backup")
        verbose_name_plural = _("Backups")

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return (
            f"Backup id {self.id}: "
            f"name - {self.name}"
        )
