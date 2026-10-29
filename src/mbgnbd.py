from pathlib import Path

import numpy as np
from scipy.special import betaln, gammaln, hyp2f1

RAIZ = Path(__file__).resolve().parents[1]


def loglik_individual(params, x, tx, T):
    """
    log L de cada cliente:

        L = Γ(r+x) α^r / Γ(r) · [ B(a, b+x+1)/B(a,b) · (α+T)^-(r+x)
                                  + B(a+1, b+x)/B(a,b) · (α+tx)^-(r+x) ]

    Ya no hay δ_{x>0}: el segundo término existe también con x = 0
    (el cliente murió justo después de su primera compra).
    """
    r, alpha, a, b = params
    x = np.asarray(x, dtype=float)
    tx = np.asarray(tx, dtype=float)
    T = np.asarray(T, dtype=float)

    c = gammaln(r + x) - gammaln(r) + r * np.log(alpha)
    A = betaln(a, b + x + 1) - betaln(a, b) - (r + x) * np.log(alpha + T)
    B = betaln(a + 1, b + x) - betaln(a, b) - (r + x) * np.log(alpha + tx)
    return c + np.logaddexp(A, B)


def loglik(params, x, tx, T):
    """Log-verosimilitud total de la muestra."""
    return np.sum(loglik_individual(params, x, tx, T))


def compras_esperadas(params, t):
    """
    E[X(t)] = b/(a - 1) · [1 - (α/(α + t))^r · 2F1(r, b + 1; a + b; t/(α + t))]
    """
    r, alpha, a, b = params
    t = np.maximum(np.asarray(t, dtype=float), 0.0)
    z = t / (alpha + t)
    return b / (a - 1) * (1 - (alpha / (alpha + t)) ** r * hyp2f1(r, b + 1, a + b, z))


def compras_condicionales(params, x, tx, T, tau):
    """
    E[Y(τ) | x, tx, T] = (a + b + x)/(a - 1) · [1 - A^(r+x) · 2F1(r + x, b + x + 1; a + b + x; 1 - A)] / D'

        A  = (α + T)/(α + T + τ)
        D' = 1 + a/(b + x) · ((α + T)/(α + tx))^(r+x)
    """
    r, alpha, a, b = params
    x = np.asarray(x, dtype=float)
    tx = np.asarray(tx, dtype=float)
    T = np.asarray(T, dtype=float)

    A = (alpha + T) / (alpha + T + tau)
    numerador = 1 - A ** (r + x) * hyp2f1(r + x, b + x + 1, a + b + x, 1 - A)
    D = 1 + a / (b + x) * ((alpha + T) / (alpha + tx)) ** (r + x)
    return (a + b + x) / (a - 1) * numerador / D


def prob_vivo(params, x, tx, T):
    """
    P(vivo | x, tx, T) = [1 + a/(b + x) · ((α + T)/(α + tx))^(r+x)]^(-1)
    """
    r, alpha, a, b = params
    x = np.asarray(x, dtype=float)
    tx = np.asarray(tx, dtype=float)
    T = np.asarray(T, dtype=float)
    return 1 / (1 + a / (b + x) * ((alpha + T) / (alpha + tx)) ** (r + x))


def prob_comprar(params, x, tx, T, tau):
    """
    P(Z = 1 | x, tx, T) = P(vivo) · [1 - ((α + T)/(α + T + τ))^(r+x)]

    Es la misma fórmula del BG/NBD (4.3): solo cambia P(vivo).
    """
    r, alpha, a, b = params
    x = np.asarray(x, dtype=float)
    T = np.asarray(T, dtype=float)
    A = (alpha + T) / (alpha + T + tau)
    return prob_vivo(params, x, tx, T) * (1 - A ** (r + x))


if __name__ == "__main__":
    from scipy import integrate
    from scipy.stats import beta, gamma

    params_prueba = (0.25, 4.0, 0.8, 2.5)
    r, alpha, a, b = params_prueba

    # Prueba 1: la fórmula cerrada coincide con la integral doble de la
    # verosimilitud individual del MBG/NBD sobre λ ~ Gamma y p ~ Beta
    def L_individual(lam, p, x, tx, T):
        # Vivo en T: sobrevivió a la primera compra y a las x repetidas -> (1-p)^(x+1)
        # Murió tras la compra en tx: sobrevivió a x compras y murió en la siguiente -> p(1-p)^x
        return ((1 - p) ** (x + 1) * lam ** x * np.exp(-lam * T)
                + p * (1 - p) ** x * lam ** x * np.exp(-lam * tx))

    print("Prueba 1: fórmula cerrada contra integral numérica")
    for x, tx, T in [(0, 0.0, 38.86), (1, 1.71, 38.86), (2, 30.43, 38.86), (5, 20.0, 30.0)]:
        f = lambda p, lam: (L_individual(lam, p, x, tx, T)
                            * gamma.pdf(lam, r, scale=1 / alpha) * beta.pdf(p, a, b))
        numerica, _ = integrate.dblquad(f, 0, np.inf, 0, 1, epsabs=1e-13, epsrel=1e-10)
        cerrada = np.exp(loglik_individual(params_prueba, [x], [tx], [T])[0])
        print(f"  x={x}: cerrada = {cerrada:.6e} | numérica = {numerica:.6e}")
        assert np.isclose(cerrada, numerica, rtol=1e-5)

    # Prueba 2: un cliente recién llegado (T = 0) no tiene historia -> E[Y(τ)] = E[X(τ)]
    cond = compras_condicionales(params_prueba, [0], [0], [0], 39)[0]
    incond = compras_esperadas(params_prueba, 39)
    print(f"\nPrueba 2: E[Y(39) | 0, 0, 0] = {cond:.6f} | E[X(39)] = {incond:.6f}")
    assert np.isclose(cond, incond)

    # Prueba 3: con x = 0, P(vivo) ya no es 1 y depende de T
    pv0 = prob_vivo(params_prueba, [0, 0, 0], [0, 0, 0], [5.0, 20.0, 38.86])
    print(f"\nPrueba 3: P(vivo) con x = 0 y T = 5, 20, 38.86 -> {np.round(pv0, 4)}")
    assert np.all(pv0 < 1) and np.all(np.diff(pv0) < 0)

    # Prueba 4: P(Z = 1) = 0 con τ = 0 y tiende a P(vivo) con τ muy grande
    p0 = prob_comprar(params_prueba, [0, 3], [0, 10.0], [30.0, 30.0], 0)
    p_inf = prob_comprar(params_prueba, [0, 3], [0, 10.0], [30.0, 30.0], 1e30)
    pv = prob_vivo(params_prueba, [0, 3], [0, 10.0], [30.0, 30.0])
    assert np.allclose(p0, 0) and np.allclose(p_inf, pv, atol=1e-4)
    print("\nPrueba 4: P(Z = 1) = 0 con τ = 0 y tiende a P(vivo) -> OK")