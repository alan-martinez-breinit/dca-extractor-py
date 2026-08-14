# DCA FTP — Herramienta de Extracción Automática de Datos

Descargador SFTP rápido y seguro con inferencia automática de esquema. Descarga archivos `.txt` desde servidores DCA remotos (Dealer Consulting Application) y genera metadatos de esquema para procesamiento asistido por IA.

## Características

- **Transferencia SFTP Segura** — Prefetch paralelo para descargas de alta velocidad
- **Generación Automática de Esquema** — Infiere tipos de columnas (Integer, Float, Date, Char) desde muestras de datos
- **Listo para IA** — Genera `schema.ini` para interpretación sin ambigüedad
- **GUI Nativa** — Interfaz Tkinter multiplataforma con seguimiento de progreso en tiempo real
- **Ejecutable Único** — Compilación PyInstaller con documentación embebida

## Inicio Rápido

### Requisitos Previos
- Python 3.8+
- Credenciales de servidor SFTP (configuradas en `src/configuration_settings.py`)

### Instalación y Ejecución

```bash
pip install -r requirements.txt
python main.py
```

### Compilar Ejecutable Independiente

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "FTP DCA AUTOPOLIS" --icon dca_icon.ico main.py
```

Ejecutable: `dist/FTP DCA AUTOPOLIS.exe`

`INSTRUCCIONES_IA.md`/`DICCIONARIO_IA.md` no viven en este repo ni se empaquetan en el `.exe`: en cada descarga la app los trae del servidor FTP DCA (mismo servidor/carpeta que los `.txt` de negocio), donde los mantiene y sube el proyecto admin `DcaFtpExportAutomation`. Si el servidor no los tiene, la descarga simplemente los omite (queda registrado en el log) — corregir estos documentos no requiere recompilar ni redistribuir el `.exe`, solo actualizar la copia en `DcaFtpExportAutomation`.

## Estructura del Proyecto

```
src/
├── application_window.py              # GUI, orquestación, progreso
├── secure_file_transfer_service.py    # Conexión SFTP y descarga paralela
├── schema_ini_generator.py            # Inferencia de esquema y generación .ini
├── filesystem_helpers.py              # Creación de directorios y validación
├── configuration_settings.py          # Credenciales, rutas, parámetros
├── color_palette.py                   # Paleta de colores
└── canvas_drawing_helpers.py          # Utilidades de dibujo (rectángulos redondeados)
```

## Salida

Tras descarga exitosa:
- **Archivos**: `C:\DCA\autopolis/{nombre_archivo}.txt` (delimitados por pipe `|`)
- **Metadatos**: `schema.ini` (compatible con Jet/Access)

Ver [DOCUMENTATION.md](DOCUMENTATION.md) para detalles de arquitectura.
