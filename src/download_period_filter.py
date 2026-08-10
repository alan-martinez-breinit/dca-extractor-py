import datetime
import os

DATE_KEY_COLUMN_NAME = "date_key"
DATE_KEY_KNOWN_DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y")

PREVIOUS_YEAR_PERIOD_KEY = "anio_anterior"
CURRENT_YEAR_PERIOD_KEY = "anio_actual"
CURRENT_MONTH_PERIOD_KEY = "mes_actual"

# Sufijo exclusivo para la parte "mes en curso" que produce el boton "Año
# Actual". Deliberadamente distinto de CURRENT_MONTH_PERIOD_KEY: ese sufijo
# ("_mes_actual") solo debe aparecer cuando el usuario presiona el boton
# "Descargar Mes Actual", nunca como efecto secundario de "Año Actual".
CURRENT_YEAR_MONTH_IN_PROGRESS_SUFFIX = "anio_actual_mes_en_curso"

DOWNLOAD_PERIOD_BUTTON_SPECS = (
    {"period_key": PREVIOUS_YEAR_PERIOD_KEY, "label": "Descargar Año Anterior", "short_label": "Año Anterior"},
    {"period_key": CURRENT_YEAR_PERIOD_KEY, "label": "Descargar Año Actual", "short_label": "Año Actual"},
    {"period_key": CURRENT_MONTH_PERIOD_KEY, "label": "Descargar Mes Actual", "short_label": "Mes Actual"},
)

SPANISH_MONTH_NAMES = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
)


def parse_date_key_to_date(date_key_value):
    """Algunos archivos DCA traen date_key como "21/01/2025 12:00:00 a. m."
    (con hora en locale espanol) y otros como "2025-01-01". Solo nos importa
    la fecha para filtrar por periodo, asi que se ignora todo lo que venga
    despues del primer espacio en vez de parsear la hora/AM-PM.
    """
    date_only_token = date_key_value.strip().split(" ")[0]
    for date_format in DATE_KEY_KNOWN_DATE_FORMATS:
        try:
            return datetime.datetime.strptime(date_only_token, date_format).date()
        except ValueError:
            continue
    return None


def row_is_in_previous_year(row_date, reference_today):
    return row_date.year == reference_today.year - 1


def row_is_in_current_year_closed_months(row_date, reference_today):
    return row_date.year == reference_today.year and row_date.month < reference_today.month


def row_is_in_current_month(row_date, reference_today):
    return row_date.year == reference_today.year and row_date.month == reference_today.month


def resolve_period_output_specs(period_key):
    """Devuelve (sufijo_de_salida, funcion_de_filtro) por cada archivo que
    debe producir ese boton. "Año Actual" produce dos: meses ya cerrados del
    año (acumulado) y el mes en curso por separado, porque el mes en curso
    sigue abierto y acumulando movimientos.
    """
    if period_key == PREVIOUS_YEAR_PERIOD_KEY:
        return ((PREVIOUS_YEAR_PERIOD_KEY, row_is_in_previous_year),)
    if period_key == CURRENT_YEAR_PERIOD_KEY:
        return (
            (CURRENT_YEAR_PERIOD_KEY, row_is_in_current_year_closed_months),
            (CURRENT_YEAR_MONTH_IN_PROGRESS_SUFFIX, row_is_in_current_month),
        )
    if period_key == CURRENT_MONTH_PERIOD_KEY:
        return ((CURRENT_MONTH_PERIOD_KEY, row_is_in_current_month),)
    raise ValueError(f"Periodo de descarga desconocido: {period_key}")


def build_period_output_file_path(destination_directory_path, remote_file_name, output_suffix):
    base_file_name_without_extension, file_extension = os.path.splitext(remote_file_name)
    return os.path.join(
        destination_directory_path, f"{base_file_name_without_extension}_{output_suffix}{file_extension}")


def write_filtered_period_files(downloaded_file_path, destination_directory_path, remote_file_name,
                                 period_output_specs, reference_today):
    """Lee downloaded_file_path una sola vez y escribe un archivo de salida
    por cada (sufijo, filtro) en period_output_specs, conservando solo las
    filas cuyo date_key cumple ese filtro. Devuelve {sufijo: ruta} y
    {sufijo: filas_escritas}.
    """
    output_file_paths = {}
    output_row_counts = {}
    output_file_handles = {}

    with open(downloaded_file_path, "r", encoding="utf-8", errors="replace") as source_file_handle:
        header_line = source_file_handle.readline()
        column_names = header_line.rstrip("\r\n").split("|")
        date_key_column_index = column_names.index(DATE_KEY_COLUMN_NAME)

        for output_suffix, _ in period_output_specs:
            output_file_path = build_period_output_file_path(
                destination_directory_path, remote_file_name, output_suffix)
            output_file_paths[output_suffix] = output_file_path
            output_row_counts[output_suffix] = 0
            output_file_handle = open(output_file_path, "w", encoding="utf-8")
            output_file_handle.write(header_line)
            output_file_handles[output_suffix] = output_file_handle

        for data_line in source_file_handle:
            row_columns = data_line.rstrip("\r\n").split("|")
            if date_key_column_index >= len(row_columns):
                continue
            row_date = parse_date_key_to_date(row_columns[date_key_column_index])
            if row_date is None:
                continue
            for output_suffix, row_belongs_to_period in period_output_specs:
                if row_belongs_to_period(row_date, reference_today):
                    output_file_handles[output_suffix].write(data_line)
                    output_row_counts[output_suffix] += 1

    for output_file_handle in output_file_handles.values():
        output_file_handle.close()

    return output_file_paths, output_row_counts


def describe_period_suffix(output_suffix, reference_today):
    current_month_name = SPANISH_MONTH_NAMES[reference_today.month - 1]

    if output_suffix == PREVIOUS_YEAR_PERIOD_KEY:
        return f"año calendario {reference_today.year - 1} completo (enero a diciembre)."

    if output_suffix == CURRENT_YEAR_PERIOD_KEY:
        if reference_today.month == 1:
            return f"meses cerrados de {reference_today.year} — ninguno todavía, enero recién comenzó."
        last_closed_month_name = SPANISH_MONTH_NAMES[reference_today.month - 2]
        return f"meses ya cerrados de {reference_today.year}: enero a {last_closed_month_name}."

    if output_suffix in (CURRENT_MONTH_PERIOD_KEY, CURRENT_YEAR_MONTH_IN_PROGRESS_SUFFIX):
        return (f"{current_month_name} {reference_today.year} — mes en curso, "
                f"datos parciales (todavía acumulando movimientos).")

    return "periodo no documentado."


def resolve_period_short_label(period_key):
    return next(
        spec["short_label"] for spec in DOWNLOAD_PERIOD_BUTTON_SPECS if spec["period_key"] == period_key)


def build_download_context_note(period_key, reference_today):
    """Bloque markdown que se antepone a INSTRUCCIONES_IA.md en cada descarga,
    para que la IA sepa que periodo cubre exactamente esta extraccion sin
    tener que adivinarlo del nombre de archivo.
    """
    button_label = resolve_period_short_label(period_key)
    period_output_specs = resolve_period_output_specs(period_key)

    suffix_description_lines = "\n".join(
        f"- `_{output_suffix}`: {describe_period_suffix(output_suffix, reference_today)}"
        for output_suffix, _ in period_output_specs
    )
    generated_at_text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    return (
        "## Contexto de esta extracción (generado automáticamente)\n\n"
        f"- Generado: {generated_at_text}\n"
        f"- Descarga solicitada: {button_label}\n"
        "- Archivos que produjo esta descarga, por sufijo de nombre:\n"
        f"{suffix_description_lines}\n\n"
        "Si en esta carpeta hay archivos con otros sufijos de una descarga anterior "
        "(`_anio_anterior`, `_anio_actual`, `_anio_actual_mes_en_curso`, `_mes_actual`), "
        "siguen siendo válidos para su propio periodo — no asumas que todos los archivos "
        "presentes corresponden a esta misma ejecución; usa el sufijo de cada nombre para "
        "saber a qué periodo pertenece.\n"
    )
