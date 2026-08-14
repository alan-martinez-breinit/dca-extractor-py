from src.configuration_settings import (
    SECURE_FILE_TRANSFER_HOST_ADDRESS,
    SECURE_FILE_TRANSFER_PORT_NUMBER,
    SECURE_FILE_TRANSFER_FALLBACK_PORT_NUMBER,
)
from src.secure_file_transfer_service import SecureFileTransferService
from src.plain_file_transfer_service import PlainFileTransferService
from src.error_message_translator import is_connection_level_failure

SFTP_PROTOCOL_LABEL = "SFTP"
PLAIN_FTP_PROTOCOL_LABEL = "FTP"


class RemoteFileTransferService:

    def __init__(self):
        self.active_client = None
        self.active_protocol_label = None

    def connect_to_remote_server(self):
        sftp_client = SecureFileTransferService()
        try:
            sftp_client.connect_to_remote_server()
        except Exception as sftp_connection_error:
            if not is_connection_level_failure(sftp_connection_error):
                raise

            ftp_client = PlainFileTransferService()
            try:
                ftp_client.connect_to_remote_server()
            except Exception as ftp_connection_error:
                raise ConnectionError(
                    f"No se pudo conectar al servidor DCA ({SECURE_FILE_TRANSFER_HOST_ADDRESS}) "
                    f"ni por SFTP (puerto {SECURE_FILE_TRANSFER_PORT_NUMBER}) ni por FTP "
                    f"(puerto {SECURE_FILE_TRANSFER_FALLBACK_PORT_NUMBER}). Verifica tu conexion "
                    "a internet, que el servidor este disponible, o que un firewall/VPN este "
                    "bloqueando ambos puertos."
                ) from ftp_connection_error

            self.active_client = ftp_client
            self.active_protocol_label = PLAIN_FTP_PROTOCOL_LABEL
            return

        self.active_client = sftp_client
        self.active_protocol_label = SFTP_PROTOCOL_LABEL

    def list_remote_text_file_names(self, remote_directory_path):
        return self.active_client.list_remote_text_file_names(remote_directory_path)

    def get_remote_file_size_in_bytes(self, remote_file_name):
        return self.active_client.get_remote_file_size_in_bytes(remote_file_name)

    def download_remote_file_with_progress(self, *args, **kwargs):
        return self.active_client.download_remote_file_with_progress(*args, **kwargs)

    def download_named_file_if_exists(self, *args, **kwargs):
        return self.active_client.download_named_file_if_exists(*args, **kwargs)

    def disconnect_from_remote_server(self):
        if self.active_client is not None:
            self.active_client.disconnect_from_remote_server()
