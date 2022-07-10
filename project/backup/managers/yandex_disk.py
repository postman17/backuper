import os
from jinja2 import Template

from django.utils.translation import gettext_lazy as _
from django.conf import settings

from helpers.base_managers import YandexDiskBaseManager, LocalContainerBaseManager
from backup.forms import OauthClientCredentialsForm
from backup.enums import BackupClientNameEnum
from backup.managers.abstract import AbstractClientManager


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

    def create_client_form_help_text(self) -> str:
        with open('project/backup/templates/backup/jinja2_templates/oauth_info.html') as file:
            template = Template(file.read())
            return _(str(template.render(
                url='https://yandex.ru/dev/id/doc/dg/oauth/tasks/register-client.html',
                site_url=settings.SITE_URL,
            )))

    def get_oauth_code_url(self, client_id: str, state: str, redirect_url: str) -> str:
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

    def upload_file(
            self,
            access_token: str,
            source_path: str,
            target_path: str,
            filename: str,
            master_password: str,
    ) -> str:
        file_name_with_path = self.create_container(
            source_path,
            target_path,
            filename,
            master_password,
        )
        clean_filename = os.path.basename(file_name_with_path)
        super().upload_file(access_token, file_name_with_path, f"backup/{clean_filename}")

        return file_name_with_path
