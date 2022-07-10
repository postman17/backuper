import os

from helpers.utils import get_current_media_path_for_files
from helpers.zip_archives import zip_folder


class LocalContainerBaseManager:
    def check_path(self, path: str) -> bool:
        return os.path.exists(path)

    def create_container(self, source_path: str, target_path, filename=None, master_password=None) -> bool:
        filename = get_current_media_path_for_files(f"{filename}.zip")
        if not self.check_path(target_path):
            os.makedirs(target_path, exist_ok=True)

        zip_folder(source_path, filename, master_password)
        return filename
