import logging

from django.utils.encoding import smart_bytes, smart_str
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from backup.managers import (
    YandexDiskManager,
    MailRuCloudManager,
    LocalContainerManager,
    DbDumpClientManager,
    GoogleDriveManager,
)
from helpers.utils import get_current_path_for_files
from helpers.crypto import EncryptDecryptWrapper


logger = logging.getLogger(__name__)


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
        logger.info(f"Execute backup: started, {repr(client_record)}, {repr(service_record)}")
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

            prepared_fields["access_token"] = smart_str(
                EncryptDecryptWrapper.decrypt(access_token)
            )

        if "source_path" in fields:
            source_path = service_record.source_folder
            prepared_fields["source_path"] = source_path

        if "target_path" in fields:
            if manager.is_local:
                prepared_fields["target_path"] = get_current_path_for_files()
            else:
                prepared_fields["target_path"] = "/"

        if "remote_address" in fields:
            prepared_fields["remote_address"] = client_record.config["remote_address"]

        if "db_port" in fields:
            prepared_fields["db_port"] = client_record.config["db_port"]

        if "username" in fields:
            prepared_fields["username"] = client_record.config["username"]

        if "database_name" in fields:
            prepared_fields["database_name"] = client_record.config["database_name"]

        master_password = client_record.config.get("master_password", None)
        prepared_fields["master_password"] = (
            smart_bytes(master_password) if
            master_password else smart_bytes(settings.MASTER_PASSWORD)
        )

        filename = manager_method(**prepared_fields)

        logger.info(
            (
                f"Execute backup: finished, "
                f"{repr(client_record)}, "
                f"{repr(service_record)}, "
                f"{filename}"
            )
        )
        return filename


# Add new manager to here
BACKUP_CLIENT_MANAGERS_MATCHER = ClientManagerMatcher(
    [
        YandexDiskManager,
        MailRuCloudManager,
        LocalContainerManager,
        DbDumpClientManager,
        GoogleDriveManager,
    ]
)
