# Interpretación de la recuperación de parámetros BG/NBD

## 1. Objetivo

Analizar cuáles parámetros del modelo BG/NBD se recuperan con mayor precisión mediante simulación y explicar las diferencias observadas entre sus estimaciones.

Este análisis corresponde al inciso 1.3 y utiliza los resultados obtenidos en la comparación entre parámetros verdaderos y estimados.

## 2. Datos utilizados

Se utilizaron los resultados de 30 cohortes simuladas, cada una con 2,357 clientes.

Los parámetros verdaderos utilizados en la simulación fueron:

- $r = 0.25$
- $\alpha = 4.00$
- $a = 0.80$
- $b = 2.50$

El tiempo de observación se generó mediante $T \sim U(27,39)$.

En cada simulación se estimaron los cuatro parámetros mediante máxima verosimilitud.

Los resultados se encuentran en `resultados/tablas/sim_comparacion.csv` y fueron calculados mediante `src/comparar_simulacion.py`.

## 3. Comparación de los parámetros

| Parámetro | Verdadero | Media estimada | Sesgo relativo | CV | RMSE |
|---|---:|---:|---:|---:|---:|
| $r$ | 0.25 | 0.2533 | +1.33 % | 4.69 % | 0.0122 |
| $\alpha$ | 4.00 | 4.0809 | +2.02 % | 7.36 % | 0.3062 |
| $a$ | 0.80 | 0.7980 | -0.25 % | 20.60 % | 0.1617 |
| $b$ | 2.50 | 2.5727 | +2.91 % | 25.23 % | 0.6423 |

Los cuatro parámetros presentan medias estimadas cercanas a sus valores verdaderos, con sesgos relativos inferiores al 3 % en valor absoluto.

Sin embargo, existen diferencias importantes en la variabilidad de las estimaciones.

## 4. Parámetros que se recuperan mejor

Los parámetros $r$ y $\alpha$ presentan los coeficientes de variación más bajos, de 4.69 % y 7.36 %, respectivamente.

Esto indica que sus estimaciones son relativamente más estables entre las 30 simulaciones.

El parámetro $r$ presenta la menor variabilidad relativa y un sesgo de solamente +1.33 %, por lo que es el parámetro que muestra mayor precisión relativa en este experimento.

Por su parte, $\alpha$ también presenta una recuperación estable, aunque su variabilidad es ligeramente superior.

En cambio, los parámetros $a$ y $b$ presentan coeficientes de variación de 20.60 % y 25.23 %, respectivamente.

Esto significa que sus estimaciones fluctúan considerablemente más entre las cohortes simuladas.

El parámetro $a$ presenta el menor sesgo relativo de los cuatro parámetros (-0.25 %), pero no es el más preciso, debido a su mayor dispersión.

El parámetro $b$ presenta la mayor variabilidad relativa y el mayor sesgo relativo, por lo que su recuperación es la menos estable de los cuatro parámetros analizados.

## 5. ¿Por qué existen estas diferencias?

En BG/NBD, los parámetros $r$ y $\alpha$ describen la distribución Gamma de las tasas individuales de compra.

Por otro lado, $a$ y $b$ describen la distribución Beta de las probabilidades individuales de abandono.

Una posible explicación de las diferencias observadas es que el comportamiento de compra proporciona información sobre las tasas de compra, mientras que el abandono no se observa directamente.

En un entorno no contractual, la ausencia de nuevas compras puede deberse a que el cliente abandonó o a que permanece activo, pero todavía no ha realizado otra transacción.

Esta incertidumbre puede dificultar la identificación de los parámetros relacionados con el abandono y contribuir a una mayor variabilidad de sus estimaciones.

Por lo tanto, es razonable que los parámetros $a$ y $b$ presenten una recuperación menos estable que $r$ y $\alpha$ en las condiciones de esta simulación.

No obstante, esta explicación es una interpretación del comportamiento del modelo. Los resultados disponibles muestran la diferencia de variabilidad, pero no permiten atribuirla de manera exclusiva a una sola causa.

## 6. Diferencia entre sesgo y precisión

El sesgo mide qué tan lejos se encuentra la media de las estimaciones respecto al valor verdadero.

La precisión describe qué tanto varían las estimaciones entre simulaciones.

Por esta razón, un parámetro puede presentar un sesgo pequeño y, al mismo tiempo, una variabilidad elevada.

Esto ocurre con el parámetro $a$, cuya media estimada es muy cercana al valor verdadero, pero cuyo coeficiente de variación alcanza el 20.60 %.

En consecuencia, para evaluar la recuperación de parámetros no basta con comparar las medias estimadas y los valores verdaderos. También es necesario considerar medidas de dispersión como la desviación estándar y el coeficiente de variación.

## 7. Interpretación del RMSE

El RMSE combina el efecto del sesgo y la variabilidad de las estimaciones.

Los resultados fueron:

- $r$: 0.0122
- $\alpha$: 0.3062
- $a$: 0.1617
- $b$: 0.6423

Estos valores están expresados en las unidades de cada parámetro.

Por lo tanto, no deben compararse directamente para establecer cuál parámetro se recupera mejor, ya que los parámetros tienen escalas diferentes.

Para comparar la estabilidad relativa entre parámetros resulta más apropiado utilizar el coeficiente de variación.

## 8. Conclusión

Los resultados de las 30 simulaciones muestran que los cuatro parámetros del modelo BG/NBD se recuperan con sesgos relativos pequeños, inferiores al 3 % en valor absoluto.

Sin embargo, los parámetros $r$ y $\alpha$ presentan mayor estabilidad y precisión relativa, con coeficientes de variación de 4.69 % y 7.36 %.

Los parámetros $a$ y $b$ presentan mayor dispersión, especialmente $b$, cuyo coeficiente de variación alcanza el 25.23 %.

Estas diferencias son coherentes con la mayor dificultad de inferir el abandono en un modelo no contractual, donde no se observa directamente si un cliente ha dejado de comprar definitivamente.

En conclusión, el procedimiento de estimación recupera adecuadamente los valores medios de los cuatro parámetros, pero la precisión de la recuperación no es igual para todos ellos.