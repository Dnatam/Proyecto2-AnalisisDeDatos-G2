# Validación del optimizador BG/NBD
## Objetivo
Verificar la estimación de los parámetros del modelo BG/NBD mediante scipy.optimize.minimize utilizando múltiples puntos iniciales.

## Procedimiento
Se utilizó la función ajustar() de src/ajuste_cdnow.py, que implementa el método L-BFGS-B.

Se optimizó la log-verosimilitud negativa sobre los logaritmos de los parámetros r, alpha, a y b para garantizar que los valores estimados sean positivos.

Se realizaron cinco optimizaciones con diferentes puntos iniciales y se seleccionó la solución con mayor log-verosimilitud.

## Resultados

- Clientes utilizados: 2,357.
- Inicializaciones evaluadas: 5.
- Inicializaciones convergentes: 5.
- Soluciones en las cotas: 0.
- Mejor log-verosimilitud: -9582.4292.

Parámetros estimados:

| Parámetro | Valor |
|-----------|-------|
| r | 0.2426 |
| alpha | 4.4136 |
| a | 0.7929 |
| b | 2.4259 |

## Interpretación
Las cinco inicializaciones convergieron a soluciones con valores prácticamente iguales de log-verosimilitud.

Las diferencias entre los parámetros estimados fueron pequeñas y ninguna solución quedó en las cotas.

Esto indica estabilidad numérica del procedimiento para los puntos iniciales evaluados.

La convergencia observada no garantiza que se haya encontrado el máximo global, pero proporciona evidencia de que el resultado no depende considerablemente de los cinco puntos iniciales utilizados.

## Archivos relacionados
- src/bgnbd.py
- src/ajuste_cdnow.py
- resultados/tablas/ajuste_cdnow_arranques.csv
- resultados/tablas/params_cdnow.csv