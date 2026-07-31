import os
import shutil
from pathlib import Path


def ensure_base_directory_exists(base_directory_path):
    if os.path.isdir(base_directory_path):
        return False
    Path(base_directory_path).mkdir(parents=True, exist_ok=True)
    return True


def ensure_client_subdirectory_exists(base_directory_path, client_subdirectory_name):
    client_subdirectory_path = os.path.join(base_directory_path, client_subdirectory_name)
    if os.path.isdir(client_subdirectory_path):
        return client_subdirectory_path, False
    Path(client_subdirectory_path).mkdir(parents=True, exist_ok=True)
    return client_subdirectory_path, True


def local_file_with_matching_name_exists(destination_directory_path, remote_file_name):
    destination_file_path = os.path.join(destination_directory_path, remote_file_name)
    return os.path.isfile(destination_file_path)


def copy_static_file_to_destination(source_file_path, destination_directory_path):
    if not os.path.isfile(source_file_path):
        return False
    file_name = os.path.basename(source_file_path)
    destination_file_path = os.path.join(destination_directory_path, file_name)
    shutil.copyfile(source_file_path, destination_file_path)
    return True
