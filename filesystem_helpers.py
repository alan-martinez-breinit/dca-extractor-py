import os
from pathlib import Path


def ensure_base_directory_exists(base_directory_path):
    """Verifica si la carpeta base existe en la maquina local.

    Si no existe, la crea. Si ya existe, no realiza ninguna accion.
    Retorna True si la carpeta fue creada, False si ya existia.
    """
    if os.path.isdir(base_directory_path):
        return False
    Path(base_directory_path).mkdir(parents=True, exist_ok=True)
    return True


def ensure_client_subdirectory_exists(base_directory_path, client_subdirectory_name):
    """Verifica si la subcarpeta del cliente existe dentro de la carpeta base.

    Si no existe, la crea. Si ya existe, no realiza ninguna accion.
    Retorna una tupla (ruta_completa_de_la_subcarpeta, fue_creada).
    """
    client_subdirectory_path = os.path.join(base_directory_path, client_subdirectory_name)
    if os.path.isdir(client_subdirectory_path):
        return client_subdirectory_path, False
    Path(client_subdirectory_path).mkdir(parents=True, exist_ok=True)
    return client_subdirectory_path, True


def local_file_with_matching_name_exists(destination_directory_path, remote_file_name):
    """Verifica si ya existe localmente un archivo cuyo nombre coincide con el remoto.

    Este archivo, en caso de existir, sera sobrescrito durante la descarga.
    Los archivos locales con nombres diferentes no se ven afectados.
    """
    destination_file_path = os.path.join(destination_directory_path, remote_file_name)
    return os.path.isfile(destination_file_path)
