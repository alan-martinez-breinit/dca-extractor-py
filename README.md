# Breinit DCA Extractor (Python)

Descarga de archivos `.jsonl` desde servidor SFTP remoto hacia una carpeta local del cliente.

## Estructura del proyecto

- `main.py` — punto de entrada, crea la ventana principal
- `application_window.py` — construcción de la interfaz gráfica y orquestación de la descarga
- `secure_file_transfer_service.py` — conexión y transferencia de archivos SFTP (sin dependencias de UI)
- `filesystem_helpers.py` — verificación y creación de carpeta base, subcarpeta y archivos locales
- `canvas_drawing_helpers.py` — utilidades de dibujo (rectángulos redondeados)
- `color_palette.py` — paleta de colores de la interfaz
- `configuration_settings.py` — credenciales, rutas y parámetros de configuración

## Requisitos

- Python 3.8+

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
python main.py
```

## Compilar a .exe

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

Ejecutable en: `dist/main.exe`
