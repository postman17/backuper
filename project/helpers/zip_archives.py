"""
https://www.calazan.com/how-to-zip-an-entire-directory-with-python/
"""
import zipfile
import os
import pyzipper
import logging

from django.conf import settings


logger = logging.getLogger(__name__)


def zipper(folder_or_file_path, output_path_with_file, password, compression=settings.ZIP_ARCHIVE_COMPRESSION):
    """Zip the contents of an entire folder (with that folder included
    in the archive) or file. Empty subfolders will be included in the archive
    as well.
    """
    logger.info(f"Create zip archive: started, {output_path_with_file}")

    parent_folder = os.path.dirname(folder_or_file_path)
    # Retrieve the paths of the folder contents.
    contents = os.walk(folder_or_file_path)

    try:
        zip_file = pyzipper.AESZipFile(
            output_path_with_file,
            'w',
            compression=compression,
            encryption=pyzipper.WZ_AES
        )
        zip_file.pwd = password

        if not os.path.isfile(folder_or_file_path):
            for root, folders, files in contents:
                for folder_name in folders:
                    absolute_path = os.path.join(root, folder_name)
                    relative_path = absolute_path.replace(parent_folder + '\\',
                                                          '')

                    logger.info(f"Create zip archive: adding {absolute_path} to archive")

                    zip_file.write(absolute_path, relative_path)
                for file_name in files:
                    absolute_path = os.path.join(root, file_name)
                    relative_path = absolute_path.replace(parent_folder + '\\', '')
                    logger.info(f"Create zip archive: adding {absolute_path} to archive")
                    zip_file.write(absolute_path, relative_path)
        else:
            with open(folder_or_file_path, "rb") as file:
                filename = os.path.basename(folder_or_file_path)
                zip_file.writestr(filename, file.read())

        logger.info(f"Create zip archive: finished, {output_path_with_file}")
    except (IOError, OSError, zipfile.BadZipfile):
        logger.error(f"Create zip archive: error, {output_path_with_file}", exc_info=True)
    finally:
        zip_file.close()
