# Comportamiento de los clientes con x = 0 en BG/NBD

## 1. Objetivo

Explicar el comportamiento de los clientes que no realizaron compras repetidas durante el período de calibración ($x=0$), analizando por qué el modelo BG/NBD les asigna una probabilidad de seguir activos igual a uno y cómo este supuesto influye en la evaluación mediante compras observadas durante el holdout.

## 2. Interpretación de x = 0

En el modelo BG/NBD, la variable $x$ representa el número de compras repetidas realizadas por un cliente durante el período de calibración.

La compra inicial no se incluye dentro de esta frecuencia.

Por lo tanto, un cliente con $x=0$ realizó su compra inicial, pero no efectuó compras adicionales durante el período de calibración.

Esto no implica necesariamente que haya abandonado, ya que el modelo distingue entre la frecuencia de compra y el estado de actividad del cliente.

## 3. Supuesto de abandono en BG/NBD

El modelo BG/NBD supone que las compras ocurren mientras el cliente permanece activo y que, después de cada compra repetida, existe una probabilidad de abandono.

La probabilidad individual de abandono se representa mediante $p$, cuya heterogeneidad entre clientes se modela con una distribución Beta:

$$
p\sim\operatorname{Beta}(a,b)
$$

Bajo el modelo BG/NBD, el abandono no ocurre después de la compra inicial, sino después de una compra repetida.

Por esta razón, si un cliente no ha realizado compras repetidas durante la calibración, el modelo considera que no ha ocurrido una oportunidad de abandono.

En consecuencia:

$$
P(\text{vivo}\mid x=0,t_x,T)=1
$$

Este resultado se deriva de los supuestos del modelo y no significa que exista certeza sobre el comportamiento real del cliente.

## 4. Relación con la fórmula de P(vivo)

Para clientes con al menos una compra repetida, la probabilidad condicional de seguir activo se calcula mediante:

$$
P(\text{vivo}\mid x,t_x,T)=
\frac{1}{
1+\frac{a}{b+x-1}
\left(\frac{\alpha+T}{\alpha+t_x}\right)^{r+x}
},\qquad x>0
$$

Sin embargo, cuando $x=0$, se utiliza el caso particular:

$$
P(\text{vivo}\mid x=0,t_x,T)=1
$$

Este caso especial es necesario porque el modelo no contempla abandono antes de la primera compra repetida.

Por lo tanto, la ausencia de compras repetidas no se interpreta automáticamente como abandono.

## 5. Resultados observados en CDNOW

Se analizaron los 2,357 clientes del conjunto de datos CDNOW utilizado para ajustar y evaluar el modelo BG/NBD.

Los resultados fueron:

| Indicador | Resultado |
|---|---:|
| Clientes totales | 2,357 |
| Clientes con x = 0 | 1,411 |
| Porcentaje con x = 0 | 59.86 % |
| Clientes con x > 0 | 946 |
| P(vivo) para x = 0 | 1.0000 |

Los clientes con $x=0$ representan aproximadamente el 59.86 % del conjunto de datos.

Esto significa que más de la mitad de los clientes no realizó compras repetidas durante el período de calibración.

## 6. Comportamiento durante el holdout

Se examinó el comportamiento de los 1,411 clientes con $x=0$ durante el período de evaluación.

| Comportamiento en holdout | Clientes | Porcentaje del grupo |
|---|---:|---:|
| Realizaron al menos una compra | 193 | 13.68 % |
| No realizaron compras | 1,218 | 86.32 % |
| Total | 1,411 | 100.00 % |

Aunque el modelo asigna una probabilidad de seguir activo igual a uno a todos estos clientes, solamente el 13.68 % realizó al menos una compra durante el holdout.

Esto se explica porque permanecer activo no garantiza que ocurra una compra durante un intervalo determinado.

La probabilidad de realizar una compra futura también depende de la tasa de compra individual y de la duración del período de evaluación.

Un cliente puede continuar activo, pero tener una frecuencia de compra suficientemente baja como para no registrar transacciones durante el holdout.

Por lo tanto:

$$
P(\text{vivo})\neq P(\text{realizar una compra futura})
$$

## 7. Efecto sobre la evaluación del modelo

En la tarea D7.T1 se utilizó directamente $P(\text{vivo})$ como puntuación para distinguir entre clientes que realizaron compras durante el holdout y aquellos que no compraron.

El AUC global obtenido fue:

$$
AUC_{\text{global}}=0.315790
$$

Se observó que los 1,411 clientes con $x=0$ reciben una probabilidad de seguir activo igual a uno, aunque 1,218 de ellos no realizaron compras durante el holdout.

Esto contribuye a que muchos clientes sin compras futuras reciban puntuaciones elevadas, afectando la capacidad de discriminación de la evaluación global.

Para estudiar este efecto se calculó nuevamente el AUC, considerando únicamente a los clientes con $x>0$.

El resultado fue:

$$
AUC_{x>0}=0.698357
$$

| Grupo evaluado | Clientes | AUC |
|---|---:|---:|
| Todos los clientes | 2,357 | 0.315790 |
| Clientes con x > 0 | 946 | 0.698357 |

La diferencia indica que los clientes sin compras repetidas influyen considerablemente en el resultado global.

Sin embargo, el AUC de 0.698357 corresponde únicamente al subconjunto con $x>0$ y no reemplaza la evaluación realizada sobre todos los clientes.

## 8. Interpretación del comportamiento

El comportamiento de los clientes con $x=0$ evidencia una característica importante del modelo BG/NBD.

La probabilidad de seguir activo describe un estado latente estimado bajo los supuestos del modelo, mientras que las compras observadas representan eventos concretos durante un período limitado.

Por ello, no es correcto interpretar la ausencia de compras durante el holdout como una confirmación de abandono.

Asimismo, una probabilidad de seguir activo igual a uno no garantiza una compra futura.

La tasa de compra individual, representada por $\lambda$, es un componente adicional del modelo y resulta relevante para estimar la ocurrencia de transacciones.

Esta distinción explica por qué $P(\text{vivo})$ no debe utilizarse automáticamente como equivalente de la probabilidad de compra durante el holdout.

## 9. Relación con MBG/NBD

Una diferencia importante entre BG/NBD y MBG/NBD es el momento en el que puede ocurrir el abandono.

En BG/NBD, el cliente puede abandonar después de una compra repetida, pero no inmediatamente después de la compra inicial.

En MBG/NBD, se permite que el abandono ocurra también después de la compra inicial.

Esta modificación permite representar situaciones en las que un cliente realiza una única compra y abandona.

Por ello, el comportamiento de los clientes con $x=0$ constituye una motivación para comparar ambos modelos en las siguientes actividades del proyecto.

No obstante, la conveniencia de utilizar MBG/NBD deberá evaluarse mediante los resultados de ajuste y predicción, y no solamente por la proporción de clientes sin compras repetidas.

## 10. Conclusiones

El modelo BG/NBD asigna una probabilidad de seguir activo igual a uno a los clientes con $x=0$, debido al supuesto de que el abandono solamente puede ocurrir después de una compra repetida.

En CDNOW se identificaron 1,411 clientes con esta característica, equivalentes aproximadamente al 59.86 % del conjunto de datos.

Durante el holdout, solamente 193 de estos clientes realizaron compras, mientras que 1,218 no registraron transacciones.

Estos resultados no contradicen directamente al modelo, porque la ausencia de compras futuras no demuestra que un cliente haya abandonado.

El análisis también permitió explicar parte del bajo AUC global obtenido al utilizar directamente $P(\text{vivo})$ como puntuación de clasificación de compras futuras.

Finalmente, el comportamiento de los clientes con $x=0$ permite comprender una limitación de los supuestos del BG/NBD y proporciona una motivación para estudiar el modelo MBG/NBD.

## 11. Archivos relacionados

- `src/clientes_activos.py`: cálculo de P(vivo) y análisis adicional.
- `documentos/clientes_activos.md`: evaluación mediante matriz de confusión, ROC y AUC.
- `data/procesado/cdnow_rfm.csv`: datos RFM de los clientes.
- `resultados/tablas/clientes_activos.csv`: probabilidades estimadas por cliente.
- `resultados/graficas/matriz_confusion_clientes.png`: matriz de confusión.
- `resultados/graficas/roc_clientes.png`: curva ROC.
