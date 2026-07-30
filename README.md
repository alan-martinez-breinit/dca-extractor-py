# Breinit DCA Extractor (Python)

Descarga de archivos `.txt` desde servidor SFTP remoto hacia una carpeta local del cliente, usando prefetch para maximizar la velocidad de transferencia.

## Estructura del proyecto

- `main.py` — punto de entrada, crea la ventana principal
- `src/application_window.py` — construcción de la interfaz gráfica y orquestación de la descarga
- `src/secure_file_transfer_service.py` — conexión y transferencia de archivos SFTP (sin dependencias de UI)
- `src/filesystem_helpers.py` — verificación y creación de carpeta base, subcarpeta y archivos locales
- `src/canvas_drawing_helpers.py` — utilidades de dibujo (rectángulos redondeados)
- `src/color_palette.py` — paleta de colores de la interfaz
- `src/configuration_settings.py` — credenciales, rutas y parámetros de configuración

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
