# Interpretación de tasas de compra y probabilidades de abandono — BG/NBD

## 1. Objetivo

Interpretar las tasas de compra y las probabilidades de abandono de los clientes mediante las distribuciones Gamma y Beta del modelo BG/NBD, utilizando los parámetros estimados a partir del conjunto de datos CDNOW.

## 2. Parámetros estimados

Se utilizaron los parámetros obtenidos mediante el ajuste por máxima verosimilitud del modelo BG/NBD sobre los datos de calibración de CDNOW.

| Parámetro | Valor estimado |
|---|---:|
| r | 0.2426 |
| α | 4.4136 |
| a | 0.7929 |
| b | 2.4259 |

Los valores se obtuvieron del archivo `resultados/tablas/params_cdnow.csv`, generado por el script `src/ajuste_cdnow.py`.

## 3. Distribución de las tasas de compra

En el modelo BG/NBD, la tasa de compra de cada cliente, representada por $\lambda$, sigue una distribución Gamma con parámetros $r$ y $\alpha$, donde $\alpha$ corresponde al parámetro de tasa.

$$
\lambda \sim \operatorname{Gamma}(r,\alpha)
$$

La media de esta distribución se calcula mediante:

$$
E[\lambda] = \frac{r}{\alpha}
$$

Sustituyendo los parámetros estimados:

$$
E[\lambda] = \frac{0.2426}{4.4136} \approx 0.054965
$$

La varianza y la desviación estándar se calculan mediante:

$$
\operatorname{Var}(\lambda) = \frac{r}{\alpha^2} \approx 0.012454
$$

$$
\sigma_{\lambda} = \sqrt{\frac{r}{\alpha^2}} \approx 0.111596
$$

### Interpretación

La tasa media estimada es de aproximadamente 0.055 compras repetidas por semana mientras un cliente permanece activo. Sin embargo, esta tasa no es igual para todos los clientes, ya que el modelo permite representar diferencias individuales en sus hábitos de compra.

La desviación estándar de 0.111596, superior a la media, indica una dispersión considerable en las tasas individuales. Esto sugiere que existen clientes con tasas de compra muy bajas y otros con tasas relativamente más altas.

Estos valores describen la distribución poblacional estimada de las tasas de compra, no la cantidad efectiva de compras realizadas semanalmente por todos los clientes.

## 4. Distribución de las probabilidades de abandono

En BG/NBD, la probabilidad individual de abandono, representada por $p$, sigue una distribución Beta con parámetros $a$ y $b$.

$$
p \sim \operatorname{Beta}(a,b)
$$

La media se calcula mediante:

$$
E[p] = \frac{a}{a+b}
$$

Sustituyendo los parámetros estimados:

$$
E[p] = \frac{0.7929}{0.7929+2.4259} \approx 0.246338
$$

La varianza y la desviación estándar se calculan mediante:

$$
\operatorname{Var}(p) = \frac{ab}{(a+b)^2(a+b+1)} \approx 0.044007
$$

$$
\sigma_p = \sqrt{\frac{ab}{(a+b)^2(a+b+1)}} \approx 0.209778
$$

### Interpretación

La probabilidad media estimada de abandono es de aproximadamente 24.63 %. Esto significa que, dentro de los supuestos del modelo BG/NBD, la probabilidad promedio de que un cliente abandone después de una compra es de 0.246338.

Esta probabilidad no representa una tasa de abandono semanal. El modelo considera que un cliente activo puede abandonar después de realizar una compra y que su probabilidad individual de abandono permanece constante a lo largo del tiempo.

La desviación estándar de 0.209778 indica que existen diferencias importantes entre las probabilidades individuales de abandono. Por lo tanto, no todos los clientes presentan el mismo riesgo de dejar de comprar.

## 5. Implementación y verificación

Para realizar los cálculos se implementó el archivo `src/interpretacion_parametros.py`, que carga los parámetros estimados desde `resultados/tablas/params_cdnow.csv` y calcula las medias, varianzas y desviaciones estándar de ambas distribuciones.

Los resultados obtenidos durante la ejecución fueron:

| Estadística | Resultado |
|---|---:|
| Media de λ | 0.054965 |
| Varianza de λ | 0.012454 |
| Desviación estándar de λ | 0.111596 |
| Media de p | 0.246338 |
| Varianza de p | 0.044007 |
| Desviación estándar de p | 0.209778 |

La ejecución finalizó correctamente y los resultados coincidieron con los valores calculados mediante las fórmulas teóricas.

## 6. Conclusiones

Los parámetros estimados del modelo BG/NBD permiten caracterizar dos aspectos del comportamiento de los clientes: la frecuencia con la que realizan compras mientras permanecen activos y su probabilidad de abandonar después de una compra.

La distribución Gamma refleja una heterogeneidad considerable en las tasas de compra, mientras que la distribución Beta muestra diferencias importantes en las probabilidades individuales de abandono.

Estos resultados permiten comprender por qué el modelo BG/NBD no supone que todos los clientes compran con la misma frecuencia ni que tienen el mismo riesgo de abandono. Ambas distribuciones proporcionan una representación probabilística de las diferencias de comportamiento dentro de la población analizada.

## 7. Archivos relacionados

- `src/interpretacion_parametros.py`: cálculo de estadísticas e interpretación de parámetros.
- `src/ajuste_cdnow.py`: estimación de los parámetros mediante máxima verosimilitud.
- `src/bgnbd.py`: implementación de las funciones principales del modelo BG/NBD.
- `resultados/tablas/params_cdnow.csv`: parámetros estimados utilizados en el análisis.
