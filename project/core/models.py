from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from helpers.models import CreatedAtAbstract, OwnerAbstract, UpdatedAtAbstract, UUIDModelAbstract
from helpers.utils import generate_file_path

User = get_user_model()


class FileObject(UUIDModelAbstract, CreatedAtAbstract, UpdatedAtAbstract, OwnerAbstract):
    """Represent a media file."""

    name = models.TextField(_("Name"), blank=True)
    file = models.FileField(_("File"), upload_to=generate_file_path)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("File object")
        verbose_name_plural = _("File objects")

    def __str__(self):
        return f"{self.name}"


class FilesAbstract(models.Model):
    files = models.ManyToManyField(FileObject, verbose_name=_("Files"), blank=True)

    class Meta:
        abstract = True


class StatusChangeLog(CreatedAtAbstract, UpdatedAtAbstract):
    """Keep models statuses changes logs."""

    initiator = models.ForeignKey(
        User,
        verbose_name=_("Initiator"),
        related_name="status_changes",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    old_status = models.CharField(_("Old status"), max_length=settings.DEFAULT_CHARFIELD_MAXLENGTH)
    new_status = models.CharField(_("New status"), max_length=settings.DEFAULT_CHARFIELD_MAXLENGTH)
    description = models.TextField(_("Description"), blank=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Status change log")
        verbose_name_plural = _("Status changes logs")

    def __str__(self):
        return f"{self.old_status} - {self.new_status}"
