# Breinit DCA Extractor (Python)

Descarga de archivos SFTP desde servidor remoto y convierte cada `.txt` (pipe-delimited) a `.jsonl` (un objeto JSON por línea, usando la primera fila como nombres de campo).

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
