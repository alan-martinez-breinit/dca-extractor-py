# Breinit DCA Extractor (Python)

Descarga de archivos `.txt` desde servidor SFTP remoto hacia una carpeta local del cliente, usando prefetch para maximizar la velocidad de transferencia. Al terminar, genera un `schema.ini` junto a los archivos descargados describiendo columnas y tipos de cada uno, para que una IA (o Jet/Access) pueda interpretarlos sin ambigüedad.

## Estructura del proyecto

- `main.py` — punto de entrada, crea la ventana principal
- `src/application_window.py` — construcción de la interfaz gráfica y orquestación de la descarga
- `src/secure_file_transfer_service.py` — conexión y transferencia de archivos SFTP (sin dependencias de UI)
- `src/filesystem_helpers.py` — verificación y creación de carpeta base, subcarpeta y archivos locales
- `src/schema_ini_generator.py` — genera `schema.ini` describiendo columnas y tipos inferidos de cada `.txt` descargado
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
pyinstaller --onefile --windowed --name "Breinit_DCA_Extractor" --icon dca_icon.ico main.py
```

Ejecutable en: `dist/Breinit_DCA_Extractor.exe`. Copia `INSTRUCCIONES_IA.md` a esa misma carpeta antes de entregar el `.exe` al cliente — el programa lo busca junto a sí mismo.
