import datetime
import os

JET_SCHEMA_DEFAULT_SECTION_TEXT = (
    "[schema.ini]\n"
    "ColNameHeader=False\n"
    "Format=CSVDelimited\n"
    "MaxScanRows=768\n"
    "CharacterSet=OEM\n"
)

SCHEMA_TYPE_SAMPLE_ROW_COUNT = 200
MINIMUM_CHARACTER_COLUMN_WIDTH = 10
MAXIMUM_CHARACTER_COLUMN_WIDTH = 255
KNOWN_DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y")


def is_integer_value(candidate_value):
    try:
        int(candidate_value)
        return True
    except ValueError:
        return False


def is_float_value(candidate_value):
    try:
        float(candidate_value)
        return True
    except ValueError:
        return False


def is_date_value(candidate_value):
    for date_format in KNOWN_DATE_FORMATS:
        try:
            datetime.datetime.strptime(candidate_value, date_format)
            return True
        except ValueError:
            continue
    return False


def infer_jet_column_type_and_width(sample_values_for_column):
    non_empty_sample_values = [value for value in sample_values_for_column if value != ""]
    if not non_empty_sample_values:
        return "Char", MINIMUM_CHARACTER_COLUMN_WIDTH

    if all(is_integer_value(value) for value in non_empty_sample_values):
        return "Integer", None

    if all(is_float_value(value) for value in non_empty_sample_values):
        return "Float", None

    if all(is_date_value(value) for value in non_empty_sample_values):
        return "Date", None

    longest_observed_value_length = max(len(value) for value in non_empty_sample_values)
    character_column_width = min(
        max(longest_observed_value_length, MINIMUM_CHARACTER_COLUMN_WIDTH),
        MAXIMUM_CHARACTER_COLUMN_WIDTH,
    )
    return "Char", character_column_width


def format_column_definition(column_index, column_name, sample_values_for_column):
    inferred_type, inferred_width = infer_jet_column_type_and_width(sample_values_for_column)
    safe_column_name = f'"{column_name}"' if " " in column_name else column_name

    if inferred_type == "Char":
        return f"Col{column_index + 1}={safe_column_name} Char Width {inferred_width}"
    return f"Col{column_index + 1}={safe_column_name} {inferred_type}"


def build_schema_ini_section_for_file(local_file_path, file_name):
    with open(local_file_path, "r", encoding="utf-8", errors="replace") as data_file_handle:
        header_line = data_file_handle.readline().rstrip("\r\n")
        column_names = header_line.split("|")

        sample_rows = []
        for _ in range(SCHEMA_TYPE_SAMPLE_ROW_COUNT):
            data_line = data_file_handle.readline()
            if not data_line:
                break
            sample_rows.append(data_line.rstrip("\r\n").split("|"))

    column_definitions = [
        format_column_definition(
            column_index, column_name,
            [row[column_index] for row in sample_rows if column_index < len(row)])
        for column_index, column_name in enumerate(column_names)
    ]

    section_lines = [
        f"[{file_name}]",
        "ColNameHeader=True",
        "Format=Delimited(|)",
        "MaxScanRows=0",
        "CharacterSet=ANSI",
    ]
    section_lines.extend(column_definitions)
    return "\n".join(section_lines)


def generate_schema_ini_file(local_destination_directory_path, downloaded_file_names):
    schema_ini_file_path = os.path.join(local_destination_directory_path, "schema.ini")

    file_sections = [
        build_schema_ini_section_for_file(
            os.path.join(local_destination_directory_path, file_name), file_name)
        for file_name in downloaded_file_names
    ]

    schema_ini_content = JET_SCHEMA_DEFAULT_SECTION_TEXT + "\n" + "\n\n".join(file_sections) + "\n"

    with open(schema_ini_file_path, "w", encoding="utf-8") as schema_ini_file_handle:
        schema_ini_file_handle.write(schema_ini_content)

    return schema_ini_file_path
