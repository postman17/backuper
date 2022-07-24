import subprocess
import logging

from helpers.utils import generate_filename
from helpers.base_managers.base import BaseManager


base_manager_logger = logging.getLogger(__name__)


class PgDumperBaseManager(BaseManager):
    def dump_db(
            self,
            remote_address: str,
            db_port: str,
            username: str,
            database_name: str,
            target_path: str,
            filename: str,
            *args,
            **kwargs,
    ) -> str:
        logger = kwargs.get("logger", base_manager_logger)
        logger.info(f"Pg dump base manager: started, {filename}")
        self.create_path(target_path)

        filename = f"{target_path}{generate_filename(filename)}.{username}.sql"
        result = subprocess.run(
            f"pg_dump -h {remote_address} "
            f"-p {db_port} "
            f"-U {username} "
            f"-d {database_name} "
            f"> {filename}",
            shell=True,
            stdout=subprocess.PIPE
        )

        logger.info(f"Pg dump base manager: finished, {result.stdout.decode('utf-8')}")
        return filename
