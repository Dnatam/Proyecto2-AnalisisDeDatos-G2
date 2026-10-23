import numpy as np
from scipy import integrate
from scipy.special import betaln, gammaln
from scipy.stats import beta, gamma

# Parámetros del artículo de Fader, Hardie y Lee (2005)
r, alpha, a, b = 0.243, 4.414, 0.793, 2.426


def L_individual(lam, p, x, tx, T):
    """Verosimilitud de 1.1 con λ y p conocidas."""
    valor = (1 - p) ** x * lam ** x * np.exp(-lam * T)
    if x > 0:
        valor += p * (1 - p) ** (x - 1) * lam ** x * np.exp(-lam * tx)
    return valor


def L_cerrada(x, tx, T):
    """Fórmula final de 1.2."""
    comun = np.exp(gammaln(r + x) - gammaln(r) + r * np.log(alpha))
    termino_a = np.exp(betaln(a, b + x) - betaln(a, b)) / (alpha + T) ** (r + x)
    termino_b = 0.0
    if x > 0:
        termino_b = np.exp(betaln(a + 1, b + x - 1) - betaln(a, b)) / (alpha + tx) ** (r + x)
    return comun * (termino_a + termino_b)


def L_numerica(x, tx, T):
    """Integral doble de 1.1 por la densidad conjunta (Gamma × Beta)."""
    integrando = lambda p, lam: (L_individual(lam, p, x, tx, T)
                                 * gamma.pdf(lam, r, scale=1 / alpha)   # tasa α -> escala 1/α
                                 * beta.pdf(p, a, b))
    valor, _ = integrate.dblquad(integrando, 0, np.inf, 0, 1, epsabs=1e-13, epsrel=1e-10)
    return valor


if __name__ == "__main__":
    casos = [(0, 0.0, 38.86), (1, 1.71, 38.86), (2, 30.43, 38.86), (5, 20.0, 30.0)]
    for x, tx, T in casos:
        c, n = L_cerrada(x, tx, T), L_numerica(x, tx, T)
        print(f"x={x}, tx={tx:5.2f}, T={T:5.2f} | cerrada = {c:.6e} | "
              f"numérica = {n:.6e} | dif. relativa = {abs(c - n) / n:.1e}")