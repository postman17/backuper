import os
import logging
from jinja2 import Template

from django.utils.translation import gettext_lazy as _
from django.conf import settings

from helpers.base_managers import YandexDiskBaseManager, LocalContainerBaseManager
from backup.forms import OauthClientCredentialsForm
from backup.enums import BackupClientNameEnum
from backup.managers.abstract import AbstractClientManager
from helpers.crypto import EncryptDecryptWrapper


logger = logging.getLogger(__name__)


class YandexDiskManager(
    LocalContainerBaseManager, YandexDiskBaseManager, AbstractClientManager
):
    """Yandex disk clients manager."""

    auth_type = "oauth"
    client_name = BackupClientNameEnum.YANDEX_DRIVE
    create_client_action_method = "get_oauth_code_url"
    create_client_action_method_fields = ["client_id", "state", "redirect_url"]
    create_client_form = OauthClientCredentialsForm
    backup_method = "upload_file"
    backup_method_fields = ["access_token", "source_path", "target_path"]
    is_local = False
    path_to_create_client_template = 'project/backup/templates/backup/jinja2_templates/yandex_disk_oauth_info.html'

    def create_client_form_help_text(self) -> str:
        with open(self.path_to_create_client_template) as file:
            template = Template(file.read())
            return _(str(template.render(
                url='https://yandex.ru/dev/id/doc/dg/oauth/tasks/register-client.html',
                site_url=settings.SITE_URL,
            )))

    def get_oauth_code_url(self, client_id: str, state: str, redirect_url: str) -> str:
        logger.info(f"{self.client_name}: get oauth code url")

        url = super().get_oauth_code_url(client_id, state, redirect_url)
        with open('project/backup/templates/backup/jinja2_templates/oauth_final_stage.html') as file:
            template = Template(file.read())
            return _(str(template.render(
                url=url,
                state=state,
                start_time_awaiting=settings.BACKUP_CLIENT_TEMP_STATE_LIFETIME_SECONDS,
                text=_(
                    "Please grant privileges, "
                    "if you not approve privileges, create client will be failed after: "
                ),
                succeed_text=_('Client created! Return to menu.'),
                failed_text=_(
                    'Create client failed. '
                    'Plz try again and check every step carefully.'
                ),
            )))

    def get_tokens(self, config: dict, code: str) -> dict:
        logger.info(f"{self.client_name}: get tokens started")

        client_id = EncryptDecryptWrapper.get_decrypted_value(config.get("client_id"), "client_id")
        client_secret = EncryptDecryptWrapper.get_decrypted_value(config.get("client_secret"), "client_secret")
        tokens = super().get_tokens(client_id, client_secret, code)

        logger.info(
            f"{self.client_name}: get tokens finished - {EncryptDecryptWrapper.mask_sensitive_data(tokens)}"
        )
        return tokens

    def upload_file(
        self,
        access_token: str,
        source_path: str,
        target_path: str,
        filename: str,
        master_password: str,
    ) -> str:
        logger.info(f"{self.client_name}: upload_file started")
        file_name_with_path = self.create_container(
            source_path,
            target_path,
            filename,
            master_password,
        )
        clean_filename = os.path.basename(file_name_with_path)
        result = super().upload_file(
            access_token,
            file_name_with_path,
            f"{settings.FOLDER_IN_REMOTE_STORAGE}/{clean_filename}"
        )

        logger.info(f"{self.client_name}: upload_file finished, {result}")
        return file_name_with_path
