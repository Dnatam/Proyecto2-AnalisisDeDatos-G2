# Ajuste del modelo BG/NBD con Online Retail

## 1. Objetivo

Aplicar el modelo BG/NBD (Beta-Geometric/Negative Binomial Distribution) al conjunto de datos Online Retail para estimar los parámetros que describen el comportamiento de compra y abandono de los clientes.

Se reutilizó la implementación de máxima verosimilitud desarrollada para CDNOW, con el propósito de aplicar el mismo procedimiento de estimación a un segundo conjunto de datos transaccionales.

## 2. Preparación de los datos

Se utilizó el archivo `online_retail_transacciones.csv`, obtenido después de la limpieza del conjunto de datos Online Retail.

El archivo contiene 18,532 transacciones correspondientes a 4,338 clientes. Cada registro representa una factura individual, con su identificador de cliente, fecha e importe total.

Para preparar los datos se implementó `src/preparacion_online_retail.py`, que construye las variables requeridas por BG/NBD.

### 2.1. Períodos de análisis

Se definieron los siguientes períodos:

| Período | Fechas |
|---|---|
| Calibración | 01/12/2010 al 31/08/2011 |
| Holdout | 01/09/2011 al 09/12/2011 |

La unidad de tiempo utilizada fue la semana, calculada a partir de las fechas y horas de las transacciones.

Se obtuvieron 11,413 transacciones en calibración y 7,119 transacciones en holdout.

### 2.2. Construcción de variables RFM

Para cada cliente observado durante calibración se calcularon:

- **Frecuencia ($x$):** número de compras repetidas después de la primera compra.
- **Recencia ($t_x$):** tiempo transcurrido entre la primera y la última compra durante calibración.
- **Tiempo de observación ($T$):** tiempo transcurrido entre la primera compra y el final de calibración.
- **Compras en holdout ($x^*$):** número de compras realizadas durante holdout por clientes presentes en calibración.

Las variables temporales se expresaron en semanas.

La frecuencia se calculó mediante:

$$
x=n_{\text{cal}}-1
$$

La recencia y el tiempo de observación se calcularon como:

$$
t_x=\frac{\text{Última compra}-\text{Primera compra}}{7\text{ días}}
$$

$$
T=\frac{\text{Fin de calibración}-\text{Primera compra}}{7\text{ días}}
$$

Los resultados se guardaron en `data/procesado/online_retail_rfm.csv`.

### 2.3. Resultados de preparación

| Indicador | Resultado |
|---|---:|
| Clientes en calibración | 3,317 |
| Compras repetidas en calibración | 8,096 |
| Compras en holdout de clientes calibrados | 5,434 |
| Clientes sin compras repetidas | 1,376 |
| Clientes con compras repetidas simultáneas | 2 |

Los clientes que aparecen por primera vez durante holdout no se incorporaron al ajuste, ya que no tienen historial de calibración.

Durante la validación se identificaron dos clientes con $x>0$ y $t_x=0$, debido a que tenían facturas diferentes registradas exactamente a la misma hora.

Estos casos se conservaron sin modificar las fechas originales. La validación de RFM se adaptó para reconocer esta situación sin tratarla automáticamente como un error.

## 3. Modelo BG/NBD

El modelo BG/NBD permite describir el comportamiento de compras repetidas de clientes en un entorno no contractual, donde no se observa directamente cuándo un cliente abandona.

El modelo considera dos componentes principales:

1. **Proceso de compras:** mientras un cliente permanece activo, sus compras siguen un proceso de Poisson con tasa individual $\lambda$.
2. **Proceso de abandono:** después de una compra, el cliente puede abandonar con una probabilidad individual $p$.

Se supone que las tasas de compra siguen una distribución Gamma y las probabilidades de abandono siguen una distribución Beta:

$$
\lambda \sim \operatorname{Gamma}(r,\alpha)
$$

$$
p \sim \operatorname{Beta}(a,b)
$$

Por lo tanto, el modelo estima cuatro parámetros:

| Parámetro | Interpretación |
|---|---|
| $r$ | Parámetro de forma de la distribución Gamma |
| $\alpha$ | Parámetro de tasa de la distribución Gamma |
| $a$ | Primer parámetro de la distribución Beta |
| $b$ | Segundo parámetro de la distribución Beta |

Estos parámetros permiten representar diferencias entre clientes en sus tasas de compra y probabilidades de abandono.

## 4. Método de estimación

Los parámetros se estimaron mediante máxima verosimilitud, reutilizando las funciones implementadas en `src/bgnbd.py` y `src/ajuste_cdnow.py`.

La función `loglik()` calcula la log-verosimilitud total de los clientes utilizando sus variables $x$, $t_x$ y $T$.

La estimación busca encontrar los parámetros que maximizan:

$$
\hat{\theta}
=
\underset{\theta}{\arg\max}
\ \log L(\theta)
$$

donde:

$$
\theta=(r,\alpha,a,b)
$$

Para asegurar que los parámetros sean positivos, la optimización se realiza sobre sus logaritmos:

$$
\eta=(\log r,\log\alpha,\log a,\log b)
$$

Se utilizó el algoritmo L-BFGS-B, disponible en `scipy.optimize.minimize`.

Se realizaron cinco optimizaciones con distintos puntos iniciales para evaluar la estabilidad de la solución.

## 5. Resultados del ajuste

### 5.1. Resultados por punto inicial

| Inicio | $r$ | $\alpha$ | $a$ | $b$ | Log-verosimilitud |
|---|---:|---:|---:|---:|---:|
| (1, 1, 1, 1) | 0.6204 | 6.6796 | 0.0499 | 1.6291 | -23197.9380 |
| (0.5, 5, 1, 3) | 0.6204 | 6.6796 | 0.0499 | 1.6287 | -23197.9380 |
| (0.1, 1, 0.5, 0.5) | 0.6204 | 6.6809 | 0.0499 | 1.6315 | -23197.9381 |
| (2, 10, 2, 5) | 0.6204 | 6.6796 | 0.0499 | 1.6286 | -23197.9380 |
| (0.3, 20, 0.2, 1) | 0.6204 | 6.6795 | 0.0499 | 1.6290 | -23197.9380 |

Los cinco puntos iniciales convergieron satisfactoriamente y alcanzaron valores prácticamente iguales de log-verosimilitud.

Ninguno de los parámetros estimados quedó pegado a las cotas de optimización.

Esto proporciona evidencia de estabilidad numérica del procedimiento, aunque no constituye una demostración de optimalidad global.

### 5.2. Parámetros finales

| Parámetro | Valor estimado |
|---|---:|
| $r$ | 0.620363 |
| $\alpha$ | 6.679619 |
| $a$ | 0.049881 |
| $b$ | 1.629120 |
| Log-verosimilitud | -23197.9380 |

Los resultados se guardaron en:

- `resultados/tablas/params_online_retail.csv`
- `resultados/tablas/ajuste_online_retail_arranques.csv`

## 6. Interpretación de los parámetros

### 6.1. Tasa media de compra

Bajo la parametrización Gamma utilizada, la tasa media de compra es:

$$
E[\lambda]=\frac{r}{\alpha}
$$

Sustituyendo los parámetros estimados:

$$
E[\lambda]
=
\frac{0.620363}{6.679619}
\approx 0.0929
$$

Esto representa una tasa media de aproximadamente **0.0929 compras por semana mientras los clientes permanecen activos**.

El resultado corresponde al promedio de la distribución de tasas individuales, no a la cantidad de compras observadas de todos los clientes por semana.

### 6.2. Probabilidad media de abandono

La probabilidad media de abandono después de una compra se calcula mediante:

$$
E[p]=\frac{a}{a+b}
$$

Sustituyendo:

$$
E[p]
=
\frac{0.049881}{0.049881+1.629120}
\approx 0.0297
$$

Por lo tanto, el modelo estima una **probabilidad media de abandono cercana al 2.97 % por ocasión de compra**.

Esta probabilidad no representa una tasa de abandono semanal, sino una probabilidad asociada a las ocasiones de compra.

### 6.3. Consideración sobre el parámetro $a$

El parámetro $a$ estimado es menor que uno:

$$
a=0.049881<1
$$

Este valor es válido para la distribución Beta y no representa un error del procedimiento de máxima verosimilitud.

Sin embargo, algunas expresiones de compras esperadas contienen el término $(a-1)$ en el denominador y requieren atención especial respecto de sus condiciones de validez y estabilidad numérica.

Por esta razón, el ajuste de parámetros se considera completado, pero cualquier aplicación posterior de las funciones de pronóstico deberá verificarse específicamente con los parámetros de Online Retail.

## 7. Comparación descriptiva con CDNOW

Como referencia, se compararon los parámetros estimados para ambos conjuntos de datos.

| Parámetro | CDNOW | Online Retail |
|---|---:|---:|
| $r$ | 0.2426 | 0.620363 |
| $\alpha$ | 4.4136 | 6.679619 |
| $a$ | 0.7929 | 0.049881 |
| $b$ | 2.4259 | 1.629120 |

La tasa media de compra estimada para CDNOW fue aproximadamente 0.0550 compras semanales, mientras que para Online Retail fue aproximadamente 0.0929.

La probabilidad media de abandono estimada fue aproximadamente 24.63 % para CDNOW y 2.97 % para Online Retail.

Estas diferencias describen el comportamiento estimado bajo cada conjunto de datos. No deben interpretarse como una comparación causal ni como evidencia de que todos los clientes de Online Retail compran con mayor frecuencia.

Los conjuntos contienen poblaciones distintas y períodos de observación diferentes.

Tampoco es apropiado comparar directamente las log-verosimilitudes totales para determinar qué conjunto tiene un mejor ajuste, debido a las diferencias en los datos y el tamaño de las muestras.

## 8. Validación del procedimiento

Se verificaron los siguientes aspectos:

- Las variables $x$, $t_x$ y $T$ contienen valores finitos.
- Las frecuencias y recencias son no negativas.
- Los tiempos de observación son positivos.
- Se cumple $t_x \leq T$ para todos los clientes.
- Los cinco puntos iniciales convergieron.
- Los cinco arranques alcanzaron log-verosimilitudes prácticamente iguales.
- Ningún parámetro quedó pegado a las cotas.
- Las log-verosimilitudes individuales fueron finitas.
- La suma de las log-verosimilitudes individuales coincidió con la log-verosimilitud total estimada.

Estas comprobaciones respaldan la consistencia numérica del ajuste.

No obstante, la convergencia del optimizador no equivale a una evaluación predictiva. Para valorar la capacidad de pronóstico del modelo será necesario contrastar sus predicciones con los datos de holdout.

## 9. Archivos utilizados y generados

### Archivos de entrada

- `data/procesado/online_retail_transacciones.csv`
- `data/procesado/online_retail_rfm.csv`

### Programas

- `src/preparacion_online_retail.py`: construye las variables RFM.
- `src/ajuste_online_retail.py`: estima los parámetros del modelo.
- `src/ajuste_cdnow.py`: proporciona el procedimiento de optimización reutilizado.
- `src/bgnbd.py`: proporciona la función de log-verosimilitud BG/NBD.

### Archivos de salida

- `data/procesado/online_retail_trans.csv`
- `data/procesado/online_retail_rfm.csv`
- `resultados/tablas/params_online_retail.csv`
- `resultados/tablas/ajuste_online_retail_arranques.csv`

## 10. Conclusiones

Se ajustó satisfactoriamente el modelo BG/NBD al conjunto de datos Online Retail, utilizando 3,317 clientes observados durante el período de calibración.

La estimación mediante máxima verosimilitud produjo los parámetros $r=0.620363$, $\alpha=6.679619$, $a=0.049881$ y $b=1.629120$, con una log-verosimilitud de aproximadamente -23197.9380.

Los cinco puntos iniciales convergieron hacia soluciones prácticamente equivalentes y ninguno de los parámetros quedó en las cotas de optimización.

A partir de los parámetros estimados se obtuvo una tasa media de compra de aproximadamente 0.0929 compras semanales mientras los clientes permanecen activos y una probabilidad media de abandono de 2.97 % por ocasión de compra.

El ajuste demuestra que la implementación de BG/NBD desarrollada para CDNOW puede reutilizarse con otro conjunto transaccional, conservando el procedimiento de estimación.

Como trabajo posterior queda evaluar la capacidad predictiva del modelo sobre el período de holdout y verificar las funciones de pronóstico para los parámetros obtenidos.
