import logging

from helpers.utils import get_current_media_path_for_files
from helpers.zip_archives import zipper
from helpers.base_managers.base import BaseManager


logger = logging.getLogger(__name__)


class LocalContainerBaseManager(BaseManager):
    def create_container(self, source_path: str, target_path, filename=None, master_password=None) -> str:
        logger.info(f"Local container base manager: started, {source_path}")
        filename = get_current_media_path_for_files(f"{filename}.zip")
        self.create_path(target_path)

        zipper(source_path, filename, master_password)

        logger.info(f"Local container base manager: finished, {filename}")
        return filename
