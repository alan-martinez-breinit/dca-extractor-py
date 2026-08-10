# Diccionario de Datos — DCA Autopolis

Este documento describe, campo por campo, el significado de negocio de cada columna en las vistas/cubos extraídos del sistema DCA. Complementa a `schema.ini`: `schema.ini` define tipo y estructura técnica de cada columna; este documento define qué representa cada campo en el negocio y qué indicadores se calculan comúnmente a partir de ellos.

Si un campo no aparece documentado aquí para una vista dada, su significado aún no ha sido confirmado — no asumas su propósito solo por el nombre; señálalo como pendiente de confirmar con el negocio.

Los indicadores marcados **(confirmado)** están adaptados de fórmulas reales implementadas en `breinit-backend-dca` (inquilino `0003`, mismo giro de negocio — agencia automotriz — y misma convención de nombres de campo DCA), no inventadas. Como cada distribuidor tiene su propia configuración de extracción DCA, algunos campos que esa fórmula usa no existen en la extracción de Autopolis; cuando eso ocurre se indica explícitamente qué falta y el indicador no se puede calcular tal cual hasta que se confirme un campo equivalente. Los indicadores sin esa marca son sugerencias propias basadas en KPIs estándar de la industria, no verificadas contra ninguna fuente — trátalos con menos confianza.

## Ventas de Autos (`*_ventas_autos_ia.txt`)

Una fila representa un movimiento (venta o cancelación) de una unidad. `Tipo_Movimiento` indica la naturaleza del movimiento; `date_key` es la fecha de ese movimiento.

### Campos

- **date_key** (Date): Fecha de la operación. Si `Tipo_Movimiento` es facturación, es la fecha de facturación; si es cancelación, es la fecha de la cancelación.
- **Tipo_de_Vehiculo** (Char, ancho 15): Modelo/línea del vehículo (ej. `VIRTUS`, `JETTA`, `VERSA`, `FRONTIER`). A pesar del nombre del campo, no es una categoría de carrocería (sedán, SUV, etc.) sino el nombre comercial del modelo.
- **Color** (Char, ancho 30): Color comercial del vehículo tal como lo reporta el fabricante (ej. `PLATA REFLEX`, `AZUL ZAFIRO`).
- **Credito_Contado** (Char, ancho 10): Forma de pago de la unidad: `CONTADO` o `CREDITO`.
- **Fecha_Entrada_Inventario** (Date): Fecha en que la unidad entró al inventario del distribuidor.
- **Marca** (Char, ancho 10): Marca del vehículo (`VW`, `NISSAN`, etc.).
- **VIN** (Char, ancho 17): Identificador único del vehículo — equivalente a una CURP para el auto.
- **Ano_Modelo** (Integer): Año modelo del vehículo.
- **Nuevo_Usado** (Char, ancho 12): Pese al nombre genérico, almacena el tipo de auto: `AUTOS NUEVOS` o `AUTOS USADOS`.
- **Sucursal** (Char, ancho 21): Sucursal/punto de venta donde se realizó la operación (ej. `NISSAN CUMBRES`, `VW LA FE`).
- **Tipo_Movimiento** (Char, ancho 11): Naturaleza del movimiento. Valor observado en muestra: `FACTURACION`. Otros valores posibles (p. ej. cancelación) no están confirmados aún — verificar con negocio.
- **Version_del_Vehiculo** (Char, ancho 55): Descripción completa de versión/equipamiento del vehículo.
- **Tipo_de_Venta** (Char, ancho 13): Canal/tipo de venta. Valores observados: `VENTA`, `FLOTILLA`, `VN CONTADO`, `VN VW LEASING`.
- **Razon_Social** (Char, ancho 18): Razón social del distribuidor/grupo que realizó la venta (ej. `AUTOPOLIS VW`, `AUTOPOLIS CUMBRES`).
- **Clientes** (Integer): Código numérico interno del cliente.
- **Clientes_Descripcion** (Char, ancho 72): Nombre o razón social del cliente.
- **Folio_Factura** (Char, ancho 10): Identificador de la factura; normalmente numérico pero puede incluir una serie alfanumérica (ej. `AE48758`).
- **Segmento** (Char, ancho 10): Segmento del vehículo. Único valor observado en muestra: `AUTO` — puede tener otros valores no vistos en esta muestra.
- **Costo_Neto** (Float): Costo neto de la unidad.
- **Bonificacion_Planta** (Float): Bonificación otorgada por la planta/fabricante sobre la unidad.
- **ISAN** (Float): Impuesto Sobre Automóviles Nuevos aplicado a la operación.
- **IVA** (Float): Impuesto al Valor Agregado de la operación.
- **Nota_Car_Cre_Cliente** (Float): Monto de nota de cargo/crédito aplicada al cliente. Signo y aplicación exacta sin confirmar con negocio.
- **Importe_Factura** (Float): Importe total facturado.
- **Uds_Vendidas** (Float): Unidades vendidas en el registro (normalmente 1 por fila).
- **Uds_Canceladas** (Float): Unidades canceladas en el registro.
- **Vta_Neta** (Float): Venta neta, sin impuestos ni conceptos adicionales.
- **Imp_HoldBack** (Float): Importe de holdback — retención del fabricante sobre el precio, recuperable por el distribuidor.
- **Uds_con_Perdida** (Float): Unidades vendidas por debajo de costo.
- **Costo_Bruto** (Float): Costo bruto de la unidad, antes de bonificaciones.
- **Dias_de_Inventario** (Float): Días que la unidad permaneció en inventario antes de venderse.
- **Uds_Entregadas** (Float): Unidades físicamente entregadas al cliente.
- **Uds_Reportadas** (Float): Unidades reportadas (a fábrica u otro sistema externo). Diferencia exacta con `Uds_Vendidas` sin confirmar con negocio.
- **Reportada_Vta_Neta** (Float): Venta neta correspondiente a las unidades reportadas.
- **Comision_Venta_UDS** (Float): Comisión por unidad vendida.
- **Comision_Venta_CrediNissan** (Float): Comisión asociada a financiamiento CrediNissan.

### Indicadores calculados

No son campos almacenados — se calculan a partir de los campos anteriores. Úsalos cuando el usuario pida métricas de negocio en vez de datos crudos.

**(confirmado)** — todos filtran/agrupan por `Sucursal` y `Nuevo_Usado`, y excluyen `Tipo_de_Venta = INTERCAMBIO` de la venta real (así lo hace el backend al comparar contra objetivo):

- **Margen bruto (aproximado)** = `Vta_Neta − Costo_Neto + Nota_Car_Cre_Cliente + Bonificacion_Planta`. La fórmula confirmada en el backend suma además `Imp_Accesorios + Importe_Bonificacion`; ninguno de los dos campos existe en la extracción de Autopolis, así que este resultado es una aproximación por defecto, no el margen bruto exacto que usa el negocio.
- **% Margen bruto** = `Margen bruto / Vta_Neta`
- **Cumplimiento de venta (día/mes)** = `Σ Vta_Neta (excluyendo INTERCAMBIO) / Obj_Venta_Dia` u `Obj_Venta_Mes` (de `objetivo_autos`, mismo `Sucursal`/`Nuevo_Usado`/periodo) `× 100`
- **Cumplimiento de margen bruto (día/mes)** = `Margen bruto (aproximado) / Obj_Utilidad_Bruta_Dia` u `Obj_Utilidad_Bruta_Mes × 100`
- **Meses de cobertura de inventario** = `Σ Exist` (de `inventario_autos`, mismo `Sucursal`/`Nuevo_Usado`, excluyendo `Auto_Demo`) `/ Obj_Vta_Uds_Mensual`
- **Cartera asociada** = `Σ Saldo` (de `cxc`, filtrando `Area_de_Negocio`) — el backend usa los valores `"Autos Nuevos"` / `"Autos Usados"` para este filtro; no confirmado que la extracción de Autopolis use exactamente esos valores en `Area_de_Negocio` (la única muestra vista fue `"Refacciones"`).

Sugeridos, sin confirmar contra ninguna fuente:

- **Ticket promedio** = `Vta_Neta / Uds_Vendidas`
- **Tasa de cancelación** = `Uds_Canceladas / (Uds_Vendidas + Uds_Canceladas)`
- **Mix Nuevo vs. Usado** = suma de `Uds_Vendidas` agrupada por `Nuevo_Usado`, sobre el total
- **Días promedio en inventario a la venta** = promedio de `Dias_de_Inventario` agrupado por `Sucursal` o `Marca`
- **Comisión total por venta** = `Comision_Venta_UDS + Comision_Venta_CrediNissan`
- **Participación por sucursal** = suma de `Vta_Neta` por `Sucursal`, sobre el total
- **% Ventas a crédito** = suma de `Uds_Vendidas` donde `Credito_Contado = CREDITO`, sobre el total

## Inventario de Autos (`*_inventario_autos_ia.txt`)

Una fila representa una unidad físicamente en inventario a la fecha de corte (`date_key`), a diferencia de `ventas_autos` que representa movimientos.

### Campos

- **date_key** (Date): Fecha de corte de este registro — instantánea del inventario a esa fecha, no una fecha de transacción.
- **Dias_en_Inventario_Rango** (Char, ancho 14): Rango/bucket de antigüedad en inventario (ej. `361 o Mas Dias`, `181 - 360 Dias`). Versión agrupada de `Dias_en_Inv`.
- **Auto_Demo** (Char, ancho 12): Indica si la unidad es vehículo de demostración. Valor observado: `No Auto Demo`.
- **Tipo_de_Vehiculo** (Char, ancho 14): Modelo/línea del vehículo (ej. `KICKS`, `T2`, `L200`, `TAOS`), igual que en `ventas_autos` — no es categoría de carrocería.
- **Color** (Char, ancho 30): Color comercial del vehículo.
- **Propio_Financiado** (Char, ancho 10): Indica si la unidad es propia o financiada (floor plan). En la muestra solo se observaron placeholders (`NA`, `*NA`) — valores reales categóricos sin confirmar.
- **Fecha_Entrada_Inventario** (Date): Fecha en que la unidad entró al inventario del distribuidor.
- **VIN** (Char, ancho 17): Identificador único del vehículo.
- **Marca** (Char, ancho 10): Marca del vehículo.
- **Ano_Modelo** (Integer): Año modelo del vehículo.
- **Num_Inventario** (Char, ancho 10): Número de inventario/stock interno de la unidad (ej. `142223`, `NU32025`).
- **Nuevo_Usado** (Char, ancho 12): `AUTOS NUEVOS` o `AUTOS USADOS`.
- **Sucursal** (Char, ancho 21): Sucursal donde está la unidad.
- **Version_del_Vehiculo** (Char, ancho 50): Descripción de versión/equipamiento.
- **Razon_Social** (Char, ancho 20): Razón social del distribuidor.
- **Tipo_Inventario** (Char, ancho 10): Clasificación del inventario. Valor observado: `VENTA`. Otros valores posibles sin confirmar.
- **Separado** (Char, ancho 10): Indica si la unidad está apartada por un cliente. Valores observados: `No`, `SI`, `0`, `*NA` — inconsistencia de formato entre `No`/`0` para "no apartado"; tratar ambos como equivalentes salvo que el negocio indique lo contrario.
- **Fecha_Separado** (Char, ancho 10): Fecha en que se apartó la unidad. `1900-01-01` es el valor centinela cuando no está apartada, no una fecha real.
- **Vendedor_Separado** (Char, ancho 13): Vendedor que registró el apartado (ej. `rcr`, `PPT1`).
- **Kilometraje** (Char, ancho 10): Kilometraje de la unidad. Valores bajos (`0`, `10`) son consistentes con unidades nuevas.
- **Origen** (Char, ancho 41): Razón social del fabricante/proveedor de origen de la unidad (ej. `NISSAN MEXICANA, S.A. DE C.V.`).
- **Segmento** (Char, ancho 10): Segmento del vehículo. Único valor observado: `AUTO`.
- **Dias_en_Inv** (Float): Días en inventario, versión numérica de `Dias_en_Inventario_Rango`.
- **Inventario** (Float): Valor monetario de la unidad en inventario (costo/valor en libros).
- **Exist** (Float): Bandera/contador de existencia — en la muestra siempre `1.0`. Úsalo para contar unidades al agregar, no como magnitud de negocio.
- **IVA** (Float): IVA asociado al valor de inventario de la unidad.
- **Dias_Separado** (Float): Días que la unidad lleva apartada (`0.0` si no está apartada).

### Indicadores calculados

- **Valor total de inventario** = suma de `Inventario`
- **Antigüedad promedio de inventario** = promedio de `Dias_en_Inv`
- **% Unidades apartadas** = conteo de `Separado = SI` / conteo total
- **Distribución por antigüedad** = conteo agrupado por `Dias_en_Inventario_Rango`
- **Mix Nuevo vs. Usado en inventario** = suma de `Exist` agrupada por `Nuevo_Usado`
- **Valor de inventario por sucursal** = suma de `Inventario` agrupada por `Sucursal`

## Inventario de Refacciones (`*_inventario_refacciones_ia.txt`)

Una fila representa una línea de existencia de una refacción en un almacén, a la fecha de corte.

### Campos

- **date_key** (Date): Fecha de corte del registro.
- **Almacen** (Char, ancho 32): Almacén donde está la existencia (ej. `ALMACEN GENERAL TIENDA VA`).
- **Razon_Social** (Char, ancho 20): Razón social del distribuidor.
- **Rango_Ant_Ult_Compra** (Char, ancho 12): Rango de antigüedad desde la última compra de la refacción (ej. `181-360 DIAS`).
- **Rango_Dias_Venta** (Char, ancho 15): Rango de días relacionado con la venta de la refacción (ej. `MAS DE 720 DIAS`, `000-090 DIAS`). Significado exacto — posible indicador de rotación — sin confirmar; no confundir con `Rango_Ant_Ult_Venta`.
- **Sucursal** (Char, ancho 18): Sucursal asociada.
- **Clasificacion_de_PMC** (Char, ancho 12): Clasificación de movimiento de la pieza (ej. `01. Facil`, `03. Lento`, `04. Nuevo`). El significado exacto de la sigla `PMC` no está confirmado; los valores en sí (fácil/lento/nuevo) indican velocidad de rotación.
- **Fecha_Ult_Venta** (Date): Fecha de la última venta de esta refacción.
- **Rango_Ant_Ult_Venta** (Char, ancho 16): Rango de antigüedad desde la última venta (ej. `091-180 DIAS`).
- **Fecha_Alta_Refaccion** (Date): Fecha en que la refacción se dio de alta en el catálogo.
- **Tipo_Refaccion** (Char, ancho 22): Tipo/origen de la refacción (ej. `Refacciones Nissan`, `REFACC`).
- **Marca** (Char, ancho 10): Marca asociada a la refacción.
- **Antiguedad_Dias_Ult_Venta** (Float): Días desde la última venta, versión numérica de `Rango_Ant_Ult_Venta`.
- **Costo_Inventario** (Float): Valor en costo de la existencia de esta línea.
- **Antiguedad_Dias_Ult_Compra** (Float): Días desde la última compra, versión numérica de `Rango_Ant_Ult_Compra`.
- **Existencia** (Float): Cantidad de piezas en existencia.
- **Cantidad_No_de_Ref** (Float): Constante `3.0` en toda la muestra observada — parece un contador de agrupación, no una cantidad de negocio por fila. Confirmar con negocio antes de usarlo en cálculos.
- **Meses_Antiguedad** (Float): Antigüedad de la refacción en meses.
- **Costo_Unitario** (Float): Costo por unidad de la refacción.

### Indicadores calculados

**(confirmado, concepto)** — `margen_bruto_refacciones_por_canal.py` en el backend calcula "inventario obsoleto" como `Σ Costo_Inventario_MN` filtrando `Rango_Ant_Ult_Compra` en los rangos de mayor antigüedad (`"361-720 DIAS"`, `"721-1080 DIAS"`, `"MAS DE 1080 DIAS"` para ese cliente):

- **Valor de inventario obsoleto** = `Σ Costo_Inventario` filtrando `Rango_Ant_Ult_Compra` en sus rangos de mayor antigüedad. Los nombres exactos de esos rangos para Autopolis no están confirmados — la muestra vista solo mostró `181-360 DIAS`, `091-180 DIAS` y `000-090 DIAS`; el archivo completo (100+ MB) probablemente tiene rangos más altos que no aparecieron en la muestra. Revisa los valores reales de `Rango_Ant_Ult_Compra` en el archivo antes de aplicar este filtro.
- **% Inventario obsoleto** = `Valor de inventario obsoleto / Σ Costo_Inventario`

Sugeridos, sin confirmar contra ninguna fuente:

- **Valor total de inventario de refacciones** = suma de `Costo_Inventario`
- **Antigüedad promedio de última venta** = promedio de `Antiguedad_Dias_Ult_Venta`
- **Refacciones sin venta reciente** = filtrar `Rango_Ant_Ult_Venta` en los rangos más altos (ej. `MAS DE 720 DIAS`)
- **Distribución por clasificación PMC** = conteo/valor agrupado por `Clasificacion_de_PMC`
- **Costo promedio por unidad** = suma de `Costo_Inventario` / suma de `Existencia`
- **Refacciones de movimiento lento** = filtrar `Clasificacion_de_PMC = "03. Lento"`

## Venta de Servicio y Refacciones (`*_venta_servicio_refacciones_ia.txt`)

Cubo del área de taller/posventa (servicio, hojalatería y pintura, refacciones de mostrador). Una fila combina una sucursal, una clasificación de orden y un bucket de antigüedad de órdenes abiertas.

### Campos

- **date_key** (Date): Fecha/periodo del registro.
- **Razon_Social** (Char, ancho 19): Razón social del distribuidor.
- **Marca** (Char, ancho 10): Marca asociada.
- **Sucursal** (Char, ancho 18): Sucursal o marca-sucursal (en sucursales mono-marca puede coincidir con `Marca`).
- **Clase_Tipo_Orden** (Char, ancho 10): Orden de trabajo. Valores observados: `C-ASE`, `C-GRL` — el significado exacto de estos códigos (posiblemente aseguradora / general) no está confirmado.
- **Tipo_Venta_Serv_Most** (Char, ancho 11): Tipo de venta. Valor observado en esta vista: `Servicio`.
- **Sub_Tipo_Venta** (Char, ancho 13): Subtipo dentro de `Tipo_Venta_Serv_Most`. Valores observados: `Refacción`, `Mano Obra`, `TOT` (probablemente "Total"), `NA`.
- **Ant_Dias_Entrega_HyP** (Char, ancho 10): Antigüedad agrupada de entrega para Hojalatería y Pintura (HyP) — expansión de la sigla no confirmada formalmente con negocio.
- **Ant_Dias_Entrega_Servicio** (Char, ancho 10): Antigüedad agrupada de entrega para Servicio general.
- **Ant_Ord_Abiertas_HyP** (Char, ancho 15): Rango de antigüedad de órdenes abiertas en Hojalatería y Pintura.
- **Ant_Ord_Abiertas_Servicio** (Char, ancho 14): Rango de antigüedad de órdenes abiertas en Servicio (ej. `00 - 15 Dias`, `16 - 30 Dias`, ... `Mas de 90 Dias`).
- **Venta** (Float): Venta ya facturada.
- **Venta_en_Proceso** (Float): Venta de órdenes aún no facturadas/en proceso.
- **Venta_Unidades** (Float): Cantidad vendida. Para `Sub_Tipo_Venta = Mano Obra` los valores observados sugieren horas de mano de obra; para `Refacción`, cantidad de piezas — la unidad de medida cambia según `Sub_Tipo_Venta` y no está unificada.
- **Venta_x_Facturar** (Float): Monto pendiente de facturar.
- **Cantidad_Ordenes_Reparacion_en_Proceso** (Float): Número de órdenes de reparación en proceso.
- **Cantidad_Ordenes_Reparacion_Facturadas** (Float): Número de órdenes de reparación facturadas.
- **Cantidad_Ordenes_Reparacion_Pendientes_Fact** (Float): Número de órdenes de reparación pendientes de facturar.
- **Cantidad_Ordenes_Reparacion_Recibidas** (Float): Número de órdenes de reparación recibidas.
- **Cantidad_Ordenes_Reparacion_Terminadas** (Float): Número de órdenes de reparación terminadas.

### Indicadores calculados

**(confirmado)**:

- **Cumplimiento de venta (día/mes)**, por `Sucursal` y departamento (`Tipo_Venta_Serv_Most` = `Servicio` u `Hojalatería`, filtrando `Sub_Tipo_Venta` según el departamento) = `Σ Venta / Obj_Vta_al_Dia` u `Obj_Vta_Mes` (de `objetivos_servicio`) `× 100`
- **Cartera asociada** = `Σ Saldo` (de `cxc`, filtrando `Area_de_Negocio` — el backend usa `"Servicio"` y `"Hojalateria"`; valores exactos para Autopolis sin confirmar)

**No calculables con la extracción actual de Autopolis** (el backend sí los implementa para otro cliente, pero requieren campos que Autopolis no exporta en esta vista):

- **Margen bruto de taller/HyP/refacciones de mostrador** = en el backend es `Venta − Costo_Neto`. `venta_servicio_refacciones` de Autopolis no tiene columna `Costo_Neto` — no hay forma de calcular este margen con los datos actuales. Si el negocio necesita esta métrica, habría que solicitar que la extracción DCA de Autopolis incluya `Costo_Neto` en esta vista.
- **Ticket promedio objetivo y su variación contra el real** = el backend los calcula desde `Ticket_Prom_Objetivo_Taller` y `Ticket_Prom_Objetivo_HyP` en `objetivos_servicio`. Ninguno de los dos campos existe en la extracción de Autopolis.
- **Ticket promedio real (taller)**, tal como lo define el backend, = `Σ Saldo (cxc, Servicio) / Σ Cantidad_Ordenes_Reparacion_Facturadas` filtrando `Clase_Tipo_Orden = "Publico"`. Autopolis sí tiene `Clase_Tipo_Orden`, pero los valores observados en su muestra son `C-ASE` y `C-GRL`, no `Publico` — cada distribuidor parece tener su propia taxonomía de códigos de orden. No asumas que `C-ASE`/`C-GRL` equivalen a "público"; confírmalo con negocio antes de replicar este filtro.

Sugeridos, sin confirmar contra ninguna fuente:

- **Venta total de taller** = `Venta + Venta_en_Proceso`
- **% Órdenes pendientes de facturar** = `Cantidad_Ordenes_Reparacion_Pendientes_Fact / Cantidad_Ordenes_Reparacion_Recibidas`
- **Tasa de cierre de órdenes** = `Cantidad_Ordenes_Reparacion_Terminadas / Cantidad_Ordenes_Reparacion_Recibidas`
- **Venta pendiente de facturar** = suma de `Venta_x_Facturar`
- **Mix Refacción vs. Mano de Obra** = suma de `Venta_en_Proceso` agrupada por `Sub_Tipo_Venta`
- **Distribución de antigüedad de órdenes abiertas** = conteo agrupado por `Ant_Ord_Abiertas_Servicio` o `Ant_Ord_Abiertas_HyP`

## Cuentas por Cobrar (`*_cxc_ia.txt`)

Una fila representa un saldo pendiente (factura, nota, etc.) a la fecha de corte.

### Campos

- **date_key** (Date): Fecha de corte del saldo.
- **Razon_Social** (Char, ancho 20): Razón social del distribuidor.
- **Sucursal** (Char, ancho 21): Sucursal asociada al saldo.
- **Rango_Antiguedad** (Char, ancho 15): Rango de antigüedad del saldo (ej. `Por Vencer`, `61-90 Dias`).
- **Vencido_Por_Vencer** (Char, ancho 10): Indica si el saldo está `Vencido` o `Por Vencer`.
- **Area_de_Negocio** (Char, ancho 12): Área de negocio origen del saldo (ej. `Refacciones`; también aplican Autos y Servicio aunque no se observaron en la muestra).
- **Tipo_de_Movimiento** (Char, ancho 10): Tipo de movimiento contable. Valor observado: `Factura`. Otros tipos (notas de cargo/crédito, pagos) no confirmados en muestra.
- **Clasificacion_de_Cartera** (Char, ancho 11): Clasificación de la cartera. Valor observado: `Aplicado`.
- **Subarea_de_Negocio** (Char, ancho 27): Subárea de negocio (ej. `Mostrador`).
- **Dias_Antiguedad** (Float): Días de antigüedad del saldo. Negativo = días que faltan para vencer; positivo = días vencido.
- **Saldo** (Float): Saldo total pendiente.
- **Saldo_Vencido** (Float): Porción del saldo ya vencida.
- **Saldo_por_Vencer** (Float): Porción del saldo aún no vencida.
- **Monto_Original** (Float): Monto original de la transacción que generó el saldo.

### Indicadores calculados

No se encontró en `breinit-backend-dca` un indicador propio de CxC más allá de usar `Saldo` como insumo de "cartera" en los reportes de otras vistas (ver `ventas_autos` y `venta_servicio_refacciones`). Los siguientes son sugeridos, sin confirmar contra ninguna fuente:

- **Cartera vencida total** = suma de `Saldo_Vencido`
- **% Cartera vencida** = suma de `Saldo_Vencido` / suma de `Saldo`
- **Antigüedad promedio ponderada** = suma de `(Dias_Antiguedad × Saldo)` / suma de `Saldo`
- **Cartera por sucursal** = suma de `Saldo` agrupada por `Sucursal`
- **Distribución por rango de antigüedad** = suma de `Saldo` agrupada por `Rango_Antiguedad`
- **Cartera por área de negocio** = suma de `Saldo` agrupada por `Area_de_Negocio`

## Objetivo Autos (`*_objetivo_autos_ia.txt`)

Cubo de metas comerciales mensuales de venta de autos, por sucursal/tipo de venta. Se cruza contra `ventas_autos` para medir cumplimiento (ver "Relaciones entre vistas" al final).

### Campos

- **date_key** (Date): Fecha del periodo objetivo (coincide con `Fec_iniOP`).
- **Sucursal** (Char, ancho 21): Sucursal a la que aplica el objetivo.
- **Nuevo_Usado** (Char, ancho 12): `AUTOS NUEVOS` o `AUTOS USADOS` — segmento al que aplica el objetivo.
- **Company** (Char, ancho 10): Agrupador de compañía (valor observado: `Autopolis`), más general que `Razon_Social`.
- **Razon_Social** (Char, ancho 20): Razón social específica del distribuidor.
- **Fec_iniOP** (Date): Fecha de inicio de la operación/periodo objetivo.
- **Fec_finOP** (Date): Fecha de fin de la operación/periodo objetivo.
- **Tipo_de_Vehiculo** (Char, ancho 10): Modelo al que aplica el objetivo. Valor observado en muestra: `NA` (objetivo no segmentado por modelo).
- **Nombre_Mes** (Integer): Número de mes del periodo (ej. `01`).
- **Nombre_Mes_Descripcion** (Char, ancho 10): Abreviatura del mes (ej. `Ene`).
- **Tipo_de_Venta** (Char, ancho 17): Canal de venta al que aplica el objetivo (`VENTA`, `FLOTILLA`, `INTERCAMBIO`, `VN VW LEASING`, etc., ver también `ventas_autos`).
- **Obj_Meses_Vta_en_Inv** (Char, ancho 10): Objetivo de meses de inventario. Tipado como texto en `schema.ini` pese a ser numérico; valores vacíos observados en la muestra.
- **Obj_Utilidad_Bruta_pct_sa** (Float): Objetivo de % de utilidad bruta (ej. `0.05505` = 5.5%). El sufijo `_sa` no está confirmado (posible "sin ajuste").
- **Obj_Precio_Promedio_x_Unidad** (Float): Objetivo de precio promedio por unidad.
- **Obj_Vta_Uds_al_Dia** (Float): Objetivo de unidades vendidas por día.
- **Obj_Vta_Uds_Mensual** (Float): Objetivo de unidades vendidas en el mes.
- **Obj_Venta_Mes** (Float): Objetivo de venta en pesos para el mes.
- **Obj_Venta_Dia** (Float): Objetivo de venta en pesos por día.
- **Obj_Utilidad_Bruta_Mes** (Float): Objetivo de utilidad bruta del mes.
- **Obj_Utilidad_Bruta_Dia** (Float): Objetivo de utilidad bruta por día.

### Indicadores calculados (requieren cruzar con `ventas_autos`)

Las fórmulas confirmadas de cumplimiento de venta, cumplimiento de margen bruto y meses de cobertura de inventario que usan los campos de esta vista están documentadas en la sección "Indicadores calculados" de **Ventas de Autos** (arriba) — se repiten ahí porque el punto de partida natural es la vista de venta, no la de objetivo. Este cubo aporta el lado `Obj_*` de esas comparaciones.

Sugerido, sin confirmar:

- **Avance esperado a la fecha** = `Obj_Venta_Dia × días transcurridos del periodo`, comparado contra venta acumulada real

## Objetivos Servicio (`*_objetivos_servicio_ia.txt`)

Cubo de metas comerciales mensuales del área de servicio/refacciones, por sucursal y sub-tipo de venta. Se cruza contra `venta_servicio_refacciones` para medir cumplimiento.

### Campos

- **date_key** (Date): Fecha del periodo objetivo.
- **Razon_Social** (Char, ancho 20): Razón social del distribuidor.
- **Sucursal** (Char, ancho 21): Sucursal a la que aplica el objetivo.
- **Company** (Char, ancho 10): Agrupador de compañía (valor observado: `Autopolis`).
- **Tipo_Venta_Serv_Most** (Char, ancho 11): Tipo de venta al que aplica el objetivo (ej. `REFACCIONES`, `Servicio`, `Hojalatería`).
- **Sub_Tipo_Venta** (Char, ancho 10): Subtipo dentro de `Tipo_Venta_Serv_Most` (`Refacción`, `Mano Obra`, `TOT`, `NA`).
- **Asesor** (Char, ancho 10): Asesor de servicio asignado. Valor observado en muestra: `NA` (objetivo no segmentado por asesor).
- **Fec_iniOP** (Date): Fecha de inicio de la operación/periodo objetivo.
- **Fec_finOP** (Date): Fecha de fin de la operación/periodo objetivo.
- **Nombre_Mes** (Integer): Número de mes del periodo.
- **Nombre_Mes_Descripcion** (Char, ancho 10): Abreviatura del mes.
- **Vendedor_Mostrador** (Char, ancho 10): Vendedor de mostrador de refacciones asignado. Valor observado en muestra: `*NA`.
- **Obj_Ordenes_Reparacion** (Float): Objetivo de número de órdenes de reparación.
- **Obj_Vta_al_Dia** (Float): Objetivo de venta por día.
- **Obj_Utilidad_pct** (Float): Objetivo de % de utilidad. Puede venir vacío en filas donde el objetivo de esa fila es de órdenes (`Obj_Ordenes_Reparacion`) y no de venta/utilidad — no todas las filas usan todas las columnas `Obj_*`.
- **Obj_Utilidad_al_Dia** (Float): Objetivo de utilidad por día.
- **Obj_Utilidad_Mes** (Float): Objetivo de utilidad del mes.
- **Obj_Vta_Mes** (Float): Objetivo de venta del mes.
- **Obj_Ordenes_Reparacion_al_Dia** (Float): Objetivo de órdenes de reparación por día.

### Indicadores calculados (requieren cruzar con `venta_servicio_refacciones`)

La fórmula confirmada de cumplimiento de venta (día/mes) está documentada en la sección "Indicadores calculados" de **Venta de Servicio y Refacciones** (arriba), junto con la nota de qué indicadores de esta vista (ticket promedio objetivo, cumplimiento de margen) no se pueden calcular por falta de campos (`Costo_Neto`, `Ticket_Prom_Objetivo_Taller`, `Ticket_Prom_Objetivo_HyP`) en la extracción de Autopolis.

Sugerido, sin confirmar:

- **Cumplimiento de órdenes de reparación** = `Cantidad_Ordenes_Reparacion_Terminadas` real / `Obj_Ordenes_Reparacion`

## Relaciones entre vistas (real vs. objetivo)

- `ventas_autos` (real) se compara contra `objetivo_autos` (meta) usando como llave `Sucursal` + `Nombre_Mes`/periodo. `Nuevo_Usado` y `Tipo_de_Venta` también deben coincidir si el objetivo está segmentado por ellos.
- `venta_servicio_refacciones` (real) se compara contra `objetivos_servicio` (meta) usando como llave `Sucursal` + `Tipo_Venta_Serv_Most` + `Sub_Tipo_Venta` + periodo.
- Antes de sumar montos de un objetivo contra el real, confirma que ambos cubren exactamente el mismo periodo (`Fec_iniOP`/`Fec_finOP` vs. `date_key`) y el mismo alcance (sucursal, segmento) — sumar a un nivel distinto del que el objetivo fue definido produce comparaciones incorrectas.
