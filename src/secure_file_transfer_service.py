import os

import paramiko

from src.configuration_settings import (
    SECURE_FILE_TRANSFER_HOST_ADDRESS,
    SECURE_FILE_TRANSFER_PORT_NUMBER,
    SECURE_FILE_TRANSFER_USERNAME,
    SECURE_FILE_TRANSFER_PASSWORD,
    REMOTE_FILE_EXTENSION_FILTER,
    SFTP_REQUEST_CHUNK_SIZE_IN_BYTES,
)


class SecureFileTransferService:

    def __init__(self):
        self.secure_shell_client = None
        self.secure_file_transfer_client = None

    def connect_to_remote_server(self):
        self.secure_shell_client = paramiko.SSHClient()
        self.secure_shell_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.secure_shell_client.connect(
            SECURE_FILE_TRANSFER_HOST_ADDRESS,
            SECURE_FILE_TRANSFER_PORT_NUMBER,
            SECURE_FILE_TRANSFER_USERNAME,
            SECURE_FILE_TRANSFER_PASSWORD,
        )

        paramiko.SFTPFile.MAX_REQUEST_SIZE = SFTP_REQUEST_CHUNK_SIZE_IN_BYTES
        self.secure_file_transfer_client = self.secure_shell_client.open_sftp()

    def list_remote_text_file_names(self, remote_directory_path):
        self.secure_file_transfer_client.chdir(remote_directory_path)
        all_remote_file_names = self.secure_file_transfer_client.listdir()
        return [
            remote_file_name
            for remote_file_name in all_remote_file_names
            if remote_file_name.endswith(REMOTE_FILE_EXTENSION_FILTER)
        ]

    def get_remote_file_size_in_bytes(self, remote_file_name):
        return self.secure_file_transfer_client.stat(remote_file_name).st_size

    def download_remote_file_with_progress(self, remote_file_name, remote_file_size_in_bytes,
                                            local_destination_directory_path, on_chunk_downloaded_callback):
        local_destination_file_path = os.path.join(local_destination_directory_path, remote_file_name)

        with open(local_destination_file_path, "wb") as local_output_file_handle:
            self.secure_file_transfer_client.getfo(
                remote_file_name,
                local_output_file_handle,
                callback=on_chunk_downloaded_callback,
                prefetch=True,
            )

        return remote_file_size_in_bytes

    def disconnect_from_remote_server(self):
        if self.secure_file_transfer_client is not None:
            self.secure_file_transfer_client.close()
        if self.secure_shell_client is not None:
            self.secure_shell_client.close()
