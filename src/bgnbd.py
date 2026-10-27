from pathlib import Path
import numpy as np
from scipy.special import betaln, gammaln, hyp2f1

RAIZ = Path(__file__).resolve().parents[1]


def loglik_individual(params, x, tx, T):
    """
    log L(r, α, a, b | x, tx, T) de cada cliente (inciso 1.2):

        log L_i = c_i + log( e^{A_i} + δ_{x>0} e^{B_i} )

        c_i = log Γ(r + x) − log Γ(r) + r log α
        A_i = log B(a, b + x) − log B(a, b) − (r + x) log(α + T)        (historia A: sigue vivo)
        B_i = log B(a + 1, b + x − 1) − log B(a, b) − (r + x) log(α + tx)  (historia B: murió en tx)
    """
    r, alpha, a, b = params
    x = np.asarray(x, dtype=float)
    tx = np.asarray(tx, dtype=float)
    T = np.asarray(T, dtype=float)

    c = gammaln(r + x) - gammaln(r) + r * np.log(alpha)
    A = betaln(a, b + x) - betaln(a, b) - (r + x) * np.log(alpha + T)

    hay_repetidas = x > 0
    x_seguro = np.where(hay_repetidas, x, 1.0)
    B = (betaln(a + 1, b + x_seguro - 1) - betaln(a, b)
         - (r + x_seguro) * np.log(alpha + tx))
    B = np.where(hay_repetidas, B, -np.inf)

    # log(e^A + e^B) calculado de forma estable
    return c + np.logaddexp(A, B)


def loglik(params, x, tx, T):
    """Log-verosimilitud total de la muestra."""
    return np.sum(loglik_individual(params, x, tx, T))

def compras_esperadas(params, t):
    """
    E[X(t)]: número esperado de compras repetidas en las t semanas posteriores a la
    primera compra, para un cliente que acaba de llegar (inciso 3.1):

        E[X(t)] = (a + b - 1)/(a - 1) · [1 - (α/(α + t))^r · 2F1(r, b; a + b - 1; t/(α + t))]

    t puede ser un número o un arreglo; para t <= 0 devuelve 0.
    """
    r, alpha, a, b = params
    t = np.maximum(np.asarray(t, dtype=float), 0.0)
    z = t / (alpha + t)
    return ((a + b - 1) / (a - 1)
            * (1 - (alpha / (alpha + t)) ** r * hyp2f1(r, b, a + b - 1, z)))

if __name__ == "__main__":
    import pandas as pd
    from verificar_integral import L_cerrada

    params_articulo = (0.243, 4.414, 0.793, 2.426)

    # Prueba 1: cliente por cliente contra la fórmula cerrada de 1.2
    print("Prueba 1: comparación con la fórmula de 1.2")
    casos = [(0, 0.0, 38.86), (1, 1.71, 38.86), (2, 30.43, 38.86), (5, 20.0, 30.0)]
    for x, tx, T in casos:
        nuestro = loglik_individual(params_articulo, [x], [tx], [T])[0]
        esperado = np.log(L_cerrada(x, tx, T))
        print(f"  x={x}: loglik_individual = {nuestro:.6f} | log(L_cerrada) = {esperado:.6f}")

    # Prueba 2: CDNOW completo con los parámetros del artículo
    rfm = pd.read_csv(RAIZ / "data" / "procesado" / "cdnow_rfm.csv")
    ll = loglik(params_articulo, rfm["x"], rfm["tx"], rfm["T"])
    print(f"\nPrueba 2: log-verosimilitud de CDNOW con los parámetros del artículo = {ll:.2f}")
    print("  (el artículo reporta -9582.4 en su óptimo)")

    # Prueba 3: con x = 0, la verosimilitud debe ser (α / (α + T))^r para cualquier a, b
    print("\nPrueba 3: clientes con x = 0 y distintos valores de b")
    r, alpha = 0.25, 4.0
    T0 = np.array([27.0, 33.0, 38.86])
    esperado = r * np.log(alpha / (alpha + T0))
    for b in [2.5, 1.0, 0.5, 0.1]:
        obtenido = loglik_individual((r, alpha, 0.8, b), np.zeros(3), np.zeros(3), T0)
        ok = np.allclose(obtenido, esperado)
        print(f"  b = {b:<4}: {np.round(obtenido, 6)} -> {'OK' if ok else 'ERROR'}")
        assert ok

    # Prueba 4: ningún nan ni inf en una muestra mixta, con parámetros extremos
    rng = np.random.default_rng(0)
    x_m, tx_m, T_m = rfm["x"].values, rfm["tx"].values, rfm["T"].values
    n_malos = 0
    for _ in range(2000):
        p = np.exp(rng.uniform(-10, 10, size=4))
        if not np.isfinite(loglik(p, x_m, tx_m, T_m)):
            n_malos += 1
    print(f"\nPrueba 4: 2000 combinaciones extremas de parámetros -> {n_malos} resultados no finitos")