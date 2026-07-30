SECURE_FILE_TRANSFER_HOST_ADDRESS = "169.62.217.83"
SECURE_FILE_TRANSFER_PORT_NUMBER = 22
SECURE_FILE_TRANSFER_USERNAME = "ftpdca"
SECURE_FILE_TRANSFER_PASSWORD = "ftpDC@2023"
REMOTE_DIRECTORY_PATH = "/ALANPRUEBAS/FTPIA/Autopolis"

LOCAL_BASE_DIRECTORY_PATH = r"C:\Users\Breinit\Documents\DCA"
LOCAL_CLIENT_SUBDIRECTORY_NAME = "autopolis"

REMOTE_FILE_EXTENSION_FILTER = ".txt"

PROGRESS_LOG_STEP_PERCENTAGE = 5
INTERFACE_UPDATE_STEP_PERCENTAGE = 0.5

# Tamano de cada peticion SFTP individual. Un valor mas grande significa menos
# peticiones para el mismo archivo.
LARGE_FILE_REQUEST_CHUNK_SIZE_IN_BYTES = 1024 * 256  # 256 KB

# Ventana de flujo del transporte SSH. El valor por defecto de paramiko (2 MB) limita
# cuantos datos pueden viajar en paralelo antes de esperar confirmacion, lo cual
# se nota mas mientras mas grande es el archivo. Se amplia al maximo permitido.
SSH_TRANSPORT_WINDOW_SIZE_IN_BYTES = 2147483647

# A partir de este tamano, el archivo se descarga dividido en partes simultaneas
# en lugar de como un solo flujo. Esto evita que un archivo grande quede limitado
# por la latencia de una sola conexion cuando el ancho de banda disponible es mayor.
LARGE_FILE_SIZE_THRESHOLD_IN_BYTES = 50 * 1024 * 1024  # 50 MB

# Cantidad de partes simultaneas en las que se divide un archivo grande para su descarga.
PARALLEL_DOWNLOAD_STREAM_COUNT_FOR_LARGE_FILES = 4
