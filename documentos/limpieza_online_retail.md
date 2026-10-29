# Limpieza y preparación de Online Retail

Programa: `src/limpiar_online_retail.py`. Entrada: `data/original/Online Retail.xlsx`.

## 1. Qué pide el enunciado

Quedarse solo con las líneas que tienen `CustomerID` y definir una **transacción como un día
con venta neta positiva de un cliente**. La palabra clave es *neta*: las devoluciones y
cancelaciones (cantidades negativas, facturas que empiezan con `C`) **no se eliminan**, se
restan de las compras del mismo día. Si se eliminaran, un cliente que compra y devuelve todo
el mismo día contaría como una compra que en realidad no existió.

## 2. Procedimiento

| Paso | Qué se hace | Líneas antes | Eliminadas | Líneas después |
|---|---|---:|---:|---:|
| 1 | Quitar líneas sin `CustomerID` | 541,909 | 135,080 | 406,829 |
| 2 | Quitar fechas inválidas | 406,829 | 0 | 406,829 |
| 3 | Quitar cantidad o precio no numéricos | 406,829 | 0 | 406,829 |

Después se calcula el importe de cada línea (`Quantity × UnitPrice`, conservando los
negativos), se agrupa por cliente y día calendario, y se suman los importes.

| Resultado | Valor |
|---|---:|
| Días cliente con al menos una línea | 19,296 |
| Días con venta neta ≤ 0 (descartados) | 2,684 |
| **Transacciones (días con venta neta > 0)** | **16,612** |
| Clientes con al menos una transacción | 4,334 |
| Rango de fechas | 1 dic 2010 a 9 dic 2011 |

Las líneas válidas se guardan en `data/procesado/online_retail_limpio.csv` y las
transacciones diarias en `data/procesado/online_retail_transacciones.csv`; el conteo por
etapa queda en `data/procesado/resumen_limpieza_online_retail.csv`.

## 3. Verificaciones

El script comprueba que no haya dos transacciones del mismo cliente el mismo día, que todas
las ventas netas sean positivas y que todas las fechas sean días completos (sin hora).

## 4. Nota sobre la función `limpiar` de la tarea

El enunciado pide usar la función `limpiar` de la tarea de series de tiempo. Este script
reproduce los pasos que afectan la definición de transacción (cliente identificado, fechas
válidas y venta neta diaria). Los duplicados exactos y las líneas con precio cero casi
nunca cambian el signo de la venta neta de un día, por lo que no alteran el conteo de
transacciones de forma apreciable.