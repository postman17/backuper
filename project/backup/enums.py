from django.utils.translation import gettext_lazy as _
from django.db import models

from helpers.enums import EnumChoicesMixin, AdditionalDataTextChoices


class BackupClientNameEnum(EnumChoicesMixin, AdditionalDataTextChoices):
    YANDEX_DRIVE = "yandex_drive", _("Yandex Drive"), "oauth"
    MAILRU_CLOUD = "mailru_cloud", _("Mailru Cloud"), "oauth"
    GOOGLE_DRIVE = "google_drive", _("Google drive"), "oauth"
    DUMP_DATABASE = "dump_database", _("Dump database"), "postgresql"
    LOCAL_CONTAINER = "local_container", _("Local container"), ""

    @classmethod
    def not_need_confirm_client_names(cls):
        return ["local_container"]


class BackupStatusEnum(EnumChoicesMixin, models.TextChoices):
    NEW = "new", _("New")
    STARTED = "started", _("Started")
    CONTAINER_CREATING_STARTED = "container_creating_started", _("Container creating started")
    CONTAINER_CREATED = "container_created", _("Archive created")
    UPLOADING_CONTAINER_TO_STORAGE = "uploading_container_to_storage", _("Uploading container to storage")
    CONTAINER_UPLOADED_TO_STORAGE = "container_uploaded_to_storage", _("Container uploaded to storage")
    DONE = "done", _("Done")
    FAILED = "failed", _("Failed")


class BackupClientTemporaryStateEnum(EnumChoicesMixin, models.TextChoices):
    IN_AWAITING = "in_awaiting", _("In awaiting")
    EXPIRED = "expired", _("Expired")
    SUCCESS = "success", _("Success")


class BackupClientStatusEnum(EnumChoicesMixin, models.TextChoices):
    CREDENTIALS_NOT_CONFIRMED = "credentials_not_confirmed", _("Credentials not confirmed")
    CREDENTIALS_CONFIRMED = "credentials_confirmed", _("Credentials confirmed")
