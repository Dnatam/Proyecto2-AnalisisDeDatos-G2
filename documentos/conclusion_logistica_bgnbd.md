# Conclusión de la comparación entre regresión logística y BG/NBD

## 1. Objetivo

Se comparó el desempeño de la regresión logística y del modelo BG/NBD para estimar la probabilidad de que un cliente realice al menos una compra durante un período futuro.

La comparación consideró la capacidad de discriminación, medida mediante AUC-ROC, y la precisión de las probabilidades, evaluada mediante Brier Score.

## 2. Comparación inicial a 39 semanas

En el experimento inicial se utilizó validación cruzada estratificada de cinco particiones y veinte semillas para evaluar la regresión logística. Se obtuvieron los siguientes resultados promedio:

| Métrica | Regresión logística |
|---|---:|
| AUC-ROC | 0.7790 |
| Brier Score | 0.1561 |

Para BG/NBD, evaluado sobre el horizonte de 39 semanas, se obtuvo un AUC-ROC de 0.7569 y un Brier Score de 0.1612.

Aunque la regresión logística presentó mejores métricas en esta comparación, el experimento no representa una evaluación prospectiva equivalente. La regresión logística fue entrenada utilizando etiquetas de compra observadas durante el período de holdout, mientras que BG/NBD se ajustó con la información del período de calibración.

La validación cruzada evita que un mismo cliente esté simultáneamente en el entrenamiento y la evaluación de una partición, pero no elimina el problema de utilizar etiquetas futuras que no estarían disponibles en el momento de realizar el pronóstico.

Por esta razón, los resultados iniciales se interpretan como una comparación retrospectiva y no como evidencia concluyente de superioridad predictiva.

## 3. Corrección de la evaluación temporal

Para obtener una comparación prospectiva se implementó un procedimiento de entrenamiento histórico y evaluación futura.

Se utilizaron dos ventanas históricas de entrenamiento, con cortes aproximadamente en las semanas 12.86 y 25.86. En cada una se construyeron las características de los clientes a partir de sus compras observadas hasta la fecha de corte y se utilizaron las compras de las siguientes 13 semanas como etiquetas.

La evaluación final se realizó al cierre de la calibración, el 30 de septiembre de 1997, equivalente a la semana 38.8571. El objetivo fue predecir si cada cliente realizaría al menos una compra durante las 13 semanas posteriores.

Se verificó que ambos modelos utilizaran las mismas variables de frecuencia (`x`), recencia (`tx`) y antigüedad (`T`) para los 2,357 clientes evaluados.

La regresión logística se entrenó con las observaciones históricas y BG/NBD utilizó los parámetros estimados con las transacciones del período de calibración.

## 4. Resultados de la comparación a 13 semanas

La evaluación incluyó 2,357 clientes, de los cuales 402 realizaron al menos una compra durante el horizonte considerado. La tasa real de compra fue del 17.06 %.

| Métrica | Regresión logística temporal | BG/NBD |
|---|---:|---:|
| AUC-ROC | 0.7928 | 0.7845 |
| Brier Score | 0.1118 | 0.1102 |
| Probabilidad media estimada | 15.46 % | 15.37 % |
| Tasa real de compra | 17.06 % | 17.06 % |

La regresión logística obtuvo un AUC-ROC ligeramente mayor, lo que indica una mejor capacidad para ordenar a los clientes según su probabilidad de realizar una compra.

Por su parte, BG/NBD presentó un Brier Score ligeramente menor, indicando una pequeña ventaja en la precisión global de las probabilidades estimadas.

Ambos modelos subestimaron la proporción total de compradores durante el período evaluado.

## 5. Ventajas y limitaciones de los modelos

### Regresión logística

La regresión logística permite incorporar características de comportamiento y aprender relaciones directamente asociadas con la ocurrencia de una compra futura.

En la evaluación temporal presentó una ligera ventaja en AUC-ROC.

Sin embargo, necesita etiquetas históricas de compra para entrenarse y, cuando cambia el horizonte de predicción, puede requerir un nuevo entrenamiento para estimar probabilidades adecuadas al nuevo período.

### BG/NBD

BG/NBD modela la frecuencia de compra y el abandono no observado mediante una estructura probabilística.

Una de sus principales ventajas es que permite calcular probabilidades para diferentes horizontes temporales utilizando los mismos parámetros estimados, sin necesidad de entrenar nuevamente un clasificador para cada horizonte.

En la comparación a 13 semanas obtuvo un Brier Score ligeramente menor que la regresión logística.

No obstante, sus resultados dependen de los supuestos probabilísticos del modelo y de la capacidad de los datos de compra para representar el comportamiento de los clientes.

## 6. Limitaciones de la comparación

La evaluación temporal utilizó un único período futuro de prueba, por lo que las diferencias observadas no permiten establecer superioridad estadística general.

Además, las dos ventanas históricas de entrenamiento de la regresión logística incluyeron observaciones de clientes que también aparecieron en la evaluación final. Por tanto, se trata de una evaluación prospectiva sobre clientes conocidos, no de una evaluación sobre clientes completamente nuevos.

Los procedimientos de entrenamiento tampoco son idénticos: la regresión logística utilizó ejemplos históricos etiquetados, mientras que BG/NBD se ajustó mediante un modelo probabilístico de las transacciones de calibración.

Estas diferencias deben considerarse al interpretar los resultados.

## 7. Conclusión general

La comparación mostró que la regresión logística y BG/NBD ofrecen resultados competitivos para estimar la probabilidad de compra futura de los clientes de CDNOW.

En la evaluación temporal de 13 semanas, la regresión logística presentó una ligera ventaja en capacidad de discriminación, mientras que BG/NBD obtuvo una pequeña ventaja en Brier Score.

La comparación inicial a 39 semanas también evidenció la importancia de evitar el uso de etiquetas futuras al evaluar modelos destinados a realizar pronósticos prospectivos.

En consecuencia, no se identifica un modelo universalmente superior. La elección depende del objetivo del análisis: la regresión logística puede resultar conveniente cuando se dispone de etiquetas históricas y se busca discriminar compradores, mientras que BG/NBD ofrece una alternativa probabilística especialmente útil para analizar el comportamiento de compra y generar predicciones para diferentes horizontes temporales.
