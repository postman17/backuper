from helpers.base_managers import YandexDiskBaseManager
from backup.forms import OauthClientCredentialsForm
from backup.enums import BackupClientNameEnum
from backup.managers.abstract import AbstractClientManager


class MailRuCloudManager(YandexDiskBaseManager, AbstractClientManager):
    """Mailru cloud clients manager."""

    auth_type = "oauth"
    client_name = BackupClientNameEnum.MAILRU_CLOUD
    create_client_form = OauthClientCredentialsForm

    def create_client_form_help_text(self) -> str:
        return ""
