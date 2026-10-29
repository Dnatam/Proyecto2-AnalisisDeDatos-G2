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

def compras_condicionales(params, x, tx, T, tau):
    """
    E[Y(τ) | x, tx, T]: compras esperadas en las siguientes τ semanas para un cliente
    con historia (x, tx, T) (inciso 3.4):

        E[Y(τ)] = (a + b + x - 1)/(a - 1) · [1 - A^(r+x) · 2F1(r + x, b + x; a + b + x - 1; 1 - A)] / D

        A = (α + T)/(α + T + τ)
        D = 1 + δ_{x>0} · a/(b + x - 1) · ((α + T)/(α + tx))^(r+x)
    """
    r, alpha, a, b = params
    x = np.asarray(x, dtype=float)
    tx = np.asarray(tx, dtype=float)
    T = np.asarray(T, dtype=float)

    A = (alpha + T) / (alpha + T + tau)
    numerador = 1 - A ** (r + x) * hyp2f1(r + x, b + x, a + b + x - 1, 1 - A)

    # Igual que en la log-verosimilitud: con x = 0 el segundo término de D no existe
    hay_repetidas = x > 0
    x_seguro = np.where(hay_repetidas, x, 1.0)
    termino = a / (b + x_seguro - 1) * ((alpha + T) / (alpha + tx)) ** (r + x_seguro)
    D = 1 + np.where(hay_repetidas, termino, 0.0)

    return (a + b + x - 1) / (a - 1) * numerador / D

def prob_vivo(params, x, tx, T):
    """
    P(vivo | x, tx, T): probabilidad de que el cliente siga activo al final de la
    calibración (inciso 4.1):

        P(vivo) = [1 + δ_{x>0} · a/(b + x - 1) · ((α + T)/(α + tx))^(r+x)]^(-1)
    """
    r, alpha, a, b = params
    x = np.asarray(x, dtype=float)
    tx = np.asarray(tx, dtype=float)
    T = np.asarray(T, dtype=float)

    hay_repetidas = x > 0
    x_seguro = np.where(hay_repetidas, x, 1.0)
    termino = a / (b + x_seguro - 1) * ((alpha + T) / (alpha + tx)) ** (r + x_seguro)
    return 1 / (1 + np.where(hay_repetidas, termino, 0.0))

def prob_comprar(params, x, tx, T, tau):
    """
    P(Z = 1 | x, tx, T): probabilidad de hacer al menos una compra en las siguientes
    τ semanas (inciso 4.3):

        P(Z = 1) = P(vivo) · [1 - ((α + T)/(α + T + τ))^(r+x)]
    """
    r, alpha, a, b = params
    x = np.asarray(x, dtype=float)
    T = np.asarray(T, dtype=float)
    A = (alpha + T) / (alpha + T + tau)
    return prob_vivo(params, x, tx, T) * (1 - A ** (r + x))

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
    
    # Prueba 5: un cliente con T = 0 (recién llegado) no tiene historia,
    # así que E[Y(τ) | 0, 0, 0] debe ser igual a E[X(τ)]
    params_cdnow = (0.2426, 4.4136, 0.7929, 2.4259)
    cond = compras_condicionales(params_cdnow, [0], [0], [0], 39)[0]
    incond = compras_esperadas(params_cdnow, 39)
    print(f"\nPrueba 5: E[Y(39) | 0, 0, 0] = {cond:.6f} | E[X(39)] = {incond:.6f}")
    assert np.isclose(cond, incond)

    # Prueba 6: P(Z = 1) vale 0 con τ = 0, crece con τ y nunca supera P(vivo)
    x6, tx6, T6 = rfm["x"].values, rfm["tx"].values, rfm["T"].values
    pv = prob_vivo(params_cdnow, x6, tx6, T6)
    p0 = prob_comprar(params_cdnow, x6, tx6, T6, 0)
    p13 = prob_comprar(params_cdnow, x6, tx6, T6, 13)
    p39 = prob_comprar(params_cdnow, x6, tx6, T6, 39)
    p_inf = prob_comprar(params_cdnow, x6, tx6, T6, 1e30)
    assert np.allclose(p0, 0)
    assert np.all((p13 <= p39) & (p39 <= pv))
    assert np.allclose(p_inf, pv, atol=1e-4)
    print("\nPrueba 6: P(Z = 1) = 0 con τ = 0, crece con τ y tiende a P(vivo) -> OK")