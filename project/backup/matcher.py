import os
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
from backup.enums import BackupStatusEnum, CreateContainerHandleEnum, BackupClientNameEnum


matcher_logger = logging.getLogger(__name__)


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

    def create_container(self, backup_record, manager, **kwargs) -> str:
        """Create backup container."""
        backup_record.set_status(BackupStatusEnum.CONTAINER_CREATING_STARTED)
        container_path = manager.create_container(**kwargs)
        backup_record.set_status(BackupStatusEnum.CONTAINER_CREATED)

        return container_path

    def run_backup(self, backup_record, manager_method, container_path, **prepared_fields):
        """Run manager backup method."""
        logger = prepared_fields["logger"]
        logger.info("Run backup: started")
        backup_record.set_status(BackupStatusEnum.UPLOADING_CONTAINER_TO_STORAGE)
        clean_filename = os.path.basename(container_path)
        prepared_fields["remote_path"] = f"{settings.FOLDER_IN_REMOTE_STORAGE}/{clean_filename}"
        prepared_fields["target_path"] = container_path
        filename = manager_method(**prepared_fields)
        backup_record.set_status(BackupStatusEnum.CONTAINER_UPLOADED_TO_STORAGE)
        logger.info("Run backup: finished")

        return filename

    def check_token(self, client_record, manager, access_token, prepared_fields):
        """Check access token or refresh if expired."""
        logger = prepared_fields["logger"]
        logger.info("Check token: started")
        is_token_valid = manager.check_access_token(access_token, logger=logger)
        if is_token_valid:
            logger.info("Check token: access token valid")
            return

        logger.info("Check token: access token not valid")
        refresh_token = client_record.config.get("refresh_token", None)
        if not refresh_token:
            logger.error("Check token: refresh token not found")
            raise ClientManagerMatcherException("Refresh token not found")

        tokens = manager.refresh_token(
            EncryptDecryptWrapper.decrypt_sensitive_fields(client_record.config), logger=logger
        )
        logger.info("Check token: refresh succeed")
        prepared_fields["access_token"] = tokens["access_token"]
        decrypted_config = EncryptDecryptWrapper.decrypt_sensitive_fields(client_record.config)
        for key, value in tokens.items():
            decrypted_config[key] = value

        client_record.config = EncryptDecryptWrapper.encrypt_sensitive_fields(decrypted_config)
        client_record.save(update_fields=["config"])
        logger.info("Check token: finished")

    def execute_backup(self, client_record, service_record, backup_record, logger=matcher_logger):
        logger.info(f"Execute backup: started, {repr(client_record)}, {repr(service_record)}")

        manager = self.get_manager_by_client_name(
            client_record.client_name
        )()
        manager_method = getattr(manager, manager.backup_method, None)
        fields = manager.backup_method_fields
        filename = None

        prepared_fields = {
            "filename": "_".join(service_record.service_name.split(" ")),
            "logger": logger,
        }
        if "access_token" in fields:
            access_token = client_record.config.get("access_token", None)
            if not access_token:
                raise Exception(_("No access_token in client record"))

            prepared_fields["access_token"] = smart_str(
                EncryptDecryptWrapper.decrypt(access_token)
            )
            if BackupClientNameEnum(manager.client_name).data == "oauth":
                self.check_token(client_record, manager, prepared_fields["access_token"], prepared_fields)

        if "source_path" in fields:
            prepared_fields["source_path"] = service_record.source_folder

        if "target_path" in fields:
            prepared_fields["target_path"] = get_current_path_for_files()

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

        if manager.create_container_handle == CreateContainerHandleEnum.BEFORE:
            filename = self.create_container(backup_record, manager, **prepared_fields)
            if manager_method:
                filename = self.run_backup(backup_record, manager_method, filename, **prepared_fields)

        if manager.create_container_handle == CreateContainerHandleEnum.AFTER:
            filename = self.run_backup(
                backup_record, manager_method, prepared_fields["target_path"], **prepared_fields
            )
            prepared_fields["source_path"] = filename
            filename = self.create_container(
                backup_record, manager,  container_path=filename, **prepared_fields
            )

        if manager.after_action_method_name:
            after_method = getattr(manager, manager.after_action_method_name, None)
            if after_method:
                after_method(**prepared_fields)

        backup_record.set_status(BackupStatusEnum.DONE)
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
