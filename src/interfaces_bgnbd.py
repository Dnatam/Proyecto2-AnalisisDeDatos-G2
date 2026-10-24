import numpy as np
from numpy.typing import NDArray

# Verosimilitud individual con lambda y p conocidos
def verosimilitud_individual(
    lam: float,
    p: float,
    x: int,
    tx: float,
    T: float
) -> float:

    # lam: tasa de compra individual (> 0)
    # p: probabilidad de abandono (0 < p < 1)
    # x: número de compras repetidas (>= 0)
    # tx: tiempo de la última compra repetida, en semanas
    # T: tiempo total de observación, en semanas
    # Retorna: verosimilitud individual

    raise NotImplementedError

# Log-verosimilitud marginal de un cliente
def log_verosimilitud(
    r: float,
    alpha: float,
    a: float,
    b: float,
    x: int,
    tx: float,
    T: float
) -> float:

    # r, alpha: parámetros de la distribución Gamma
    # a, b: parámetros de la distribución Beta
    # x, tx, T: datos de calibración del cliente
    # Retorna: log-verosimilitud individual

    raise NotImplementedError

# Log-verosimilitud total de todos los clientes
def log_verosimilitud_total(
    parametros: NDArray[np.float64],
    x: NDArray[np.int64],
    tx: NDArray[np.float64],
    T: NDArray[np.float64]
) -> float:

    # parametros: arreglo [r, alpha, a, b]
    # x: compras repetidas de todos los clientes
    # tx: tiempo de última compra repetida
    # T: tiempo total de observación
    # Los tres arreglos deben tener igual longitud
    # Retorna: suma de las log-verosimilitudes

    raise NotImplementedError

# Función objetivo para el optimizador
def neg_log_verosimilitud(
    parametros_log: NDArray[np.float64],
    x: NDArray[np.int64],
    tx: NDArray[np.float64],
    T: NDArray[np.float64]
) -> float:

    # parametros_log: logaritmos de [r, alpha, a, b]
    # Se recuperan los parámetros usando np.exp()
    # Esto garantiza que los parámetros sean positivos
    # Retorna: negativo de la log-verosimilitud total

    raise NotImplementedError

# Estimación de los parámetros del modelo BG/NBD
def ajustar_bgnbd(
    x: NDArray[np.int64],
    tx: NDArray[np.float64],
    T: NDArray[np.float64],
    iniciales: tuple[float, float, float, float]
) -> dict:

    # x, tx, T: datos de calibración
    # iniciales: valores iniciales de r, alpha, a y b
    # Retorna: diccionario con los parámetros estimados,
    # log-verosimilitud y estado de convergencia

    raise NotImplementedError