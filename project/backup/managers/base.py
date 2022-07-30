import os

from django.conf import settings


class BaseBackupManager:
    def get_remote_file_path(self, target_path: str) -> str:
        return os.path.join(settings.FOLDER_IN_REMOTE_STORAGE, target_path.split("/")[-1])
