# Interfaces de las funciones del modelo BG/NBD

## 1. Objetivo
Definir las entradas, salidas, tipos de datos y restricciones de las funciones utilizadas para implementar, estimar y evaluar el modelo BG/NBD. Las interfaces se basan en las variables obtenidas del procesamiento de CDNOW y en las expresiones matemáticas de la verosimilitud desarrolladas en los incisos 1.1 y 1.2.

## 2. Variables del modelo
| Variable | Descripción | Tipo | Restricción |
|---|---|---|---|
| x | Número de compras repetidas | int | x ≥ 0 |
| tx | Tiempo de la última compra repetida | float | 0 ≤ tx ≤ T |
| T | Tiempo total de observación | float | T > 0 |
| lam | Tasa individual de compra | float | lam > 0 |
| p | Probabilidad individual de abandono | float | 0 < p < 1 |
| r | Parámetro de forma de Gamma | float | r > 0 |
| alpha | Parámetro de tasa de Gamma | float | alpha > 0 |
| a | Primer parámetro de Beta | float | a > 0 |
| b | Segundo parámetro de Beta | float | b > 0 |

Los tiempos se expresan en semanas. Cuando un cliente no registra compras repetidas (x = 0), se establece tx = 0.

## 3. Funciones del modelo

### 3.1. Verosimilitud individual
**Archivo:** `src/verificar_integral.py`

**Entradas:**
- `lam`: tasa individual de compra.
- `p`: probabilidad individual de abandono.
- `x`: número de compras repetidas.
- `tx`: tiempo de la última compra repetida.
- `T`: tiempo total de observación.

**Salida:** Valor numérico de la verosimilitud individual.

**Relación matemática:** Corresponde a la verosimilitud desarrollada en el inciso 1.1. Considera que un cliente puede continuar activo durante el período de observación o haber abandonado después de su última compra repetida. Cuando x = 0, únicamente se considera el caso correspondiente a un cliente que no ha abandonado después de una compra repetida.

### 3.2. loglik_individual()
**Archivo:** `src/bgnbd.py`

**Entradas:**
- `params`: arreglo de parámetros poblacionales `[r, alpha, a, b]`.
- `x`: número de compras repetidas de uno o varios clientes.
- `tx`: tiempo de la última compra repetida.
- `T`: tiempo total de observación.

**Salida:** Log-verosimilitud marginal de cada cliente, calculada a partir de sus datos de calibración.

**Relación matemática:** Implementa la expresión marginal obtenida en el inciso 1.2, integrando la heterogeneidad individual de las tasas de compra y las probabilidades de abandono mediante las distribuciones Gamma y Beta. Utiliza funciones logarítmicas para mejorar la estabilidad numérica y contempla el caso x = 0.

### 3.3. loglik()

**Archivo:** `src/bgnbd.py`

**Entradas:**
- `params`: arreglo de parámetros poblacionales `[r, alpha, a, b]`.
- `x`: arreglo de compras repetidas de todos los clientes.
- `tx`: arreglo de tiempos de la última compra repetida.
- `T`: arreglo de tiempos totales de observación.

**Salida:** Valor `float` correspondiente a la suma de las log-verosimilitudes individuales.

**Propósito:** Calcular la log-verosimilitud total de la muestra, que se utiliza para estimar los parámetros poblacionales del modelo BG/NBD. Los arreglos x, tx y T deben contener la misma cantidad de observaciones.

### 3.4. menos_loglik()

**Archivo:** `src/ajuste_cdnow.py`

**Entradas:**
- `log_params`: arreglo que contiene los logaritmos de `[r, alpha, a, b]`.
- `x`: arreglo de compras repetidas.
- `tx`: arreglo de tiempos de la última compra repetida.
- `T`: arreglo de tiempos totales de observación.

**Salida:** Valor `float` correspondiente al negativo de la log-verosimilitud total.

**Propósito:** Funcionar como objetivo de minimización para `scipy.optimize.minimize`. Los parámetros se transforman mediante `np.exp()` antes de calcular la log-verosimilitud, lo que garantiza que los parámetros estimados sean positivos.

### 3.5. ajustar()

**Archivo:** `src/ajuste_cdnow.py`

**Entradas:**
- `x`: arreglo de compras repetidas.
- `tx`: arreglo de tiempos de la última compra repetida.
- `T`: arreglo de tiempos totales de observación.
- `inicios`: conjunto opcional de puntos iniciales para los parámetros `[r, alpha, a, b]`.

**Salida:** Una tupla `(mejor, arranques)` que contiene dos estructuras `pandas.Series` y `pandas.DataFrame`, respectivamente.

**Descripción de las salidas:**
- `mejor`: contiene los parámetros estimados del ajuste con mayor log-verosimilitud, el valor de la log-verosimilitud, el estado de convergencia, la comprobación de cotas y el punto inicial utilizado.
- `arranques`: contiene los resultados obtenidos con cada punto inicial, permitiendo comparar las estimaciones y verificar la convergencia.

**Propósito:** Estimar los cuatro parámetros poblacionales del modelo BG/NBD utilizando el método L-BFGS-B con múltiples inicializaciones. El procedimiento selecciona la solución con mayor log-verosimilitud entre los resultados obtenidos.

### 3.6. simular_cohorte_bgnbd()

**Archivo:** `src/simulador.py`

**Entradas:**
- `r`: parámetro de forma de la distribución Gamma.
- `alpha`: parámetro de tasa de la distribución Gamma.
- `a`: primer parámetro de la distribución Beta.
- `b`: segundo parámetro de la distribución Beta.
- `n_clientes`: número de clientes que se desea simular.
- `T_min`: tiempo mínimo de observación.
- `T_max`: tiempo máximo de observación.
- `seed`: semilla aleatoria opcional para reproducir los resultados.

**Salida:** Una tupla `(xs, txs, Ts, lambdas, ps)` que contiene los arreglos de compras repetidas, tiempos de última compra, tiempos de observación, tasas individuales de compra y probabilidades individuales de abandono.

**Propósito:** Generar cohortes sintéticas de clientes siguiendo los supuestos del modelo BG/NBD, permitiendo comprobar el funcionamiento del procedimiento de estimación con parámetros conocidos.

## 4. Validaciones generales

Antes de realizar los cálculos, se deben considerar las siguientes condiciones:

1. Los parámetros poblacionales r, alpha, a y b deben ser positivos.
2. El número de compras repetidas debe ser entero y no negativo.
3. Los tiempos deben cumplir la relación 0 ≤ tx ≤ T.
4. Cuando x = 0, también debe cumplirse tx = 0.
5. Los arreglos x, tx y T deben tener la misma longitud.
6. Los tiempos deben expresarse en semanas para mantener la consistencia de los cálculos.
7. Los datos del período de holdout no deben utilizarse durante la estimación de los parámetros.

Estas condiciones representan las restricciones que deben respetar los datos y parámetros del modelo. Su definición no implica que todas las funciones realicen automáticamente las validaciones.

## 5. Relación con las siguientes tareas

Las interfaces documentadas permiten identificar cómo se conectan los diferentes componentes del proyecto. La función `loglik_individual()` calcula la contribución de cada cliente, mientras que `loglik()` obtiene la log-verosimilitud total de la muestra. Posteriormente, `menos_loglik()` transforma el problema de maximización en uno de minimización y `ajustar()` estima los parámetros utilizando múltiples inicializaciones.

Por otra parte, `simular_cohorte_bgnbd()` permite generar datos sintéticos para evaluar si el procedimiento de estimación recupera adecuadamente los parámetros utilizados en la simulación. De esta manera, las interfaces sirven como referencia para las pruebas numéricas, la calibración con CDNOW y la evaluación del modelo BG/NBD.