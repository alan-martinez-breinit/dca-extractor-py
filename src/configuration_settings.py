import os

SECURE_FILE_TRANSFER_HOST_ADDRESS = "169.62.217.83"
SECURE_FILE_TRANSFER_PORT_NUMBER = 22
# Respaldo: mismo servidor, mismas credenciales y misma estructura de carpetas,
# pero por FTP plano (no SSH) en el puerto 21. Solo se usa si el puerto 22 no
# logra conectar (no si la conexion SSH conecta pero rechaza la autenticacion).
SECURE_FILE_TRANSFER_FALLBACK_PORT_NUMBER = 21
SECURE_FILE_TRANSFER_USERNAME = "ftpdca"
SECURE_FILE_TRANSFER_PASSWORD = "ftpDC@2023"
REMOTE_DIRECTORY_PATH = "/FTP_AI/COMPANYS/Autopolis"
SYSTEM_DRIVE_ROOT_PATH = os.environ.get("SystemDrive", "C:") + os.sep
LOCAL_BASE_DIRECTORY_PATH = os.path.join(SYSTEM_DRIVE_ROOT_PATH, "DCA")
LOCAL_CLIENT_SUBDIRECTORY_NAME = "autopolis"

REMOTE_FILE_EXTENSION_FILTER = ".txt"

# INSTRUCCIONES_IA.md se maneja aparte (no como copia literal): cada descarga le
# antepone una nota de contexto con el periodo solicitado antes de escribirlo.
AI_INSTRUCTIONS_FILE_NAME = "INSTRUCCIONES_IA.md"

# Otros documentos que si se copian tal cual, sin modificar. DICCIONARIO_IA.md
# es estatico a proposito: dado el volumen de correcciones e informacion de
# negocio que lleva, se prefiere control manual total sobre el texto en vez de
# generarlo por inferencia (que podria fallar el match o el tipo en silencio).
# Ambos se descargan del servidor DCA (subidos ahi por el lado admin,
# DcaFtpExportAutomation) en cada corrida — no hay copia local ni empaquetada
# en el .exe: si el servidor no los tiene, se omiten de forma visible en el
# log en vez de caer a una copia local que podria estar desactualizada.
STATIC_DOCUMENTATION_FILE_NAMES = ("DICCIONARIO_IA.md",)

PROGRESS_LOG_STEP_PERCENTAGE = 5
INTERFACE_UPDATE_STEP_PERCENTAGE = 0.5
SFTP_REQUEST_CHUNK_SIZE_IN_BYTES = 1024 * 256
