import os
import uuid
from typing import Any

from django.utils import timezone
from django.conf import settings


def generate_filename(filename: str) -> str:
    """Generate filename."""
    filename_splitted = os.path.split(filename)
    if len(filename_splitted) > 1:
        ext = filename_splitted[-1]
        filename = f"{uuid.uuid4()}.{ext}"
    else:
        filename = f"{uuid.uuid4()}"

    return filename


def generate_file_path(instance: Any, filename: str) -> str:
    """Generate file path."""
    date = timezone.now().strftime("%Y/%m/%d")
    filename = generate_filename(filename)
    return os.path.join(settings.PATH_TO_FILES_FORMAT.format(date=date), filename)


def get_current_path_for_files():
    """Getting current path for files by date."""
    date = timezone.now().strftime("%Y/%m/%d")
    return os.path.join(
        settings.MEDIA_ROOT,
        settings.PATH_TO_FILES_FORMAT.format(date=date),
    )


def get_current_media_path_for_files(filename):
    """Getting current media path for files by date."""
    date = timezone.now().strftime("%Y/%m/%d")
    filename = generate_filename(filename)
    path = os.path.join(
        settings.MEDIA_ROOT,
        settings.PATH_TO_FILES_FORMAT.format(date=date),
    )
    return os.path.join(path, filename)


def get_uuid_hex_state() -> str:
    """Get uuid4 without dashes."""
    return uuid.uuid4().hex
