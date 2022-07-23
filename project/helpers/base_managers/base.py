import os


class BaseManager:
    def create_path(self, path: str) -> None:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
