import datetime
import json
import os
from pathlib import Path

from src.download_run_info import resolve_executing_program_name

# Bitacora de monitoreo (demo): se guarda en la carpeta Descargas del usuario
# de Windows, en JSON, para que un sistema de monitoreo externo pueda leerla
# facil. Version demo: solo 3 campos (fecha/hora, ejecutor, que se descargo).
MONITORING_LOG_FILE_NAME = "autopolis_dca_monitoreo.json"


def resolve_user_downloads_directory_path():
    return os.path.join(os.path.expanduser("~"), "Downloads")


def append_monitoring_entry(period_button_label):
    entry = {
        "fecha_hora": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "quien_ejecuto": resolve_executing_program_name(),
        "que_descargo": period_button_label,
    }

    downloads_directory_path = resolve_user_downloads_directory_path()
    log_file_path = os.path.join(downloads_directory_path, MONITORING_LOG_FILE_NAME)

    try:
        Path(downloads_directory_path).mkdir(parents=True, exist_ok=True)

        existing_entries = []
        if os.path.isfile(log_file_path):
            with open(log_file_path, "r", encoding="utf-8") as existing_file_handle:
                try:
                    existing_entries = json.load(existing_file_handle)
                except json.JSONDecodeError:
                    existing_entries = []

        existing_entries.append(entry)
        with open(log_file_path, "w", encoding="utf-8") as log_file_handle:
            json.dump(existing_entries, log_file_handle, ensure_ascii=False, indent=2)
    except OSError:
        # Es informativo, no critico: si no se puede escribir (disco lleno,
        # permisos, etc.) no debe tapar el resultado real de la descarga.
        pass
