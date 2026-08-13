# Diccionario de Datos — DCA Autopolis

Este documento describe, campo por campo, el significado de negocio de cada columna en las vistas/cubos extraídos del sistema DCA. Complementa a `schema.ini`: `schema.ini` define tipo y estructura técnica de cada columna; este documento define qué representa cada campo en el negocio y qué indicadores se calculan comúnmente a partir de ellos.

Si un campo no aparece documentado aquí para una vista dada, su significado aún no ha sido confirmado — no asumas su propósito solo por el nombre; Pregunta si el significado que estas asumiendo es el correcto.

---

## Campos Globales

Campos que aparecen igual en más de una vista — documentados aquí una sola vez en vez de repetirlos. `date_key` se documenta en cada vista porque su significado cambia según la vista (fecha de operación vs. fecha de corte).

- **VIN**: Identificador único del vehículo — equivalente a una CURP para el auto.
- **Tipo_de_Vehiculo**: Modelo/línea del vehículo (ej. `VIRTUS`, `JETTA`, `KICKS`, `TAOS`). A pesar del nombre del campo, no es categoría de carrocería (sedán, SUV, etc.) sino el nombre comercial del modelo.
- **Color**: Color comercial del vehículo tal como lo reporta el fabricante (ej. `PLATA REFLEX`, `AZUL ZAFIRO`).
- **Fecha_Entrada_Inventario**: Fecha en que la unidad entró al inventario del distribuidor.
- **Marca**: Marca del vehículo (`VW`, `NISSAN`, etc.).
- **Ano_Modelo**: Año modelo del vehículo.
- **Nuevo_Usado**: Pese al nombre genérico, almacena la separación de autos: `AUTOS NUEVOS` o `AUTOS USADOS`.
- **Sucursal**: Sucursal del distribuidor (ej. `NISSAN CUMBRES`, `VW LA FE`).
- **Version_del_Vehiculo**: Descripción detallada del vehiculo, como la versión/equipamiento.
- **Razon_Social**: Razón social del distribuidor/grupo (ej. `AUTOPOLIS VW`, `AUTOPOLIS CUMBRES`).
- **Segmento**: Segmento del vehículo. Único valor observado: `AUTO`.

---

## Ventas de Autos (`*_ventas_autos_ia.txt`)

Una fila representa un movimiento de una unidad. `Tipo_Movimiento` indica la naturaleza del movimiento; `date_key` es la fecha de ese movimiento.

### Campos

- **date_key**: Periodo de la operación. Si Tipo_Movimiento es facturacion , es la fecha de facturacion; si es cancelacion es la fecha de la cancelacion, en caso de que el indicador de Uds_Entregadas sea el que este lleno, la fecha pertenece a la Fecha de entrega de la unidad.
- **Credito_Contado**: Forma de pago de la unidad: `CONTADO` o `CREDITO`.
- **Tipo_Movimiento**: Naturaleza del movimiento. Valor observado en muestra: `FACTURACION`y `CANCELACION`.
- **Tipo_de_Venta**: Canal o tipo de venta. Valores Observados:`VENTA`, `FLOTILLA`, `INTERCAMBIO`, `MENUDEO`, `VN CONTADO`. Por default excluir el tipo de `INTERCAMBIO` y las que lleven la palabra `CONCESIONARIAS`.
- **Clientes**: Código numérico interno del cliente.
- **Clientes_Descripcion**: Nombre o razón social del cliente.
- **Folio_Factura**: Identificador de la factura; normalmente numérico pero puede incluir una serie alfanumérica (ej. `AE48758`).
- **Costo_Neto**: Costo neto de la unidad.
- **Bonificacion_Planta**: Bonificación otorgada por la planta/fabricante sobre la unidad.
- **ISAN**: Impuesto Sobre Automóviles Nuevos aplicado a la operación.
- **IVA**: Impuesto al Valor Agregado de la operación.
- **Nota_Car_Cre_Cliente**: Monto de nota de cargo/crédito aplicada al vehiculo y aplicación depende el mismo de movimiento
- **Importe_Factura**: Importe total facturado incluye todo los impuestos
- **Uds_Vendidas**: Unidades vendidas netas del periodo, es decir todas las facturas positivas menos las facturas negativas del mes.
- **Uds_Canceladas**: Unidades canceladas en el periodo.
- **Vta_Neta**: Venta neta, sin impuestos ni conceptos adicionales.
- **Imp_HoldBack**: Importe de holdback — retención del fabricante sobre el precio, recuperable por el distribuidor.
- **Uds_con_Perdida**: Unidades vendidas por debajo de costo.
- **Costo_Bruto**: Costo bruto de la unidad, antes de bonificaciones.
- **Dias_de_Inventario**: Días que la unidad permaneció en inventario antes de venderse.
- **Uds_Entregadas**: Unidades físicamente entregadas al cliente.
- **Uds_Reportadas**: Unidades reportadas (a la planta u otro sistema externo).
- **Reportada_Vta_Neta**: Venta neta correspondiente a las unidades reportadas.
- **Comision_Venta_UDS**: Comisión por unidad vendida.
- **Comision_Venta_CrediNissan**: Comisión asociada a financiamiento CrediNissan.

### Indicadores de Calculo

No son campos del archivo — se calculan a partir de los campos de arriba. Úsalos cuando pidan una métrica de negocio (utilidad, porcentaje de utilidad) en vez de un dato crudo.

- **Utilidad Bruta $** — Fórmula: {**Vta_Neta**} -({**Costo_Bruto**}-{**Bonificacion_Planta**})
- **Utilidad Bruta %** — Fórmula: (({**Vta_Neta**} -({**Costo_Bruto**}-{**Bonificacion_Planta**}) ) / {**Vta_Neta**})

---

## Inventario de Autos (`*_inventario_autos_ia.txt`)

Una fila representa una unidad físicamente en inventario a la fecha de corte (`date_key`), a diferencia de `ventas_autos` que representa movimientos.

### Campos

- **date_key**: Periodo al que pertenece al inventario al final del ultimo dia de ese mes , no una fecha de transacción.
- **Dias_en_Inventario_Rango**: Rango de antigüedad en inventario (ej. `361 o Mas Dias`, `181 - 360 Dias`). Versión agrupada de `Dias_en_Inv`.
- **Auto_Demo**: Indica si la unidad es vehículo de demostración. Valor observado: `No Auto Demo` y `Auto Demo`.
- **Propio_Financiado**: Indica si la unidad es propia o financiada. En la muestra solo se observaron placeholders (`NA`, `*NA`) — valores reales no están identificados.
- **Num_Inventario**: Número de inventario/stock interno de la unidad dentro del concesionario (ej. `142223`, `NU32025`).
- **Tipo_Inventario**: Clasificación del inventario. Valor observado: `VENTA` y `FLOTILLA`.
- **Separado**: Indica si la unidad está apartada por un cliente. Valores observados: `No`, `SI`, `0`, `*NA` — cualquier valor distinto de `No`/`Si` se trata como `NA`.
- **Fecha_Separado**: Fecha en que se apartó la unidad. `1900-01-01` es el valor default cuando no está apartada.
- **Vendedor_Separado**: Vendedor que registró el apartado (ej. `rcr`, `PPT1`).
- **Kilometraje**: Kilometraje de la unidad. Valores bajos (`0`, `10`) son consistentes con unidades nuevas.
- **Origen**: Razón social del fabricante/proveedor de origen de la unidad (ej. `NISSAN MEXICANA, S.A. DE C.V.`).
- **Dias_en_Inv**: Días en inventario, versión numérica de `Dias_en_Inventario_Rango`.
- **Inventario**: Valor monetario de la unidad en inventario (costo/valor en libros).
- **Exist**: contador de existencia — vale `1`. Úsalo para contabilizar las unidades.
- **IVA**: IVA asociado al valor de inventario de la unidad.
- **Dias_Separado**: Días que la unidad lleva apartada (`0` si no está apartada).

---

## Inventario de Refacciones (`*_inventario_refacciones_ia.txt`)

Una fila representa una línea de existencia de una refacción en un almacén, a la fecha de corte.

### Campos

- **date_key**: Periodo al que pertenece al inventario al final del ultimo dia de ese mes , no una fecha de transacción.
- **Almacen**: Almacén donde está la existencia (ej. `ALMACEN GENERAL TIENDA VA`).
- **Rango_Ant_Ult_Compra**: Rango de antigüedad desde la última compra de la refacción (ej. `181-360 DIAS`).
- **Rango_Dias_Venta**: Rango de días relacionado con la venta de la refacción (ej. `MAS DE 720 DIAS`, `000-090 DIAS`).— posible indicador de rotación; no confundir con `Rango_Ant_Ult_Venta`.
- **Clasificacion_de_PMC**: Clasificación de movimiento de la pieza (ej. `01. Facil`, `03. Lento`, `04. Nuevo`); los valores en sí (fácil/lento/nuevo) indican velocidad de rotación.
- **Fecha_Ult_Venta**: Fecha de la última venta de esta refacción.
- **Rango_Ant_Ult_Venta**: Rango de antigüedad desde la última venta (ej. `091-180 DIAS`).
- **Fecha_Alta_Refaccion**: Fecha en que la refacción se dio de alta en el catálogo.
- **Tipo_Refaccion**: Tipo/origen de la refacción (ej. `Refacciones Nissan`, `REFACC`).
- **Antiguedad_Dias_Ult_Venta**: Días desde la última venta, versión numérica de `Rango_Ant_Ult_Venta`.
- **Costo_Inventario**: Valor en costo de la existencia.
- **Antiguedad_Dias_Ult_Compra**: Días desde la última compra, versión numérica de `Rango_Ant_Ult_Compra`.
- **Existencia**: Cantidad de piezas en existencia.
- **Cantidad_No_de_Ref**: la cantidad de los diferentes tipos de refacciones en inventario.
- **Meses_Antiguedad**: Antigüedad de la refacción en meses.
- **Costo_Unitario**: Costo por unidad de la refacción.

---

## Venta de Servicio y Refacciones (`*_venta_servicio_refacciones_ia.txt`)

Cubo del área de taller/posventa (servicio, hojalatería y pintura, refacciones de mostrador).

### Campos

- **date_key**: Periodo de la operación. Si Tipo_Movimiento es facturacion , es la fecha de facturacion; si es cancelacion es la fecha de la cancelacion, para los indicadores de Abiertas, en proceso y pendientes por facturar la fecha indica el periodo al que pertenece al final del ultimo dia de ese mes , no una fecha de transacción.
- **Clase_Tipo_Orden**: Clasificación del tipo de orden de trabajo. Valores observados: `C-GRL`, `Colision`, `G-GAR`, `GARANTIA`, `Interno`, `MAYOREO`, `Mostrador`, `NA`, `PUBLICO`. La columna mezcla códigos abreviados (`C-GRL`, `G-GAR`) y nombres completos (`GARANTIA`, `Interno`, etc.) sin un mapeo documentado entre ellos — trátalos como valores independientes, no asumas que un código y un nombre completo son equivalentes salvo que el negocio lo confirme.
- **Tipo_Venta_Serv_Most**: Tipo de venta del departamento de postventa.Valor observado en esta vista: `SERVICIO`, `REFACCIONES`, `HOJALATERIA`.
- **Sub_Tipo_Venta**: Subtipo de venta dentro del área de postventa. Valores observados: `Refacción`, `Mano Obra`, `TOT`, `NA`.
- **Ant_Dias_Entrega_HyP**: Antigüedad agrupada de entrega para Hojalatería y Pintura (HyP) — cuántos días se tardaron en entregar el vehículo.
- **Ant_Dias_Entrega_Servicio**: Antigüedad agrupada de entrega para Servicio general — cuántos días se tardaron en entregar el vehículo.
- **Ant_Ord_Abiertas_HyP**: Rango de antigüedad de órdenes abiertas en Hojalatería y Pintura — días en hyp desde que se inició la orden. Tiene relacion a las ordenes abiertas, es decir En proceso y Pendientes por Facturar.
- **Ant_Ord_Abiertas_Servicio**: Rango de antigüedad de órdenes abiertas en Servicio (ej. `00 - 15 Dias`, `16 - 30 Dias`, ... `Mas de 90 Dias`) — días en taller desde que se inició la orden. Tiene relacion a las ordenes abiertas, es decir En proceso y Pendientes por Facturar.
- **Venta**: Venta ya facturada.
- **Costo_Neto**: Costo neto de la orden facturada — usado junto con `Venta` para calcular `Utilidad Bruta`.
- **Venta_en_Proceso**: Venta de órdenes aún no facturadas ni terminadas — estatus "en proceso".
- **Venta_Unidades**: Cantidad vendida. Para `Sub_Tipo_Venta = Mano Obra` los valores observados sugieren horas de mano de obra; para `Refacción`, cantidad de piezas — la unidad de medida cambia según `Sub_Tipo_Venta` y no está unificada.
- **Venta_x_Facturar**: Venta de órdenes ya terminadas pero aún no facturadas — estatus "pendiente por facturar".
- **Cantidad_Ordenes_Reparacion_en_Proceso**: Número de órdenes de reparación en proceso, el valor se maneja como un saldo, es decir lo que se tiene "En Proceso" al ultimo dia del mes del periodo.
- **Cantidad_Ordenes_Reparacion_Facturadas**: Número de órdenes de reparación facturadas.
- **Cantidad_Ordenes_Reparacion_Pendientes_Fact**: Número de órdenes de reparación pendientes de facturar, el valor se maneja como un saldo, es decir lo que se tiene "pendiente por facturar" al ultimo dia del mes del periodo.
- **Cantidad_Ordenes_Reparacion_Recibidas**: Número de órdenes de reparación recibidas. en el mes
- **Cantidad_Ordenes_Reparacion_Terminadas**: Número de órdenes de reparación terminadas. en el mes
- **Cantidad_Servicios_x_VIN**: Numero de los diferentes VIN por Servicios
- **Cantidad_VIN_en_Proceso**: Numero de los diferentes VIN en proceso
- **Cantidad_VIN_Facturados**: Numero de los diferentes VIN facturados
- **Cantidad_VIN_Pendientes_Fact**: Numero de los diferentes VIN pendientes de facturar
- **Cantidad_VIN_Recibidos**: Numero de los diferentes VIN recibidos en el mes
- **Cantidad_VIN_Terminados**: Numero de los diferentes VIN terminados en el mes

### Indicadores de Calculo

- **Utilidad Bruta** — Fórmula: {**Venta**} - {**Costo_Neto**}
- **Utilidad Bruta %** — Fórmula: {**Utilidad Bruta**} / {**Venta**}
- **Cantidad Ordenes Reparacion Abiertas** — Fórmula: {**Cantidad_Ordenes_Reparacion_en_Proceso**} + {**Cantidad_Ordenes_Reparacion_Pendientes_Fact**}
- **Cantidad VIN Abiertas** — Fórmula: {**Cantidad_VIN_en_Proceso**} + {**Cantidad_VIN_Pendientes_Fact**}
- **Venta Promedio X Orden** — Fórmula: {**Venta**} / {**Cantidad_Ordenes_Reparacion_Facturadas**}
- **Venta Abiertas** — Fórmula: {**Venta_en_Proceso**} + {**Venta_x_Facturar**}

---

## Cuentas por Cobrar (`*_cxc_ia.txt`)

Una fila representa un saldo pendiente (factura, nota, etc.) a la fecha de corte.

### Campos

- **date_key**: Fecha de corte del saldo — instantánea de la cartera a esa fecha, no una fecha de transacción.
- **Rango_Antiguedad**: Rango de antigüedad de vencimiento del saldo (ej. `Por Vencer`, `61-90 Dias`).
- **Vencido_Por_Vencer**: Indica si el saldo está `Vencido` o `Por Vencer`.
- **Area_de_Negocio**: Departamento origen del saldo.
- **Tipo_de_Movimiento**: Tipo de movimiento contable. Valores observados: `Factura`, `ANTICIPO`.
- **Clasificacion_de_Cartera**: Clasificación de la cartera. Valor observado: `Aplicado`. Identifica si el documento está relacionado/aplicado a la factura emitida.
- **Subarea_de_Negocio**: Subárea de negocio (ej. `Mostrador`) — descripción detallada del departamento al que pertenece.
- **Dias_Antiguedad**: Días de antigüedad del saldo. Negativo = días que faltan para vencer; positivo = días vencido.
- **Saldo**: Saldo total en cartera.
- **Saldo_Vencido**: Valor del saldo ya vencido.
- **Saldo_por_Vencer**: Valor del saldo aún no vencido.
- **Monto_Original**: Monto original de la transacción que generó el saldo.

---

## Objetivo Autos (`*_objetivo_autos_ia.txt`)

Cubo de metas comerciales mensuales de venta de autos, por sucursal/tipo de venta. Se cruza contra `ventas_autos` para medir cumplimiento.

### Campos

- **date_key**: Fecha de corte de los objetivos — instantánea de las metas a ese mes, no una fecha de transacción.
- **Company**: Identificador de Servidor en BI. Nunca utilizar dentro de reportes o analizar a ese nivel.
- **Fec_iniOP**: Fecha de inicio de la carga del mes de objetivo. **Almacenada como texto (`varchar`), no como fecha nativa** — no asumas que el orden alfabético del string equivale a orden cronológico; parsea primero como fecha antes de comparar o filtrar rangos. nunca utilices este campo para reportes o analizar a este nivel.
- **Fec_finOP**: Fecha de fin de la carga del mes de objetivo. Mismo aviso que `Fec_iniOP`: es texto, no fecha nativa. nunca utilices este campo para reportes o analizar a este nivel.
- **Tipo_de_Vehiculo**: tipo de vehiculo al que aplica el objetivo. Valor observado en muestra: `NA` (objetivo no segmentado por modelo) — a diferencia del `Tipo_de_Vehiculo` global, aquí prácticamente no se usa.
- **Nombre_Mes**: Número de mes del periodo (ej. `01`). Almacenado como texto, no debe usarse para mostrar en reportes, solo es informativo internamente.
- **Nombre_Mes_Descripcion**: Abreviatura del mes (ej. `Ene`).
- **Tipo_de_Venta**: Canal de venta al que aplica el objetivo (`VENTA`, `FLOTILLA`, `INTERCAMBIO`, `VN VW LEASING`, etc., ver también `ventas_autos`).
- **Obj_Meses_Vta_en_Inv**: Objetivo de meses de inventario. Numérico en la base real (no texto, pese a lo que sugiere `schema.ini` en algunas extracciones).
- **Obj_Utilidad_Bruta_pct_sa**: Objetivo de % de utilidad bruta (ej. `0.05505` = 5.5%). El sufijo `_sa` no debe mostrarse. Se llama solo "% Objetivo Utilidad Bruta". verificar que los datos correspondan al resultado en % de la formula "Objetivo Utilidad Bruta/Objetivo Venta"
- **Obj_Precio_Promedio_x_Unidad**: Objetivo de precio promedio por unidad.
- **Obj_Vta_Uds_al_Dia**: Objetivo de unidades vendidas al día. Valor se va moviendo durante el transcurso del mes, pero al cierre de mes o meses cerrados, debe tener el mismo valor de "Obj_Vta_Uds_Mensual"
- **Obj_Vta_Uds_Mensual**: Objetivo de unidades vendidas en el mes.
- **Obj_Venta_Mes**: Objetivo de venta en pesos para el mes.
- **Obj_Venta_Dia**: Objetivo de venta en pesos al día. Valor se va moviendo durante el transcurso del mes, pero al cierre de mes o meses cerrados, debe tener el mismo valor de "Obj_Venta_Mes"
- **Obj_Utilidad_Bruta_Mes**: Objetivo de utilidad bruta del mes.
- **Obj_Utilidad_Bruta_Dia**: Objetivo de utilidad bruta al día.  Valor se va moviendo durante el transcurso del mes, pero al cierre de mes o meses cerrados, debe tener el mismo valor de "Obj_Utilidad_Bruta_Mes"

---

## Objetivos Servicio (`*_objetivos_servicio_ia.txt`)

Cubo de metas comerciales mensuales del área de servicio/refacciones, por sucursal y sub-tipo de venta. Se cruza contra `venta_servicio_refacciones` para medir cumplimiento.

Mismo caso que `Objetivo Autos`: `Fec_iniOP`/`Fec_finOP` confirmados como texto (`varchar`) en la base real, no `DATE`. Fecha de inicio/Fecha fin de la carga del mes de objetivo. Nunca utilices este campo para reportes o analizar a este nivel.

### Campos

- **date_key**: Fecha del periodo objetivo.
- **Company**: Identificador de Servidor en BI. Nunca utilizar dentro de reportes o analizar a ese nivel.
- **Tipo_Venta_Serv_Most**: Tipo de venta al que aplica el objetivo (ej. `REFACCIONES`, `Servicio`, `Hojalatería`).
- **Sub_Tipo_Venta**: Subtipo dentro de `Tipo_Venta_Serv_Most` (`Refacción`, `Mano Obra`, `TOT`, `NA`).
- **Asesor**: Asesor de servicio asignado. Valor observado en muestra: `NA` (objetivo no segmentado por asesor).
- **Fec_iniOP**: Fecha de inicio de la carga del mes de objetivo. Nunca utilices este campo para reportes o analizar a este nivel.
- **Fec_finOP**: Fecha de fin de la carga del mes de objetivo. Mismo aviso que `Fec_iniOP`: es texto, no fecha nativa. Nunca utilices este campo para reportes o analizar a este nivel.
- **Nombre_Mes**: Número de mes del periodo (ej. `01`). Almacenado como texto, no debe usarse para mostrar en reportes, solo es informativo internamente.
- **Nombre_Mes_Descripcion**: Abreviatura del mes.
- **Vendedor_Mostrador**: Vendedor de mostrador de refacciones asignado. Valor observado en muestra: `*NA`.
- **Obj_Ordenes_Reparacion**: Objetivo de número de órdenes de reparación facturadas.
- **Obj_Vta_al_Dia**: Objetivo de venta al día. Valor se va moviendo durante el transcurso del mes, pero al cierre de mes o meses cerrados, debe tener el mismo valor de "Obj_Vta_Mes"
- **Obj_Utilidad_pct**: Objetivo de % de utilidad. Puede venir vacío en filas donde el objetivo de esa fila es de órdenes (`Obj_Ordenes_Reparacion`). Verificar que los datos correspondan al resultado en % de la formula "Objetivo Utilidad/Objetivo Vta"
- **Obj_Utilidad_al_Dia**: Objetivo de utilidad al día. Valor se va moviendo durante el transcurso del mes, pero al cierre de mes o meses cerrados, debe tener el mismo valor de "Obj_Utilidad_Mes"
- **Obj_Utilidad_Mes**: Objetivo de utilidad del mes.
- **Obj_Vta_Mes**: Objetivo de venta del mes.
- **Obj_Ordenes_Reparacion_al_Dia**: Objetivo de órdenes de reparación al día.  Valor se va moviendo durante el transcurso del mes, pero al cierre de mes o meses cerrados, debe tener el mismo valor de "Obj_Ordenes_Reparacion"

---

## Finanzas (`*_finanzas_ia.txt`)

Cubo contable: Balance General y Estado de Resultados. Una fila es una línea/concepto contable de un reporte, para una sucursal y un periodo. Jerarquía de clasificación de 6 niveles: `Rubro_Global` → `Rubro` → `Agrupador_Nivel_1` → `Agrupador_Nivel_2` → `Agrupador_Nivel_3` → `Agrupador_Nivel_4` (cada nivel es más granular; los códigos numéricos parecen anidarse — el código de un nivel empieza con el código del nivel anterior) Los codigos se usan para darle un ordenamiento a los conceptos descriptivos de cada agrupador.

### Campos

- **date_key**: Fecha del registro. Fecha de corte de la contabilidad a esa fecha, no una fecha de transacción.
- **Company**: Agrupador de compañía (valor observado: `Autopolis`, `Autopolis VW`). No usarse para ningun reporte o analizar a ese detalle
- **Area_de_Negocio**: Departamento/área del negocio al que pertenece la línea contable. Valores observados: `Administracion`, `Autos Nuevos`, `Autos Seminuevos`, `AUTOS FLOTILLA`, `Servicio`, `Refacciones`, `Laminado y Pintura`, `OTROS`, `NA`.
- **Reporte**: Código del tipo de reporte. Valores observados: `1` = `BALANCE GENERAL`, `2` = `ESTADO DE RESULTADOS`, `99` = `NA`.
- **Reporte_Descripcion**: Descripción de `Reporte`.
- **Rubro_Global**: Código del rubro de más alto nivel.
- **Rubro_Global_Descripcion**: Descripción de `Rubro_Global`.
- **Rubro**: Código del rubro, un nivel más granular que `Rubro_Global`.
- **Rubro_Descripcion**: Descripción de `Rubro`.
- **Agrupador_Nivel_1**: Código de agrupación, nivel 1 (dentro de `Rubro`).
- **Agrupador_Nivel_1_Descripcion**: Descripción de `Agrupador_Nivel_1`.
- **Agrupador_Nivel_2**: Código de agrupación, nivel 2 (más granular que nivel 1).
- **Agrupador_Nivel_2_Descripcion**: Descripción de `Agrupador_Nivel_2`.
- **Agrupador_Nivel_3**: Código de agrupación, nivel 3.
- **Agrupador_Nivel_3_Descripcion**: Descripción de `Agrupador_Nivel_3`.
- **Agrupador_Nivel_4**: Código de agrupación, nivel 4 — el más granular de la jerarquía.
- **Agrupador_Nivel_4_Descripcion**: Descripción de `Agrupador_Nivel_4`.
- **Fec_iniOP**: Fecha de inicio del periodo del reporte.
- **Fec_finOP**: Fecha de fin del periodo del reporte.
- **Gastos**: Pese al nombre, no es un monto — es el nombre del concepto/cuenta contable de esa línea (ej. `AGUINALDO`, `PAPELERIA Y ARTICULOS DE ESCRITORIO`). No siempre coincide con `Agrupador_Nivel_4_Descripcion`; parece ser la cuenta específica dentro de esa agrupación.
- **Saldo_Inicial**: Saldo inicial del periodo para esta línea.
- **Cargos_Mensual**: Cargos/débitos del mes.
- **Creditos_Mensual**: Créditos/abonos del mes.
- **Saldo_Final**: Saldo final del periodo para esta línea.

### Indicadores de Calculo

- **Saldo Mensual** — Fórmula: {Cargos Mensual}-{Creditos Mensual}. Es el saldo del mes consultado. Este dato dentro del reporte de Estado de Resultados, si puede ser acumulable. 

**Filas placeholder**: cuando `Reporte = 99` (`NA`) toda la jerarquía viene `NA`/`99` — Son cuentas contables que aun no se asigaron dentro de algun agrupador. No las asignes ni asumas a que agrupador debe "mapearse". En caso se que tengan datos en los saldos o movimientos del mes, se debe indicar "Hay cuentas contables no asignadas, reportar con Soporte DCA para asignacion dentro de reportes".

---

## Mercado INEGI (`*_industria_ia.txt`)

Cubo de referencia de mercado: cruza el catálogo de vehículos de Autopolis contra la clasificación oficial de INEGI (Instituto Nacional de Estadística y Geografía) y trae, por periodo y modelo, cuántas unidades se registraron a nivel nacional — probablemente para calcular participación de mercado (unidades reales de Autopolis, de otra vista, entre `Unidades` de este cubo). La informacion se actualiza al corte de un mes anterior, por lo cual informacion de "mes actual" no se tendra datos.

### Campos

- **date_key**: Fecha del periodo.
- **Company**: Agrupador de compañía (valor observado: `Autopolis`). No debe considerarse para reportes o analizis a ese nivel.
- **Marca**: Ver [Campos Globales](#campos-globales). En la muestra viene `*NA` — en esta vista el nombre de marca "real" se visualiza en `Marca_INEGI`, no aquí.
- **Tipo_de_Vehiculo**: Ver [Campos Globales](#campos-globales). — en esta vista el modelo viene en los campos `_INEGI` de abajo, no aquí.
- **Tipo_de_Vehiculo_Original_INEGI**: Nombre del modelo tal como lo reporta INEGI, sin normalizar (ej. `Neon`).
- **Tipo_de_Vehiculo_INEGI**: Nombre del modelo normalizado/oficial de INEGI. 
- **Segmento_INEGI**: Segmento de mercado según la clasificación oficial de INEGI (ej. `Compactos`) — distinto del campo global `Segmento`, que en el resto de las vistas solo trae `AUTO`.
- **Marca_INEGI**: Marca oficial según INEGI (ej. `Chrysler`). En la muestra, el modelo `Neon` es Chrysler/Dodge — parece ser el campo de marca real de esta vista, mientras el `Marca` global viene vacío.
- **Nombre_Mes**: Número de mes del periodo (ej. `01`).
- **Nombre_Mes_Descripcion**: Abreviatura del mes (ej. `Ene`).
- **Origen**: Indica si la unidad es de fabricación nacional o importada. Valor observado: `IMPORTADO`.
- **Pais_Origen**: País de fabricación de origen (ej. `Estados Unidos`).
- **Fecha_ltima_Actualizacion**: Fecha en que se actualizó por última vez este registro. El nombre del campo probablemente debería ser "Fecha_Ultima_Actualizacion" — falta la `U`, posible problema de codificación de acentos (`Ú` perdida), el mismo tipo de corrupción que ya documenta `INSTRUCCIONES_IA.md`. Usa el nombre tal cual aparece en el archivo real al referenciarlo.
- **Fec_iniOP**: Fecha de inicio de la carga del periodo.
- **Fec_finOP**: Fecha de fin de la carga del periodo.
- **Unidades**: Cantidad de unidades del periodo. **Es el total de la industria/mercado nacional para ese modelo y periodo (dato INEGI), no ventas propias de Autopolis** — No lo uses como venta de Autopolis.
