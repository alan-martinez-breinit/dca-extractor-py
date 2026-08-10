import os
import sys

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
