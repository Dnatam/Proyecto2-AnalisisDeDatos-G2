from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import gammaln

RAIZ = Path(__file__).resolve().parents[1]
PROCESADO = RAIZ / "data" / "procesado"
TABLAS = RAIZ / "resultados" / "tablas"


def loglik_nbd(log_par, x, T):
    """NBD: log L = log Γ(r+x) − log Γ(r) + r log α − (r+x) log(α+T)."""
    r, alpha = np.exp(log_par)
    return np.sum(gammaln(r + x) - gammaln(r) + r * np.log(alpha) - (r + x) * np.log(alpha + T))


def ajustar_nbd(x, T):
    res = minimize(lambda lp: -loglik_nbd(lp, x, T), np.log([0.5, 5.0]), method="Nelder-Mead")
    return np.exp(res.x), -res.fun


filas = []
for nombre, archivo_rfm, archivo_params in [
    ("Online Retail", "online_retail_rfm.csv", "params_online_retail.csv"),
    ("CDNOW", "cdnow_rfm.csv", "params_cdnow.csv"),
]:
    rfm = pd.read_csv(PROCESADO / archivo_rfm)
    bg = pd.read_csv(TABLAS / archivo_params).iloc[0]
    (r_nbd, a_nbd), ll_nbd = ajustar_nbd(rfm["x"].values, rfm["T"].values)
    filas.append({
        "datos": nombre,
        "E_p_bgnbd": bg["a"] / (bg["a"] + bg["b"]),
        "loglik_bgnbd": bg["loglik"],
        "r_nbd": r_nbd, "alpha_nbd": a_nbd,
        "loglik_nbd": ll_nbd,
        "ganancia_bgnbd": bg["loglik"] - ll_nbd,
        "frac_x0": (rfm["x"] == 0).mean(),
        "frac_x0_que_compra_en_holdout": (rfm.loc[rfm["x"] == 0, "x_star"] > 0).mean(),
    })

tabla = pd.DataFrame(filas)
print(tabla.T.to_string(header=False))
tabla.to_csv(TABLAS / "online_retail_bg_vs_nbd.csv", index=False)
print("\nGuardado en resultados/tablas/online_retail_bg_vs_nbd.csv")