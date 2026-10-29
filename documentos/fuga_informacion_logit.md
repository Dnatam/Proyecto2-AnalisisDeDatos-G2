# Fuga de información en la comparación entre regresión logística y BG/NBD

## 1. Objetivo

Analizar si la comparación ingenua entre la regresión logística y el modelo BG/NBD, realizada en el inciso 6.1, fue justa, identificando la fuga de información temporal y su efecto sobre la evaluación predictiva.

Este análisis corresponde al inciso 6.2 del proyecto.

## 2. Comparación realizada

En el inciso 6.1 se implementó una regresión logística para predecir si un cliente realizaría al menos una compra durante el período de holdout.

La variable objetivo se definió como:

$$
Z_i =
\begin{cases}
1, & \text{si el cliente compró en holdout} \\
0, & \text{si no compró en holdout}
\end{cases}
$$

El período de calibración finalizó el 30 de septiembre de 1997, mientras que el holdout comprendió del 1 de octubre de 1997 al 30 de junio de 1998.

La regresión logística se evaluó mediante validación cruzada estratificada de 5 folds y 20 semillas, utilizando las etiquetas de compra en holdout.

Por su parte, BG/NBD estimó sus parámetros únicamente a partir de las historias de compra observadas durante calibración.

## 3. ¿Dónde ocurre la fuga de información?

La fuga de información aparece porque la regresión logística utiliza, durante su entrenamiento, etiquetas construidas con compras realizadas después de la fecha en la que supuestamente debía efectuarse el pronóstico.

En cada fold, la regresión logística se entrena con las etiquetas de holdout de otros clientes. Aunque los clientes de entrenamiento y validación están separados, las etiquetas utilizadas contienen información sobre lo ocurrido entre octubre de 1997 y junio de 1998.

Por ejemplo, si se quisiera realizar una predicción el 30 de septiembre de 1997, todavía no sería posible conocer qué clientes comprarían durante los siguientes nueve meses.

Sin embargo, la regresión logística de la comparación ingenua utiliza precisamente esa información para aprender la relación entre las características de los clientes y sus compras futuras.

BG/NBD, en cambio, no utiliza las compras del holdout para estimar sus parámetros.

Por lo tanto, los modelos no compiten bajo las mismas condiciones de información.

## 4. ¿Por qué la validación cruzada no elimina el problema?

La validación cruzada evita que una misma observación sea utilizada simultáneamente para entrenar y evaluar la regresión logística dentro de un fold.

Sin embargo, no garantiza que la información utilizada para entrenar estuviera disponible en la fecha del pronóstico.

En este caso, la separación por clientes es correcta, pero las etiquetas de entrenamiento corresponden a un período futuro respecto al cierre de calibración.

Por eso, el problema no consiste en que los clientes de validación aparezcan directamente en el entrenamiento, sino en que se utiliza información futura de otros clientes.

La validación cruzada mide el desempeño del modelo cuando ya se conocen las etiquetas del período evaluado para parte de la cohorte, una condición distinta de la predicción que habría sido posible el 30 de septiembre de 1997.

## 5. ¿Con qué etiquetas se podía entrenar la logística el 30 de septiembre?

En una situación real, el 30 de septiembre de 1997 únicamente estarían disponibles las compras registradas hasta esa fecha.

Por lo tanto, la regresión logística tendría que entrenarse con etiquetas construidas a partir de períodos históricos que ya hubieran finalizado.

Por ejemplo, podría utilizarse la información de los clientes hasta el 1 de julio de 1997 para calcular sus características y definir como etiqueta si realizaron compras entre el 2 de julio y el 30 de septiembre de 1997.

De esta manera, tanto las características como las etiquetas de entrenamiento estarían disponibles al momento de realizar la predicción.

Posteriormente, el modelo entrenado podría aplicarse a las características calculadas al 30 de septiembre para pronosticar compras en un período futuro.

Este procedimiento es el que se desarrolla en el inciso 6.3.

## 6. Relación con la fuga de información en series de tiempo

El problema es equivalente a utilizar observaciones futuras para construir un modelo que supuestamente realiza predicciones desde una fecha anterior.

En series de tiempo, es necesario respetar el orden cronológico: el entrenamiento debe utilizar información pasada y la evaluación debe realizarse sobre períodos posteriores.

Si se incorporan datos futuros al entrenamiento, el modelo obtiene una ventaja que no tendría en una aplicación real.

En este proyecto, la fuga no proviene de incluir directamente las compras futuras como características, sino de utilizar sus resultados como etiquetas de entrenamiento.

Esto puede producir una evaluación demasiado favorable de la regresión logística frente a BG/NBD.

## 7. Conclusión

La comparación ingenua del inciso 6.1 no fue completamente justa porque la regresión logística y BG/NBD utilizaron información disponible en momentos diferentes.

Aunque la validación cruzada separó correctamente los clientes de entrenamiento y validación, la regresión logística aprendió utilizando etiquetas del holdout de otros clientes.

BG/NBD, por el contrario, se ajustó únicamente con información disponible hasta el 30 de septiembre de 1997.

Por lo tanto, cualquier ventaja de la regresión logística en esta comparación debe interpretarse con cautela, ya que no demuestra necesariamente que hubiera realizado mejores predicciones en una situación real.

Para obtener una comparación temporalmente justa, es necesario entrenar la regresión logística con características y etiquetas de períodos históricos ya observados, y evaluar ambos modelos sobre el mismo período futuro.
