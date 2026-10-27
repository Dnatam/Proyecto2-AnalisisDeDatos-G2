from pathlib import Path

import numpy as np
from scipy.special import betaln, gammaln

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
    B = betaln(a + 1, b + x - 1) - betaln(a, b) - (r + x) * np.log(alpha + tx)

    # δ_{x>0} en escala logarítmica: si x = 0, el término B no existe -> log(0) = -inf
    B = np.where(x > 0, B, -np.inf)

    # log(e^A + e^B) calculado de forma estable
    return c + np.logaddexp(A, B)

def loglik(params, x, tx, T):
    """Log-verosimilitud total de la muestra."""
    return np.sum(loglik_individual(params, x, tx, T))

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