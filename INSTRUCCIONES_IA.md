# Instrucciones para la IA — Datos DCA Autopolis

Estos archivos `.txt` (delimitados por pipe `|`) y el archivo `schema.ini` que los acompaña son una extracción del sistema DCA (Dealer Consulting Application) para el cliente Autopolis. El conjunto de archivos cambia entre extracciones — no asumas que coincide con una extracción anterior.

## Cómo leer los datos

- `schema.ini` es la única fuente de verdad sobre qué archivos vienen en esta extracción y qué columnas y tipos (`Integer`, `Float`, `Date`, `Char`) tiene cada uno. Léelo directamente de los archivos adjuntos — esa información ya la tienes, no hace falta preguntarle al usuario.
- La primera línea de cada `.txt` es el encabezado real; los datos empiezan en la segunda línea.
- Los archivos pueden pesar varios cientos de MB. Procésalos por partes en lugar de cargarlos completos en memoria.

## Patrones de nomenclatura

Los nombres de archivo siguen un patrón por área de negocio. Úsalo para inferir el propósito de un archivo sin necesidad de que el usuario te lo explique:

- `venta_*` — operaciones de venta (autos, servicio, refacciones).
- `inventario_*` — existencias (autos, refacciones).
- `objetivo_*` / `objetivos_*` — metas comerciales por sucursal y periodo.
- `cxc*` — cuentas por cobrar / cartera de clientes.
- Contiene `servicio` — órdenes de taller / servicio postventa.
- Contiene `refacciones` — refacciones y partes.

## Campos comunes para cruzar información entre archivos

Verifica en `schema.ini` cuáles de estos campos existen en los archivos que vas a cruzar:

- `Company` / `Razon_Social` / `Sucursal` — empresa y sucursal.
- `date_key`, `Nombre_Mes`, `Nombre_Mes_Descripcion` — periodo del registro.
- `VIN` — identifica un vehículo específico.
- `Clientes` / `Clientes_Descripcion` — identifican al cliente.

## Reglas

1. Antes de responder, revisa tú mismo `schema.ini` — no le preguntes al usuario qué archivos o columnas existen, esa información ya está en el archivo adjunto.
2. Si el nombre de un archivo no encaja en ningún patrón conocido, revisa sus columnas en `schema.ini` para entender su contenido antes de usarlo.
3. Solo pregunta al usuario cuando el significado de negocio de algo no pueda derivarse de los datos ni del nombre (por ejemplo, un código interno sin descripción en ninguna columna).
4. No inventes valores ni completes datos faltantes: si un dato no está en el archivo, indícalo.
