import datetime
import os
import sys

DOWNLOAD_HISTORY_LOG_FILE_NAME = "historial_descargas.log"
DEVELOPMENT_MODE_EXECUTOR_LABEL = "python main.py (modo desarrollo)"


def resolve_executing_program_name():
    if getattr(sys, "frozen", False):
        return os.path.basename(sys.executable)
    return DEVELOPMENT_MODE_EXECUTOR_LABEL


def format_duration_message(duration_in_seconds):
    """Convierte segundos a un texto legible tipo "2 min 30 seg". Omite los
    minutos cuando son 0 (dice "45 seg", no "0 min 45 seg") para que suene
    natural al leerlo, no como un valor de depuracion.
    """
    total_seconds = max(0, int(duration_in_seconds))
    minutes, remaining_seconds = divmod(total_seconds, 60)
    if minutes == 0:
        return f"{remaining_seconds} seg"
    return f"{minutes} min {remaining_seconds} seg"


def append_download_history_entry(destination_directory_path, period_button_label, outcome_text,
                                   files_generated_count, elapsed_seconds):
    """Agrega una linea al historial persistente de descargas: quien ejecuto,
    cuando, que periodo pidio y como termino. No borra corridas anteriores —
    es un log de auditoria, se acumula con el tiempo.
    """
    executed_at_text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    executing_program_name = resolve_executing_program_name()
    elapsed_time_text = format_duration_message(elapsed_seconds)

    log_line = (
        f"[{executed_at_text}] Ejecutor: {executing_program_name} | "
        f"Descarga: {period_button_label} | Resultado: {outcome_text} | "
        f"Archivos generados: {files_generated_count} | Duracion: {elapsed_time_text}\n"
    )

    log_file_path = os.path.join(destination_directory_path, DOWNLOAD_HISTORY_LOG_FILE_NAME)
    try:
        with open(log_file_path, "a", encoding="utf-8") as log_file_handle:
            log_file_handle.write(log_line)
    except OSError:
        # El historial es informativo, no critico: si no se puede escribir
        # (disco lleno, permisos, etc.) no debe tapar el error real de la
        # descarga que ya se esta manejando en el llamador.
        pass
