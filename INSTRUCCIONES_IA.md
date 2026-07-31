# Instrucciones para la IA — Datos DCA Autopolis

Este documento acompaña a los archivos `.txt` y `schema.ini` extraídos del sistema DCA (Dealer Consulting Application) para el cliente Autopolis. Súbelos o pégalos junto a este archivo en tu IA de preferencia.

## Formato de los archivos

- Cada `.txt` está delimitado por pipe (`|`), no por coma.
- La primera línea de cada archivo es el encabezado real con el nombre de cada columna.
- `schema.ini`, en la misma carpeta, describe para cada archivo el nombre y tipo de dato (`Integer`, `Float`, `Date`, `Char`) de cada columna. **Consulta siempre `schema.ini` antes de interpretar un archivo** — es la fuente de verdad sobre la estructura; no asumas el tipo o significado de una columna solo por su nombre.
- Los archivos pueden pesar varios cientos de MB. Si necesitas procesarlos completos, hazlo por partes (streaming) en lugar de cargarlos enteros en memoria.

## Contenido de cada archivo

| Archivo | Contenido |
|---|---|
| `venta_autos.txt` | Ventas de vehículos nuevos y usados: VIN, fecha de venta, costo, venta neta, unidades vendidas, comisiones, cliente, sucursal. |
| `inventario_autos.txt` | Existencia actual de vehículos: VIN, marca, año modelo, nuevo/usado, días en inventario, color, sucursal. |
| `venta_servicio_refacciones.txt` | Órdenes de taller (servicio) y venta de refacciones: folio de orden, técnico, asesor, costo, venta, fechas de recepción/facturación/entrega. |
| `inventario_refacciones.txt` | Existencia de refacciones en almacén: número de parte, descripción, existencia, costo unitario, fecha de última compra/venta. |
| `cxc.txt` | Cuentas por cobrar: folio, fecha de vencimiento, saldo, saldo vencido, monto original, cliente, vendedor. |
| `objetivo_autos.txt` | Metas comerciales de venta de autos por sucursal y periodo (venta objetivo, unidades objetivo, utilidad objetivo). |
| `objetivos_servicio.txt` | Metas de taller/servicio por sucursal y periodo (órdenes objetivo, venta objetivo, utilidad objetivo). |

## Campos comunes para cruzar información entre archivos

- `Company` / `Razon_Social` / `Sucursal` — identifican la empresa y sucursal.
- `date_key`, `Nombre_Mes`, `Nombre_Mes_Descripcion` — periodo del registro.
- `VIN` — identifica un vehículo específico (presente en venta, inventario y servicio de autos).
- `Clientes` / `Clientes_Descripcion` — identifican al cliente.

## Reglas

1. Antes de responder cualquier pregunta sobre los datos, revisa `schema.ini` para confirmar las columnas y tipos disponibles en el archivo relevante.
2. Si necesitas cruzar información entre archivos, usa los campos comunes listados arriba.
3. Si el nombre de una columna no deja claro su significado de negocio, dilo explícitamente y pregunta en lugar de asumir.
4. No inventes valores ni completes datos faltantes: si un dato no está en el archivo, indícalo.
5. Si aparece un archivo `.txt` no descrito aquí, consulta su sección en `schema.ini` para entender su estructura antes de usarlo.
