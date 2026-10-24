
# Interfaces de las funciones del modelo BG/NBD

## 1. Objetivo

Definir las entradas, salidas, tipos de datos y restricciones de las
funciones necesarias para implementar y estimar el modelo BG/NBD.

Estas interfaces se basan en las variables obtenidas del procesamiento
de CDNOW y en la verosimilitud derivada en los incisos 1.1 y 1.2.

## 2. Variables del modelo

| Variable | Descripción | Tipo | Restricción |
|----------|-------------|------|-------------|
| x | Número de compras repetidas | int | x >= 0 |
| tx | Tiempo hasta la última compra repetida | float | 0 <= tx <= T |
| T | Tiempo total de observación | float | T > 0 |
| lam | Tasa individual de compra | float | lam > 0 |
| p | Probabilidad individual de abandono | float | 0 < p < 1 |
| r | Parámetro de forma de Gamma | float | r > 0 |
| alpha | Parámetro de tasa de Gamma | float | alpha > 0 |
| a | Primer parámetro de Beta | float | a > 0 |
| b | Segundo parámetro de Beta | float | b > 0 |

Los tiempos se expresan en semanas.

Cuando x = 0, se establece tx = 0.

## 3. Funciones definidas

### 3.1 verosimilitud_individual()

Entradas:
- lam: tasa de compra individual.
- p: probabilidad individual de abandono.
- x: número de compras repetidas.
- tx: tiempo de la última compra repetida.
- T: tiempo total de observación.

Salida:
- float: verosimilitud individual con lam y p conocidos.

Relación matemática:
- Corresponde a la verosimilitud derivada en el inciso 1.1.
- Considera que el cliente puede seguir activo o haber abandonado
  después de su última compra repetida.
- Si x = 0, solamente se considera el caso de cliente activo.

### 3.2 log_verosimilitud()

Entradas:
- r, alpha: parámetros poblacionales de Gamma.
- a, b: parámetros poblacionales de Beta.
- x, tx, T: datos individuales de calibración.

Salida:
- float: log-verosimilitud marginal de un cliente.

Relación matemática:
- Corresponde a la fórmula del inciso 1.2.
- Integra la heterogeneidad individual de lam y p.
- Se utilizarán funciones logarítmicas para mejorar la
  estabilidad numérica.

### 3.3 log_verosimilitud_total()

Entradas:
- parametros: arreglo [r, alpha, a, b].
- x: arreglo de compras repetidas.
- tx: arreglo de tiempos de última compra repetida.
- T: arreglo de tiempos totales de observación.

Salida:
- float: suma de las log-verosimilitudes individuales.

Restricciones:
- Los arreglos x, tx y T deben tener igual longitud.
- Los parámetros poblacionales deben ser positivos.

### 3.4 neg_log_verosimilitud()

Entradas:
- parametros_log: logaritmos de [r, alpha, a, b].
- x, tx, T: arreglos de datos de calibración.

Salida:
- float: negativo de la log-verosimilitud total.

Propósito:
- Utilizarse como función objetivo de scipy.optimize.minimize.
- La transformación exponencial permite recuperar parámetros
  positivos durante la optimización.

### 3.5 ajustar_bgnbd()

Entradas:
- x, tx, T: arreglos de datos de calibración.
- iniciales: tupla de valores iniciales (r, alpha, a, b).

Salida:
- dict: resultados del ajuste.

El diccionario deberá incluir:
- r: parámetro de forma estimado.
- alpha: parámetro de tasa estimado.
- a: primer parámetro Beta estimado.
- b: segundo parámetro Beta estimado.
- log_verosimilitud: valor total alcanzado.
- convergencia: indicador de éxito del optimizador.
- mensaje: información del proceso de optimización.

## 4. Validaciones generales

Antes de realizar los cálculos se deberá verificar que:

1. Todos los parámetros poblacionales sean positivos.
2. El número de compras repetidas sea entero y no negativo.
3. Se cumpla 0 <= tx <= T.
4. Cuando x = 0, también se cumpla tx = 0.
5. Los arreglos de datos tengan igual longitud.
6. Los tiempos estén expresados en semanas.
7. Los datos de holdout no se utilicen para estimar parámetros.

## 5. Relación con las siguientes tareas

Estas interfaces permitirán:

- Implementar la log-verosimilitud del BG/NBD.
- Evaluar correctamente los casos con x = 0.
- Optimizar los parámetros mediante SciPy.
- Ajustar el modelo utilizando CDNOW.
- Reutilizar las funciones durante las simulaciones.

La implementación matemática y las pruebas numéricas se realizarán
en las siguientes etapas del proyecto.
