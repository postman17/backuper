from django.utils.translation import gettext_lazy as _

from backup.forms import LocalContainerCredentialsForm
from backup.enums import BackupClientNameEnum, CreateContainerHandleEnum
from backup.managers.abstract import AbstractClientManager
from helpers.base_managers import LocalContainerBaseManager


class LocalContainerManager(LocalContainerBaseManager, AbstractClientManager):
    """local container clients manager."""

    client_name = BackupClientNameEnum.LOCAL_CONTAINER
    create_client_form = LocalContainerCredentialsForm
    create_client_action_method = "get_finish_text"
    create_client_action_method_fields = ["master_password"]
    backup_method = ""
    backup_method_fields = ["source_path", "target_path", "master_password"]
    create_container_handle = CreateContainerHandleEnum.BEFORE
    after_action_method_name = None
    delete_file_method_name = None

    def create_client_form_help_text(self) -> str:
        return _("If keep empty, will use the backup service master password<br><br>")

    def get_finish_text(self, *args, **kwargs):
        return _('<p style="color: green; font-size: 15px;">Client created successfully</p>')
