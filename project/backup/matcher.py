from django.utils.encoding import smart_bytes
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from backup.managers import YandexDiskManager, MailRuCloudManager, LocalContainerManager
from helpers.utils import get_current_path_for_files


class ClientManagerMatcherException(Exception):
    pass


class ClientManagerMatcher:
    def __init__(self, managers: list) -> None:
        self.managers = managers
        self.managers_by_client_name = {manager.client_name: manager for manager in managers}

    def get_manager_by_client_name(self, client_name: str):
        manager = self.managers_by_client_name.get(client_name, None)
        if not manager:
            raise ClientManagerMatcherException(_("Manager by client name not found."))

        return manager

    def get_form_by_client_name(self, client_name: str):
        manager = self.get_manager_by_client_name(client_name)
        form = manager.create_client_form
        if not form:
            raise ClientManagerMatcherException(_("Form in manager not found."))

        return form

    def get_form_help_text_by_client_name(self, client_name: str):
        manager = self.get_manager_by_client_name(client_name)()

        return manager.create_client_form_help_text()

    def execute_backup(self, client_record, service_record):
        manager = self.get_manager_by_client_name(
            client_record.client_name
        )()
        manager_method = getattr(manager, manager.backup_method)
        fields = manager.backup_method_fields
        prepared_fields = {
            "filename": "_".join(service_record.service_name.split(" "))
        }
        if "access_token" in fields:
            access_token = client_record.config.get("access_token", None)
            if not access_token:
                raise Exception(_("No access_token in client record"))

            prepared_fields["access_token"] = access_token

        if "source_path" in fields:
            source_path = service_record.source_folder
            prepared_fields["source_path"] = source_path

        if "target_path" in fields:
            if manager.is_local:
                prepared_fields["target_path"] = get_current_path_for_files()
            else:
                prepared_fields["target_path"] = "/"

        if "master_password" in fields:
            master_password = client_record.config.get("master_password", None)
            if master_password is None:
                raise Exception(_("No master_password in client record"))

            prepared_fields["master_password"] = (
                smart_bytes(master_password) if
                master_password != "" else settings.MASTER_PASSWORD
            )

        filename = manager_method(**prepared_fields)
        return filename


BACKUP_CLIENT_MANAGERS_MATCHER = ClientManagerMatcher(
    [
        YandexDiskManager,
        MailRuCloudManager,
        LocalContainerManager,
    ]
)
