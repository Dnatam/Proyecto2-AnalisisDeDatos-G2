# Prueba de la implementación del modelo BG/NBD con un conjunto pequeño de clientes

## 1. Objetivo

Comprobar el funcionamiento de la implementación del modelo BG/NBD y del procedimiento de optimización mediante un conjunto pequeño de clientes, verificando el cálculo de la log-verosimilitud, la estimación de parámetros y la convergencia del optimizador.

## 2. Datos utilizados

Se construyó un conjunto ficticio de 10 clientes con diferentes cantidades de compras repetidas y tiempos de última compra. Todos los clientes tienen un período de observación de 30 semanas y se incluyeron casos sin compras repetidas (x = 0) para verificar su tratamiento en el modelo.

| Cliente | x | tx | T |
|---|---|---|---|
| 1 | 0 | 0 | 30 |
| 2 | 1 | 5 | 30 |
| 3 | 2 | 10 | 30 |
| 4 | 3 | 15 | 30 |
| 5 | 0 | 0 | 30 |
| 6 | 4 | 20 | 30 |
| 7 | 1 | 8 | 30 |
| 8 | 2 | 12 | 30 |
| 9 | 5 | 25 | 30 |
| 10 | 0 | 0 | 30 |

Donde x representa el número de compras repetidas, tx el tiempo transcurrido hasta la última compra repetida y T el tiempo total de observación. Los tiempos se expresan en semanas.

## 3. Procedimiento

Se utilizó la función `loglik()` del archivo `src/bgnbd.py` para calcular la log-verosimilitud inicial con los parámetros `[1.0, 1.0, 1.0, 1.0]`. Posteriormente, se ejecutó la función `ajustar()` del archivo `src/ajuste_cdnow.py`, que utiliza `scipy.optimize.minimize` con el método L-BFGS-B y cinco puntos iniciales diferentes.

El procedimiento permitió obtener los parámetros estimados, calcular nuevamente la log-verosimilitud y comparar los resultados antes y después del ajuste. También se verificó que los parámetros fueran positivos, que el optimizador reportara convergencia y que la mejor solución no estuviera pegada a las cotas establecidas.

## 4. Resultados

### 4.1. Comparación de log-verosimilitud

| Indicador | Resultado |
|---|---:|
| Log-verosimilitud inicial | -79.7446 |
| Log-verosimilitud final | -67.0601 |
| Mejora de log-verosimilitud | 12.6845 |

La log-verosimilitud aumentó de -79.7446 a -67.0601, lo que indica que el procedimiento de optimización encontró parámetros que proporcionan un mejor ajuste a los datos que los parámetros iniciales utilizados.

### 4.2. Parámetros estimados

| Parámetro | Valor estimado |
|---|---:|
| r | 1.2930 |
| alpha | 14.3248 |
| a | 478.5491 |
| b | 1611.8440 |

### 4.3. Resultados de las inicializaciones

| Inicio | Log-verosimilitud | Convergencia | En cota |
|---|---:|---|---|
| (1.0, 1.0, 1.0, 1.0) | -67.0601 | Sí | No |
| (0.5, 5.0, 1.0, 3.0) | -67.0603 | Sí | No |
| (0.1, 1.0, 0.5, 0.5) | -67.0604 | Sí | No |
| (2.0, 10.0, 2.0, 5.0) | -67.0601 | Sí | No |
| (0.3, 20.0, 0.2, 1.0) | -67.0602 | Sí | No |

Las cinco inicializaciones reportaron convergencia y alcanzaron valores de log-verosimilitud muy similares. Ninguna de las soluciones quedó pegada a las cotas del optimizador.

### 4.4. Verificaciones realizadas

| Verificación | Resultado |
|---|---|
| Mejora de la log-verosimilitud | True |
| Todos los parámetros positivos | True |
| Convergencia del mejor ajuste | True |
| Mejor ajuste en una cota | False |

## 5. Interpretación

La implementación del modelo BG/NBD permitió procesar correctamente los 10 clientes, incluyendo aquellos que no registraron compras repetidas. El optimizador ejecutó las cinco inicializaciones sin errores y obtuvo una mejora en la log-verosimilitud, lo que confirma el funcionamiento del procedimiento de estimación para el conjunto de prueba.

Se observó que los parámetros a y b alcanzaron valores elevados y presentaron diferencias entre las inicializaciones, aunque los valores finales de log-verosimilitud fueron prácticamente iguales. Esto sugiere que, con una muestra tan pequeña, los parámetros relacionados con la distribución Beta pueden presentar dificultades de identificación y mayor inestabilidad en sus estimaciones.

Los resultados de esta prueba permiten verificar la ejecución y el comportamiento del modelo con pocos clientes, pero no constituyen una evaluación de la precisión de recuperación de parámetros verdaderos, ya que los datos utilizados fueron definidos manualmente y no se generaron a partir de parámetros poblacionales conocidos.

## 6. Conclusión

La prueba de la implementación del modelo BG/NBD con un conjunto pequeño de clientes se realizó satisfactoriamente. Se comprobó el cálculo de la log-verosimilitud, la ejecución del optimizador con múltiples inicializaciones, la obtención de parámetros positivos y la convergencia de las cinco ejecuciones. La mejora de la log-verosimilitud confirma que el procedimiento encontró un ajuste superior al punto inicial evaluado, mientras que la variabilidad de algunos parámetros evidencia las limitaciones de estimación con muestras reducidas.

## 7. Archivos relacionados

- `src/prueba_clientes_pequenos.py`: implementación de la prueba con 10 clientes ficticios.
- `src/bgnbd.py`: cálculo de la log-verosimilitud del modelo.
- `src/ajuste_cdnow.py`: procedimiento de optimización mediante múltiples inicializaciones.