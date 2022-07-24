import os
import logging

from django.utils.translation import gettext_lazy as _

from helpers.base_managers import PgDumperBaseManager, LocalContainerBaseManager
from backup.enums import BackupClientNameEnum, CreateContainerHandleEnum
from backup.forms import DbDumpCredentialsForm


manager_logger = logging.getLogger(__name__)


class DbDumpClientManager(LocalContainerBaseManager, PgDumperBaseManager):
    client_name = BackupClientNameEnum.DUMP_DATABASE
    create_client_form = DbDumpCredentialsForm
    create_client_action_method = "get_finish_text"
    create_client_action_method_fields = ["master_password"]
    backup_method = "dump_db"
    backup_method_fields = ["remote_address", "db_port", "username", "database_name", "target_path", "source_path"]
    create_container_handle = CreateContainerHandleEnum.AFTER
    after_action_method_name = "remove_dump"

    def create_client_form_help_text(self) -> str:
        return _("Enter database credentials. For remote address may use docker app name.<br><br>")

    def get_finish_text(self, *args, **kwargs):
        return _('<p style="color: green; font-size: 15px;">Client created successfully</p>')

    def dump_db(self,
            remote_address: str,
            db_port: str,
            username: str,
            database_name: str,
            target_path: str,
            filename: str,
            master_password: str,
            *args,
            **kwargs,
    ) -> str:
        logger = kwargs.get("logger", manager_logger)
        logger.info(f"{self.client_name}: dump db started")
        dump_filename_with_path = super().dump_db(
            remote_address,
            db_port,
            username,
            database_name,
            target_path,
            filename,
            *args,
            **kwargs,
        )

        logger.info(f"{self.client_name}: dump created - {dump_filename_with_path}")
        return dump_filename_with_path

    def remove_dump(self, source_path: str, **kwargs) -> None:
        os.remove(source_path)
