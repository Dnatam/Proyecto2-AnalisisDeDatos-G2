# Limpieza y preparación del conjunto de datos Online Retail

## 1. Objetivo

Realizar la limpieza y preparación del conjunto de datos Online Retail para su posterior utilización en el modelo BG/NBD, eliminando registros que no representan compras válidas y consolidando las líneas de productos en transacciones individuales.

El procedimiento busca obtener información consistente sobre los clientes, sus compras y las fechas en las que ocurrieron, sin modificar el archivo original.

## 2. Descripción del conjunto de datos

Se utilizó el archivo `data/original/Online Retail.xlsx`, que contiene información transaccional entre el 1 de diciembre de 2010 y el 9 de diciembre de 2011.

El conjunto original contiene 541,909 registros y 8 columnas:

| Columna | Descripción |
|---|---|
| InvoiceNo | Identificador de la factura |
| StockCode | Código del producto |
| Description | Descripción del producto |
| Quantity | Cantidad adquirida |
| InvoiceDate | Fecha y hora de la transacción |
| UnitPrice | Precio unitario del producto |
| CustomerID | Identificador del cliente |
| Country | País asociado a la compra |

Cada fila representa una línea de producto de una factura. Por lo tanto, varias filas pueden corresponder a una misma transacción.

Para utilizar los datos con BG/NBD es necesario identificar los eventos de compra por cliente, evitando contar cada producto como una compra independiente.

## 3. Diagnóstico inicial

Antes de realizar la limpieza se identificaron las siguientes características:

| Característica | Cantidad |
|---|---:|
| Registros originales | 541,909 |
| Clientes identificados | 4,372 |
| Facturas distintas | 25,900 |
| Registros sin CustomerID | 135,080 |
| Registros sin Description | 1,454 |
| Cantidades no positivas | 10,624 |
| Precios no positivos | 2,517 |
| Filas de facturas canceladas | 9,288 |
| Duplicados exactos | 5,268 |

Estas condiciones pueden superponerse, por lo que sus cantidades iniciales no deben sumarse para determinar el número de registros eliminados.

## 4. Procedimiento de limpieza

La limpieza se implementó en `src/limpiar_online_retail.py`, utilizando Python y la biblioteca pandas.

Se aplicaron las siguientes reglas de manera secuencial:

1. Eliminar registros sin identificador de cliente (`CustomerID`).
2. Excluir facturas cuyo identificador comienza con `C`, utilizadas para representar cancelaciones.
3. Excluir registros con cantidades menores o iguales a cero.
4. Excluir registros con precios unitarios menores o iguales a cero.
5. Excluir registros sin fecha o identificador de factura.
6. Eliminar filas duplicadas exactas.
7. Normalizar los identificadores de clientes y facturas.
8. Convertir las fechas a un formato de fecha y hora.
9. Ordenar los registros por cliente, fecha y factura.

No se eliminó información únicamente por la ausencia de una descripción del producto, ya que esta variable no es indispensable para identificar las compras.

La eliminación de duplicados exactos se adoptó como criterio de limpieza. No obstante, debe considerarse que algunos registros idénticos podrían corresponder a líneas legítimas de una factura.

## 5. Resultados de la limpieza

El programa generó el siguiente resumen:

| Etapa | Registros eliminados | Registros restantes |
|---|---:|---:|
| Datos originales | — | 541,909 |
| Sin CustomerID | 135,080 | 406,829 |
| Facturas canceladas | 8,905 | 397,924 |
| Cantidad no positiva | 0 | 397,924 |
| Precio no positivo | 40 | 397,884 |
| Sin fecha o factura | 0 | 397,884 |
| Duplicados exactos | 5,192 | 392,692 |

En total se eliminaron 149,217 registros, equivalentes aproximadamente al 27.54 % del conjunto original.

Se conservaron 392,692 líneas de venta, correspondientes al 72.46 % de los registros iniciales.

La eliminación de cero registros durante la etapa de cantidades no positivas se explica porque los registros que cumplían esa condición ya habían sido excluidos mediante filtros anteriores.

De manera similar, las cantidades de facturas canceladas y duplicados eliminados durante el procedimiento son menores que las identificadas inicialmente, debido a la aplicación secuencial de los filtros.

## 6. Construcción de la tabla de transacciones

Después de limpiar las líneas de venta, se construyó una segunda tabla que representa las transacciones individuales.

Se agruparon los registros mediante `CustomerID` e `InvoiceNo`, de manera que cada combinación de cliente y factura representa una compra.

El importe de cada línea se calculó como:

$$
\text{Importe}=\text{Quantity}\times\text{UnitPrice}
$$

Posteriormente, el importe total de cada factura se obtuvo sumando los importes de sus productos:

$$
\text{Total de factura}=\sum_{i=1}^{m}\text{Importe}_i
$$

Para la fecha de cada transacción se utilizó la fecha y hora más temprana registrada entre las líneas de la factura.

La tabla resultante contiene las siguientes columnas:

| Columna | Descripción |
|---|---|
| CustomerID | Identificador del cliente |
| InvoiceNo | Identificador de la factura |
| InvoiceDate | Fecha y hora de la compra |
| Total | Importe total de la factura |

Esta estructura permite identificar las compras realizadas por cada cliente y será utilizada posteriormente para construir las variables requeridas por BG/NBD.

## 7. Resultados finales

Después de consolidar las líneas de productos se obtuvieron:

| Característica | Resultado |
|---|---:|
| Líneas de venta limpias | 392,692 |
| Clientes identificados | 4,338 |
| Transacciones individuales | 18,532 |
| Facturas distintas | 18,532 |
| Importe total conservado | 8,887,208.89 |
| Primera fecha | 2010-12-01 08:26:00 |
| Última fecha | 2011-12-09 12:50:00 |

El conjunto final contiene 4,338 clientes y 18,532 eventos de compra.

Es importante distinguir las 392,692 líneas de productos de las 18,532 transacciones, ya que BG/NBD modela eventos de compra y no cantidades de productos adquiridos.

## 8. Validación de los resultados

Se revisaron los archivos CSV generados para comprobar la consistencia del procedimiento.

Las verificaciones confirmaron que:

- No existen identificadores de cliente vacíos.
- No existen facturas canceladas en las líneas limpias.
- No existen cantidades o precios unitarios no positivos.
- No existen filas duplicadas exactas en el archivo limpio.
- No existen combinaciones duplicadas de cliente y factura en la tabla de transacciones.
- No existen importes totales no positivos.
- Ambas tablas contienen los mismos 4,338 clientes.
- El importe total calculado a partir de las líneas coincide con la suma de los importes de las transacciones.

También se identificaron 30 facturas cuyas líneas contienen más de una fecha u hora. En estos casos, el procedimiento seleccionó la fecha más temprana.

Las verificaciones indican que los archivos generados son consistentes con los criterios de limpieza implementados.

## 9. Relación con el modelo BG/NBD

La limpieza de Online Retail constituye una etapa previa al ajuste del modelo BG/NBD.

A partir de la tabla de transacciones será posible construir las variables:

- $x$: cantidad de compras repetidas del cliente durante la calibración.
- $t_x$: tiempo transcurrido desde la primera compra hasta la última compra repetida.
- $T$: tiempo transcurrido desde la primera compra hasta el final del período de calibración.

Para ello será necesario definir el período de calibración, el período de evaluación y la unidad de tiempo.

Estas operaciones corresponden a la siguiente etapa del proyecto y no forman parte del procedimiento de limpieza realizado.

## 10. Archivos generados

### Programa

`src/limpiar_online_retail.py`

Implementa la limpieza y construcción de transacciones.

### Archivo de líneas limpias

`data/procesado/online_retail_limpio.csv`

Contiene los registros de productos que cumplen las condiciones establecidas.

### Archivo de transacciones

`data/procesado/online_retail_transacciones.csv`

Contiene una fila por combinación de cliente y factura, con fecha e importe total.

### Resumen del procedimiento

`data/procesado/resumen_limpieza_online_retail.csv`

Registra los filtros aplicados y la cantidad de registros eliminados en cada etapa.

## 11. Conclusiones

La limpieza de Online Retail permitió transformar un conjunto original de 541,909 líneas de productos en 392,692 líneas de venta válidas según los criterios establecidos.

Posteriormente, estas líneas se consolidaron en 18,532 transacciones correspondientes a 4,338 clientes.

El procedimiento permitió excluir registros sin identificación de cliente, cancelaciones, cantidades y precios no positivos, así como duplicados exactos.

Las validaciones realizadas confirmaron la consistencia de los identificadores, las transacciones y los importes calculados.

Finalmente, se obtuvo una estructura transaccional que podrá utilizarse para construir las variables de frecuencia, recencia y tiempo de observación requeridas por BG/NBD, facilitando su aplicación al conjunto de datos Online Retail.
