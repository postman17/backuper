"""
https://www.calazan.com/how-to-zip-an-entire-directory-with-python/
"""
import zipfile
import os
import pyzipper


def zip_folder(folder_path, output_path_with_file, password):
    """Zip the contents of an entire folder (with that folder included
    in the archive). Empty subfolders will be included in the archive
    as well.
    """
    parent_folder = os.path.dirname(folder_path)
    # Retrieve the paths of the folder contents.
    contents = os.walk(folder_path)
    try:
        zip_file = pyzipper.AESZipFile(
            output_path_with_file,
            'w',
            compression=pyzipper.ZIP_DEFLATED,
            encryption=pyzipper.WZ_AES
        )
        zip_file.pwd = password

        for root, folders, files in contents:
            for folder_name in folders:
                absolute_path = os.path.join(root, folder_name)
                relative_path = absolute_path.replace(parent_folder + '\\',
                                                      '')
                print("Adding '%s' to archive." % absolute_path)
                zip_file.write(absolute_path, relative_path)
            for file_name in files:
                absolute_path = os.path.join(root, file_name)
                relative_path = absolute_path.replace(parent_folder + '\\',
                                                      '')
                print("Adding '%s' to archive." % absolute_path)
                zip_file.write(absolute_path, relative_path)

        print(f"{output_path_with_file} created successfully.")
    except (IOError, OSError, zipfile.BadZipfile) as exc:
        print(exc)
    finally:
        zip_file.close()
