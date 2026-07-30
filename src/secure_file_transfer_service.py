import os
import threading

import paramiko

from src.configuration_settings import (
    SECURE_FILE_TRANSFER_HOST_ADDRESS,
    SECURE_FILE_TRANSFER_PORT_NUMBER,
    SECURE_FILE_TRANSFER_USERNAME,
    SECURE_FILE_TRANSFER_PASSWORD,
    REMOTE_FILE_EXTENSION_FILTER,
    LARGE_FILE_REQUEST_CHUNK_SIZE_IN_BYTES,
    SSH_TRANSPORT_WINDOW_SIZE_IN_BYTES,
)


class SecureFileTransferService:
    """Encapsula la conexion y transferencia de archivos por SFTP.

    No conoce nada sobre la interfaz grafica: expone metodos simples
    que la capa de presentacion puede orquestar e informar mediante callbacks.
    """

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

        underlying_transport = self.secure_shell_client.get_transport()
        underlying_transport.default_window_size = SSH_TRANSPORT_WINDOW_SIZE_IN_BYTES
        underlying_transport.window_size = SSH_TRANSPORT_WINDOW_SIZE_IN_BYTES

        # Peticiones SFTP mas grandes: menos peticiones individuales para el mismo
        # archivo, lo que evita la pausa larga previa a que se vea progreso real
        # en archivos grandes (antes se despachaban miles de peticiones de 32 KB).
        paramiko.SFTPFile.MAX_REQUEST_SIZE = LARGE_FILE_REQUEST_CHUNK_SIZE_IN_BYTES

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
        """Descarga usando prefetch: paramiko encola muchas lecturas en paralelo
        en lugar de esperar la respuesta de red de cada lectura antes de pedir la siguiente.
        Esto reduce drasticamente el tiempo total en conexiones con latencia (VPN/SFTP remoto).
        """
        local_destination_file_path = os.path.join(local_destination_directory_path, remote_file_name)

        with open(local_destination_file_path, "wb") as local_output_file_handle:
            self.secure_file_transfer_client.getfo(
                remote_file_name,
                local_output_file_handle,
                callback=on_chunk_downloaded_callback,
                prefetch=True,
            )

        return remote_file_size_in_bytes

    def download_remote_file_in_parallel_parts(self, remote_file_name, remote_file_size_in_bytes,
                                                local_destination_directory_path, parallel_stream_count,
                                                on_bytes_downloaded_callback):
        """Divide el archivo en partes de tamano similar y las descarga al mismo tiempo
        usando varios canales SFTP independientes sobre la misma conexion SSH.

        Un solo flujo secuencial queda limitado por la latencia de ida y vuelta de cada
        peticion, sin importar cuanto ancho de banda este disponible. Varias partes en
        paralelo aprovechan ese ancho de banda ocioso.
        """
        local_destination_file_path = os.path.join(local_destination_directory_path, remote_file_name)

        with open(local_destination_file_path, "wb") as preallocation_file_handle:
            if remote_file_size_in_bytes > 0:
                preallocation_file_handle.seek(remote_file_size_in_bytes - 1)
                preallocation_file_handle.write(b"\0")

        byte_range_size_per_stream = -(-remote_file_size_in_bytes // parallel_stream_count)  # division hacia arriba
        byte_ranges = []
        range_start_offset = 0
        while range_start_offset < remote_file_size_in_bytes:
            range_end_offset = min(range_start_offset + byte_range_size_per_stream, remote_file_size_in_bytes)
            byte_ranges.append((range_start_offset, range_end_offset))
            range_start_offset = range_end_offset

        total_bytes_downloaded_across_streams = 0
        progress_reporting_lock = threading.Lock()
        first_raised_exception = []

        def download_one_byte_range(range_start_offset, range_end_offset):
            nonlocal total_bytes_downloaded_across_streams
            try:
                stream_sftp_client = self.secure_shell_client.open_sftp()
                try:
                    with stream_sftp_client.open(remote_file_name, "rb") as remote_range_file_handle:
                        remote_range_file_handle.seek(range_start_offset)
                        with open(local_destination_file_path, "r+b") as local_range_file_handle:
                            local_range_file_handle.seek(range_start_offset)
                            remaining_bytes_in_range = range_end_offset - range_start_offset
                            while remaining_bytes_in_range > 0:
                                bytes_to_read_now = min(
                                    LARGE_FILE_REQUEST_CHUNK_SIZE_IN_BYTES, remaining_bytes_in_range)
                                downloaded_chunk = remote_range_file_handle.read(bytes_to_read_now)
                                if not downloaded_chunk:
                                    break
                                local_range_file_handle.write(downloaded_chunk)
                                remaining_bytes_in_range -= len(downloaded_chunk)

                                with progress_reporting_lock:
                                    total_bytes_downloaded_across_streams += len(downloaded_chunk)
                                    on_bytes_downloaded_callback(
                                        total_bytes_downloaded_across_streams, remote_file_size_in_bytes)
                finally:
                    stream_sftp_client.close()
            except Exception as raised_exception:
                first_raised_exception.append(raised_exception)

        worker_threads = [
            threading.Thread(target=download_one_byte_range, args=byte_range, daemon=True)
            for byte_range in byte_ranges
        ]
        for worker_thread in worker_threads:
            worker_thread.start()
        for worker_thread in worker_threads:
            worker_thread.join()

        if first_raised_exception:
            raise first_raised_exception[0]

        return remote_file_size_in_bytes

    def disconnect_from_remote_server(self):
        if self.secure_file_transfer_client is not None:
            self.secure_file_transfer_client.close()
        if self.secure_shell_client is not None:
            self.secure_shell_client.close()
