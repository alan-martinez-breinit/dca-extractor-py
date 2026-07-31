# Instrucciones para la IA — Datos DCA Autopolis

Este documento acompaña a los archivos `.txt` y `schema.ini` extraídos del sistema DCA (Dealer Consulting Application) para el cliente Autopolis. Súbelos o pégalos junto a este archivo en tu IA de preferencia.

**El conjunto de archivos varía entre extracciones**: pueden desaparecer archivos, agregarse otros nuevos, o cambiar sus columnas. Este documento no es una lista cerrada — es una guía de formato y de patrones de nomenclatura. La fuente de verdad sobre qué archivos existen y qué columnas tiene cada uno, en esta extracción especifica, es siempre `schema.ini`.

## Formato de los archivos

- Cada `.txt` está delimitado por pipe (`|`), no por coma.
- La primera línea de cada archivo es el encabezado real con el nombre de cada columna.
- `schema.ini`, en la misma carpeta, describe para cada archivo el nombre y tipo de dato (`Integer`, `Float`, `Date`, `Char`) de cada columna. **Consulta siempre `schema.ini` antes de interpretar un archivo** — es la fuente de verdad sobre la estructura; no asumas el tipo o significado de una columna solo por su nombre.
- Antes de responder cualquier pregunta, revisa qué archivos vienen realmente en `schema.ini` — no des por hecho que están los mismos de una extracción anterior.
- Los archivos pueden pesar varios cientos de MB. Si necesitas procesarlos completos, hazlo por partes (streaming) en lugar de cargarlos enteros en memoria.

## Patrones de nomenclatura

Los nombres de archivo siguen un patrón por área de negocio. Úsalo para inferir el propósito de un archivo aunque no esté en la lista de ejemplos de abajo:

- `venta_*` — operaciones de venta (autos, servicio, refacciones).
- `inventario_*` — existencias (autos, refacciones).
- `objetivo_*` / `objetivos_*` — metas comerciales por sucursal y periodo.
- `cxc*` — cuentas por cobrar / cartera de clientes.
- Archivos con `servicio` en el nombre — órdenes de taller / servicio postventa.
- Archivos con `refacciones` en el nombre — refacciones y partes.

Si aparece un archivo cuyo nombre no encaja en ningún patrón conocido, no asumas su contenido: revisa sus columnas en `schema.ini` y, si el significado de negocio no es evidente, pregunta antes de interpretarlo.

## Ejemplos de archivos vistos en extracciones anteriores

Esta tabla es solo referencia histórica — puede que no coincida con los archivos de la extracción actual.

| Archivo (ejemplo) | Contenido típico |
|---|---|
| `venta_autos.txt` | Ventas de vehículos nuevos y usados: VIN, fecha de venta, costo, venta neta, unidades vendidas, comisiones, cliente, sucursal. |
| `inventario_autos.txt` | Existencia actual de vehículos: VIN, marca, año modelo, nuevo/usado, días en inventario, color, sucursal. |
| `venta_servicio_refacciones.txt` | Órdenes de taller (servicio) y venta de refacciones: folio de orden, técnico, asesor, costo, venta, fechas de recepción/facturación/entrega. |
| `inventario_refacciones.txt` | Existencia de refacciones en almacén: número de parte, descripción, existencia, costo unitario, fecha de última compra/venta. |
| `cxc.txt` | Cuentas por cobrar: folio, fecha de vencimiento, saldo, saldo vencido, monto original, cliente, vendedor. |
| `objetivo_autos.txt` | Metas comerciales de venta de autos por sucursal y periodo (venta objetivo, unidades objetivo, utilidad objetivo). |
| `objetivos_servicio.txt` | Metas de taller/servicio por sucursal y periodo (órdenes objetivo, venta objetivo, utilidad objetivo). |

## Campos comunes para cruzar información entre archivos

Cuando existan en el archivo (confírmalo en `schema.ini`), estos campos suelen repetirse entre tablas y sirven para relacionarlas:

- `Company` / `Razon_Social` / `Sucursal` — identifican la empresa y sucursal.
- `date_key`, `Nombre_Mes`, `Nombre_Mes_Descripcion` — periodo del registro.
- `VIN` — identifica un vehículo específico.
- `Clientes` / `Clientes_Descripcion` — identifican al cliente.

## Reglas

1. Antes de responder cualquier pregunta sobre los datos, revisa `schema.ini` para confirmar qué archivos existen en esta extracción y qué columnas/tipos tiene cada uno.
2. No asumas que el conjunto de archivos es el mismo que en una extracción anterior.
3. Si necesitas cruzar información entre archivos, confirma primero que el campo común exista en ambos según `schema.ini`.
4. Si el nombre de un archivo o de una columna no deja claro su significado de negocio, dilo explícitamente y pregunta en lugar de asumir.
5. No inventes valores ni completes datos faltantes: si un dato no está en el archivo, indícalo.
