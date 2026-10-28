import numpy as np


def simular_cliente(lam, p, T, rng):
    """
    Simula la historia de compras de un cliente individual según los supuestos del BG/NBD:
      1. Las compras ocurren como un proceso de Poisson con tasa `lam`.
      2. Tras cada compra, el cliente decide abandonar con probabilidad `p`.
      3. El periodo de observación dura `T` semanas.

    Parámetros:
        lam (float): Tasa individual de compra (compras/semana).
        p (float): Probabilidad individual de abandono tras cada compra.
        T (float): Tiempo total de observación (semanas).
        rng (np.random.Generator): Generador de números aleatorios NumPy.

    Retorna:
        tuple (int, float): (x, tx)
            - x: Número de compras repetidas.
            - tx: Momento de la última compra repetida (en semanas).
    """
    t = 0.0
    x = 0
    tx = 0.0

    while True:
        # Tiempo hasta la siguiente compra ~ Exponencial(lam)
        wait = rng.exponential(scale=1.0 / lam)
        if t + wait > T:
            break

        t += wait
        x += 1
        tx = t

        # El cliente decide si abandona ("muere") justo después de la compra
        if rng.random() < p:
            break

    return x, tx


def simular_cohorte_bgnbd(r, alpha, a, b, n_clientes=2357, T_min=27.0, T_max=39.0, seed=None):
    """
    Simula una cohorte completa de clientes bajo el modelo BG/NBD.

    Paso a paso del modelo:
      1. Genera rates de compra: lambda ~ Gamma(r, alpha)
      2. Genera probabilidades de muerte: p ~ Beta(a, b)
      3. Asigna tiempos de observación: T ~ Uniforme(T_min, T_max)
      4. Simula la historia (x, tx) de cada cliente.

    Parámetros:
        r (float): Parámetro de forma de la Gamma.
        alpha (float): Parámetro de escala/tasa de la Gamma.
        a (float): Primer parámetro de la Beta.
        b (float): Segundo parámetro de la Beta.
        n_clientes (int): Cantidad de clientes a simular (por defecto 2,357).
        T_min (float): Tiempo mínimo de observación en semanas.
        T_max (float): Tiempo máximo de observación en semanas.
        seed (int, opcional): Semilla para reproducibilidad.

    Retorna:
        tuple (np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray):
            (x, tx, T, lambdas, ps)
    """
    rng = np.random.default_rng(seed)

    # 1. Generar heterogeneidad entre clientes según los supuestos
    lambdas = rng.gamma(shape=r, scale=1.0 / alpha, size=n_clientes)
    ps = rng.beta(a=a, b=b, size=n_clientes)
    Ts = rng.uniform(T_min, T_max, size=n_clientes)

    xs = np.zeros(n_clientes, dtype=int)
    txs = np.zeros(n_clientes, dtype=float)

    # 2. Simular cada cliente individualmente
    for i in range(n_clientes):
        xs[i], txs[i] = simular_cliente(lambdas[i], ps[i], Ts[i], rng)

    return xs, txs, Ts, lambdas, ps


if __name__ == "__main__":
    # Prueba rápida del simulador
    r, alpha, a, b = 0.25, 4.0, 0.8, 2.5
    x_sim, tx_sim, T_sim, lams, ps = simular_cohorte_bgnbd(r, alpha, a, b, seed=42)

    print("=== PRUEBA DEL SIMULADOR BG/NBD (D3.T4) ===")
    print(f"Clientes simulados: {len(x_sim)}")
    print(f"Promedio de compras repetidas (x): {x_sim.mean():.4f}")
    print(f"Máximo de compras repetidas: {x_sim.max()}")
    print(f"Fracción de clientes sin re-compra (x=0): {(x_sim == 0).mean():.4f}")
    print("¡Simulador listo y verificado correctamente!")