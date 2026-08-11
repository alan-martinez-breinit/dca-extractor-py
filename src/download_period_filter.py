import datetime
import os

PREVIOUS_YEAR_PERIOD_KEY = "anio_anterior"
CURRENT_YEAR_PERIOD_KEY = "anio_actual"
CURRENT_MONTH_PERIOD_KEY = "mes_actual"

DOWNLOAD_PERIOD_BUTTON_SPECS = (
    {"period_key": PREVIOUS_YEAR_PERIOD_KEY, "label": "Descargar Año Anterior", "short_label": "Año Anterior"},
    {"period_key": CURRENT_YEAR_PERIOD_KEY, "label": "Descargar Año Actual", "short_label": "Año Actual"},
    {"period_key": CURRENT_MONTH_PERIOD_KEY, "label": "Descargar Mes Actual", "short_label": "Mes Actual"},
)

SPANISH_MONTH_NAMES = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
)

# Que sufijos de archivo remoto arrastra cada boton. El FTP separa el año en
# "meses ya cerrados" (sufijo anio_actual) y "mes en curso" (sufijo
# mes_actual, que sigue acumulando movimientos) como archivos distintos, asi
# que "Año Actual" necesita ambos grupos para representar el año completo a
# la fecha (7 datasets x 2 sufijos = 14 archivos). "Mes Actual" en solitario
# solo trae el segundo grupo — no confundir uno con el otro.
PERIOD_KEY_TO_MATCHING_FILE_SUFFIXES = {
    PREVIOUS_YEAR_PERIOD_KEY: (PREVIOUS_YEAR_PERIOD_KEY,),
    CURRENT_YEAR_PERIOD_KEY: (CURRENT_YEAR_PERIOD_KEY, CURRENT_MONTH_PERIOD_KEY),
    CURRENT_MONTH_PERIOD_KEY: (CURRENT_MONTH_PERIOD_KEY,),
}


def remote_file_name_matches_any_suffix(remote_file_name, file_suffixes):
    """El FTP ya entrega un archivo por periodo, distinguido por un sufijo en
    el nombre (ej. "..._anio_actual.txt"). El periodo se resuelve por nombre
    de archivo — no hay filtrado de filas del lado cliente.
    """
    base_file_name_without_extension, _ = os.path.splitext(remote_file_name)
    return any(
        base_file_name_without_extension.endswith(f"_{file_suffix}")
        for file_suffix in file_suffixes
    )


def filter_remote_file_names_for_period(remote_file_names, period_key):
    matching_file_suffixes = PERIOD_KEY_TO_MATCHING_FILE_SUFFIXES[period_key]
    return [
        remote_file_name for remote_file_name in remote_file_names
        if remote_file_name_matches_any_suffix(remote_file_name, matching_file_suffixes)
    ]


def describe_period_file_suffix(file_suffix, reference_today):
    current_month_name = SPANISH_MONTH_NAMES[reference_today.month - 1]

    if file_suffix == PREVIOUS_YEAR_PERIOD_KEY:
        return f"año calendario {reference_today.year - 1} completo (enero a diciembre)."
    if file_suffix == CURRENT_YEAR_PERIOD_KEY:
        if reference_today.month == 1:
            return f"meses cerrados de {reference_today.year} — ninguno todavía, enero recién comenzó."
        last_closed_month_name = SPANISH_MONTH_NAMES[reference_today.month - 2]
        return f"meses ya cerrados de {reference_today.year}: enero a {last_closed_month_name}."
    if file_suffix == CURRENT_MONTH_PERIOD_KEY:
        return (f"{current_month_name} {reference_today.year} — mes en curso, "
                f"datos parciales (todavía acumulando movimientos).")
    return "periodo no documentado."


def resolve_period_short_label(period_key):
    return next(
        spec["short_label"] for spec in DOWNLOAD_PERIOD_BUTTON_SPECS if spec["period_key"] == period_key)


def build_download_context_note(period_key, reference_today):
    """Bloque markdown que se antepone a INSTRUCCIONES_IA.md en cada descarga,
    para que la IA sepa que periodo cubre exactamente esta extracción sin
    tener que adivinarlo del nombre de archivo.
    """
    button_label = resolve_period_short_label(period_key)
    matching_file_suffixes = PERIOD_KEY_TO_MATCHING_FILE_SUFFIXES[period_key]
    generated_at_text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    suffix_description_lines = "\n".join(
        f"- `_{file_suffix}`: {describe_period_file_suffix(file_suffix, reference_today)}"
        for file_suffix in matching_file_suffixes
    )

    return (
        "## Contexto de esta extracción (generado automáticamente)\n\n"
        f"- Generado: {generated_at_text}\n"
        f"- Descarga solicitada: {button_label}\n"
        "- Archivos que incluyó esta descarga, por sufijo de nombre:\n"
        f"{suffix_description_lines}\n\n"
        "Si en esta carpeta hay archivos con otros sufijos de una descarga anterior "
        "(`_anio_anterior`, `_anio_actual`, `_mes_actual`), siguen siendo válidos para su "
        "propio periodo — no asumas que todos los archivos presentes corresponden a esta "
        "misma ejecución; usa el sufijo de cada nombre para saber a qué periodo pertenece.\n"
    )
