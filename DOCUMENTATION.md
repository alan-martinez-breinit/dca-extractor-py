# DCA FTP — Arquitectura e Implementación

## Descripción General

DCA FTP extrae datos tabulares desde servidores SFTP remotos y genera automáticamente metadatos de esquema para interpretación por IA. La arquitectura separa responsabilidades: orquestación de UI, lógica SFTP, operaciones de filesystem e inferencia de esquema.

## Arquitectura

### Capas

```
┌─────────────────────────────────────┐
│    application_window.py            │  GUI + Orquestación
│  (Tkinter, tracking de progreso)    │
└────────────┬────────────────────────┘
             │
┌────────────▼──────────────────────────────────────┐
│  Capa de Servicios                                │
├────────────────────────────────────────────────────┤
│ • SecureFileTransferService (SFTP)                │
│ • filesystem_helpers (I/O)                        │
│ • schema_ini_generator (Inferencia de tipos)      │
└────────────┬──────────────────────────────────────┘
             │
┌────────────▼──────────────────────┐
│  Infraestructura y Configuración  │
├───────────────────────────────────┤
│ • configuration_settings.py       │
│ • color_palette.py                │
└───────────────────────────────────┘
```

### Separación de Responsabilidades

- **application_window.py** — Solo GUI, sin lógica de negocio. Lanza threads para operaciones I/O-bound.
- **secure_file_transfer_service.py** — Conectividad SFTP. Sin dependencias de UI. Sin estado.
- **schema_ini_generator.py** — Funciones puras para inferencia de tipos y generación formato Jet.
- **filesystem_helpers.py** — Operaciones de directorio y archivo idempotentes.
- **configuration_settings.py** — Centralizacion de secretos, rutas y parámetros de sintonización.

## Decisiones de Diseño Clave

### 1. Prefetch Paralelo para SFTP

**Decisión**: Implementar prefetch paralelo en `SecureFileTransferService`.

**Justificación**: Las transferencias SFTP están limitadas por I/O. Paralelizar múltiples descargas reduce significativamente el tiempo total, especialmente para datasets de 100s de MB.

**Trade-off**: Overhead de conexión vs. ganancia de throughput. Sintonizado mediante `MAX_CONCURRENT_TRANSFERS` en `configuration_settings.py`.

### 2. Inferencia de Tipos mediante Muestreo

**Decisión**: Inferir tipos de columnas (Integer, Float, Date, Char) muestreando primeras 200 filas.

**Justificación**:
- Escanear archivos completos de 500MB es prohibitivamente lento.
- Muestra de 200 filas es estadísticamente suficiente para la mayoría de datasets.
- Formato Jet/Access `.ini` requiere tipos en tiempo de esquema.

**Limitaciones**:
- Si valores de columna son mixtos (ej: "123" en primeras 200 filas, "ABC" después), tipo inferido puede ser incorrecto.
- Mitigación: Documentar estrategia de muestreo en `INSTRUCCIONES_IA.md`.

### 3. Instrucciones IA Embebidas

**Decisión**: Embebeñ `INSTRUCCIONES_IA.md` en `.exe` mediante PyInstaller `--add-data`.

**Justificación**: Sistemas de IA (Claude, GPT) necesitan semántica de datos para interpretar campos DCA correctamente. Fuente única de verdad previene desvío de esquema.

**Mecanismo Override**: Archivo externo (mismo directorio que `.exe`) tiene prioridad. Permite actualizaciones sin recompilación.

### 4. Manejo de Charset (ANSI vs. OEM)

**Problema**: Archivos DCA se exportan en charsets heredados (ANSI, OEM). Acentos, `ñ` y caracteres especiales pueden corromperse.

**Implementación**: `open(..., encoding="utf-8", errors="replace")` en generación de esquema. Bytes no-UTF8 → carácter de reemplazo.

**Orientación Usuario**: `INSTRUCCIONES_IA.md` documenta problemas de encoding y mitigación.

### 5. Formato de Esquema Jet/Access

**Decisión**: Generar archivos `.ini` legibles por Microsoft Jet (Access, importación Excel).

**Formato** (ejemplo):

```ini
[schema.ini]
ColNameHeader=False
Format=CSVDelimited
MaxScanRows=768
CharacterSet=OEM

[venta_diaria.txt]
ColNameHeader=True
Format=Delimited(|)
MaxScanRows=0
CharacterSet=ANSI
Col1=VIN Char Width 20
Col2=Fecha_Venta Date
Col3=Monto_Neto Float
Col4=Comisión Float
```

**Justificación**: Jet es estándar de facto para usuarios no-técnicos (Excel, Access). Elimina ambigüedad en importación.

## Diagrama de Flujo

```
Usuario hace clic en "Descargar Archivos"
    ↓
ApplicationWindow valida rutas + spinner inicia
    ↓
SecureFileTransferService.download_files()
    │
    ├─ Conectar SFTP (credenciales desde config)
    ├─ Listar directorio remoto
    ├─ Lanzar N threads, cada uno descarga 1 archivo
    │  (Prefetch: thread pool, basado en cola)
    └─ Callback progreso → Actualización UI cada X%
    ↓
Archivos escritos en directorio local
    ↓
schema_ini_generator.generate_schema_ini_file()
    │
    └─ Para cada .txt:
       ├─ Leer header (nombres de columnas)
       ├─ Muestrear 200 filas
       ├─ Inferir tipo por columna
       └─ Formatear sección Jet
    ↓
schema.ini escrito
    ↓
Copiar INSTRUCCIONES_IA.md a carpeta salida (si no está embebido)
    ↓
UI: "Descarga completada" ✓
```

## Configuración

Todos los parámetros en `configuration_settings.py`:

| Parámetro | Ejemplo | Propósito |
|-----------|---------|----------|
| `SFTP_HOST` | `sftp.dealer.com` | Servidor remoto |
| `SFTP_PORT` | `22` | Puerto SFTP |
| `SFTP_USERNAME` | `autopolis_user` | Autenticación |
| `SFTP_PASSWORD` | `***` | Autenticación (⚠️ nunca comitear) |
| `REMOTE_DIRECTORY_PATH` | `/data/exports/` | Archivos a descargar |
| `LOCAL_BASE_DIRECTORY_PATH` | `C:\DCA\` | Raíz local |
| `MAX_CONCURRENT_TRANSFERS` | `4` | Workers paralelos |
| `PROGRESS_LOG_STEP_PERCENTAGE` | `5` | Frecuencia log (%) |

**Seguridad**: Credenciales deben almacenarse en variables de entorno o vault seguro, no hardcodeadas. Implementación actual es solo demostración.

## Estrategia de Testing

### Tests Unitarios (recomendado, aún no implementado)

- `test_schema_ini_generator.py`
  - Test inferencia tipos: integers, floats, dates, strings mixtos
  - Test casos extremos: columnas vacías, valores nulos, anchos límite
  - Test generación formato Jet

- `test_filesystem_helpers.py`
  - Idempotencia creación directorios
  - Casos extremos de permisos

### Tests de Integración

- Mock servidor SFTP (fixtures test paramiko)
- End-to-end: descarga → generación esquema → validación sintaxis `.ini`

### Validación Manual

- Descargar export DCA real (~50MB)
- Abrir `.ini` en Excel (Datos → Texto en columnas)
- Verificar tipos inferidos coincidan con realidad

## Limitaciones Conocidas

1. **Fragilidad Inferencia de Tipos** — Si columna tiene tipos mixtos (primeras 200 filas numéricas, luego texto), inferencia puede fallar. Mitigación: editar `.ini` manualmente post-descarga.

2. **Corrupción Charset** — Encodings heredados (ANSI, OEM) pueden producir mojibake para texto acentuado. Mitigación: orientación usuario en `INSTRUCCIONES_IA.md`.

3. **Overhead Prefetch** — Si remoto es lento o archivos pequeños, paralelismo puede añadir overhead. Sintonizar `MAX_CONCURRENT_TRANSFERS`.

4. **Sin Sync Incremental** — Siempre redescarga todos los archivos. Sin sync delta o resume-on-fail.

5. **Fuente SFTP Única** — Hardcodeada a un remoto. Multi-fuente requiere refactor de config.

## Mejoras Futuras

- [ ] Descargas incremental/resume (track filesize/mtime)
- [ ] Detección charset pluggable (librería chardet)
- [ ] Drag-drop config UI (upload JSON vs. hardcoding)
- [ ] Async logging (evitar bloqueo thread UI)
- [ ] Retry logic con backoff exponencial
- [ ] Tests unitarios + CI/CD integration
- [ ] Modo API (wrapper FastAPI para uso headless)

## Dependencias

| Paquete | Versión | Propósito |
|---------|---------|----------|
| `paramiko` | ~3.0 | Cliente SFTP |
| `pyinstaller` | ~5.0 | Bundling ejecutable |

Dependencias mínimas por diseño — reduce riesgo cadena suministro y bloat binario.

## Debugging

Habilitar logging verboso (modificar `configuration_settings.py`):

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Luego ejecutar `python main.py` — handshakes SFTP, listas archivos, inferencias tipos logged a stderr.

## Licencia

MIT. Ver [LICENSE](LICENSE).
