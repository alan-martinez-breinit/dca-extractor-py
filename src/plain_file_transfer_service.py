import ftplib
import os

from src.configuration_settings import (
    SECURE_FILE_TRANSFER_HOST_ADDRESS,
    SECURE_FILE_TRANSFER_FALLBACK_PORT_NUMBER,
    SECURE_FILE_TRANSFER_USERNAME,
    SECURE_FILE_TRANSFER_PASSWORD,
    REMOTE_FILE_EXTENSION_FILTER,
    SFTP_REQUEST_CHUNK_SIZE_IN_BYTES,
)


class PlainFileTransferService:

    def __init__(self):
        self.ftp_client = None

    def connect_to_remote_server(self):
        self.ftp_client = ftplib.FTP()
        self.ftp_client.connect(SECURE_FILE_TRANSFER_HOST_ADDRESS, SECURE_FILE_TRANSFER_FALLBACK_PORT_NUMBER)
        self.ftp_client.login(SECURE_FILE_TRANSFER_USERNAME, SECURE_FILE_TRANSFER_PASSWORD)
        self.ftp_client.set_pasv(True)

    def list_remote_text_file_names(self, remote_directory_path):
        self.ftp_client.cwd(remote_directory_path)
        all_remote_file_names = self.ftp_client.nlst()
        return [
            remote_file_name
            for remote_file_name in all_remote_file_names
            if remote_file_name.endswith(REMOTE_FILE_EXTENSION_FILTER)
        ]

    def get_remote_file_size_in_bytes(self, remote_file_name):
        self.ftp_client.voidcmd("TYPE I")
        return self.ftp_client.size(remote_file_name)

    def download_remote_file_with_progress(self, remote_file_name, remote_file_size_in_bytes,
                                            local_destination_directory_path, on_chunk_downloaded_callback,
                                            local_file_name_override=None):
        local_file_name = local_file_name_override if local_file_name_override is not None else remote_file_name
        local_destination_file_path = os.path.join(local_destination_directory_path, local_file_name)

        bytes_downloaded_so_far = 0
        with open(local_destination_file_path, "wb") as local_output_file_handle:
            def handle_downloaded_block(block_bytes):
                nonlocal bytes_downloaded_so_far
                local_output_file_handle.write(block_bytes)
                bytes_downloaded_so_far += len(block_bytes)
                on_chunk_downloaded_callback(bytes_downloaded_so_far, remote_file_size_in_bytes)

            self.ftp_client.retrbinary(
                f"RETR {remote_file_name}", handle_downloaded_block,
                blocksize=SFTP_REQUEST_CHUNK_SIZE_IN_BYTES)

        return remote_file_size_in_bytes

    def disconnect_from_remote_server(self):
        if self.ftp_client is None:
            return
        try:
            self.ftp_client.quit()
        except ftplib.all_errors:
            self.ftp_client.close()
