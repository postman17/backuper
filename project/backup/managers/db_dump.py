import os
import logging

from django.utils.translation import gettext_lazy as _

from helpers.base_managers import PgDumperBaseManager, LocalContainerBaseManager
from backup.enums import BackupClientNameEnum
from backup.forms import DbDumpCredentialsForm


logger = logging.getLogger(__name__)


class DbDumpClientManager(LocalContainerBaseManager, PgDumperBaseManager):
    auth_type = None
    client_name = BackupClientNameEnum.DUMP_DATABASE
    create_client_form = DbDumpCredentialsForm
    create_client_action_method = "get_finish_text"
    create_client_action_method_fields = ["master_password"]
    backup_method = "dump_db"
    backup_method_fields = ["remote_address", "db_port", "username", "database_name", "target_path"]
    is_local = True

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
        file_name_with_path = self.create_container(
            dump_filename_with_path,
            target_path,
            filename,
            master_password,
        )

        logger.info(f"{self.client_name}: container for dump created - {file_name_with_path}")

        os.remove(dump_filename_with_path)
        logger.info(f"{self.client_name}: dump deleted, method finished")

        return file_name_with_path
