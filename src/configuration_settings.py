import os
import sys

SECURE_FILE_TRANSFER_HOST_ADDRESS = "169.62.217.83"
SECURE_FILE_TRANSFER_PORT_NUMBER = 22
SECURE_FILE_TRANSFER_USERNAME = "ftpdca"
SECURE_FILE_TRANSFER_PASSWORD = "ftpDC@2023"
REMOTE_DIRECTORY_PATH = "/FTP_AI/COMPANYS/Autopolis"
SYSTEM_DRIVE_ROOT_PATH = os.environ.get("SystemDrive", "C:") + os.sep
LOCAL_BASE_DIRECTORY_PATH = os.path.join(SYSTEM_DRIVE_ROOT_PATH, "DCA")
LOCAL_CLIENT_SUBDIRECTORY_NAME = "autopolis"

REMOTE_FILE_EXTENSION_FILTER = ".txt"

if getattr(sys, "frozen", False):
    APPLICATION_ROOT_DIRECTORY_PATH = os.path.dirname(sys.executable)
    BUNDLED_RESOURCES_DIRECTORY_PATH = getattr(sys, "_MEIPASS", APPLICATION_ROOT_DIRECTORY_PATH)
else:
    APPLICATION_ROOT_DIRECTORY_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    BUNDLED_RESOURCES_DIRECTORY_PATH = APPLICATION_ROOT_DIRECTORY_PATH

AI_INSTRUCTIONS_SOURCE_FILE_NAME = "INSTRUCCIONES_IA.md"

# Orden de busqueda para el archivo de instrucciones de IA: primero junto al .exe
# (permite reemplazarlo sin recompilar), y como respaldo, la copia empaquetada
# dentro del propio ejecutable (para que nunca falte si alguien mueve solo el .exe).
AI_INSTRUCTIONS_SEARCH_DIRECTORIES = (APPLICATION_ROOT_DIRECTORY_PATH, BUNDLED_RESOURCES_DIRECTORY_PATH)

PROGRESS_LOG_STEP_PERCENTAGE = 5
INTERFACE_UPDATE_STEP_PERCENTAGE = 0.5
SFTP_REQUEST_CHUNK_SIZE_IN_BYTES = 1024 * 256
