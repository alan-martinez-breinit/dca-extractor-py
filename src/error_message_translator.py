import socket

import paramiko

from src.configuration_settings import (
    SECURE_FILE_TRANSFER_HOST_ADDRESS,
    SECURE_FILE_TRANSFER_PORT_NUMBER,
)


def translate_exception_to_spanish_message(exception):
    if isinstance(exception, paramiko.ssh_exception.NoValidConnectionsError):
        return (
            f"No se pudo conectar al servidor SFTP "
            f"({SECURE_FILE_TRANSFER_HOST_ADDRESS}:{SECURE_FILE_TRANSFER_PORT_NUMBER}). "
            "Verifica tu conexion a internet, que el servidor este disponible, "
            "o que un firewall/VPN no este bloqueando el puerto 22.")

    if isinstance(exception, paramiko.AuthenticationException):
        return "El servidor SFTP rechazo el usuario o la contraseña de conexion."

    if isinstance(exception, socket.gaierror):
        return "No se pudo resolver la direccion del servidor SFTP. Verifica tu conexion a internet."

    if isinstance(exception, socket.timeout):
        return "Se agoto el tiempo de espera al conectar con el servidor SFTP."

    if isinstance(exception, PermissionError):
        file_path_hint = f": {exception.filename}" if exception.filename else ""
        return f"Sin permisos para escribir en la carpeta de destino{file_path_hint}."

    if isinstance(exception, FileNotFoundError):
        file_path_hint = f": {exception.filename}" if exception.filename else ""
        return f"No se encontro la ruta{file_path_hint}."

    if isinstance(exception, paramiko.SSHException):
        return f"Error de conexion SFTP: {exception}"

    return str(exception)


def is_connection_level_failure(exception):
    if isinstance(exception, paramiko.AuthenticationException):
        return False
    return isinstance(exception, OSError)
