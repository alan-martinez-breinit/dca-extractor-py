import os

SECURE_FILE_TRANSFER_HOST_ADDRESS = "169.62.217.83"
SECURE_FILE_TRANSFER_PORT_NUMBER = 22
SECURE_FILE_TRANSFER_USERNAME = "ftpdca"
SECURE_FILE_TRANSFER_PASSWORD = "ftpDC@2023"
REMOTE_DIRECTORY_PATH = "/ALANPRUEBAS/FTPIA/Autopolis"

# Se calcula a partir del usuario que ejecuta el .exe en cada maquina, para que
# funcione igual sin importar el nombre de usuario de Windows del cliente.
CURRENT_USER_DOCUMENTS_DIRECTORY_PATH = os.path.join(os.path.expanduser("~"), "Documents")
LOCAL_BASE_DIRECTORY_PATH = os.path.join(CURRENT_USER_DOCUMENTS_DIRECTORY_PATH, "DCA")
LOCAL_CLIENT_SUBDIRECTORY_NAME = "autopolis"

REMOTE_FILE_EXTENSION_FILTER = ".txt"

PROGRESS_LOG_STEP_PERCENTAGE = 5
INTERFACE_UPDATE_STEP_PERCENTAGE = 0.5

# Tamano de cada peticion SFTP individual durante el prefetch. Por defecto paramiko
# usa 32 KB por peticion: para un archivo de 200 MB eso son ~7000 peticiones que se
# despachan antes de que llegue el primer dato util, lo que se ve como una pausa larga
# en 0% antes de que el progreso avance. Un valor mas grande reduce esa cantidad de
# peticiones sin tocar la ventana de flujo del transporte (eso si afecto el rendimiento
# general y fue revertido).
SFTP_REQUEST_CHUNK_SIZE_IN_BYTES = 1024 * 256  # 256 KB
