from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from bgnbd import loglik

RAIZ = Path(__file__).resolve().parents[1]
TABLAS = RAIZ / "resultados" / "tablas"
NOMBRES = ["r", "alpha", "a", "b"]

# Puntos iniciales para (r, α, a, b). Se optimiza sobre sus logaritmos.
INICIOS = [
    (1.0, 1.0, 1.0, 1.0),
    (0.5, 5.0, 1.0, 3.0),
    (0.1, 1.0, 0.5, 0.5),
    (2.0, 10.0, 2.0, 5.0),
    (0.3, 20.0, 0.2, 1.0),
]
COTA = 10.0 


def menos_loglik(log_params, x, tx, T):
    """-log L en función de log(r, α, a, b): así los parámetros siempre son positivos."""
    return -loglik(np.exp(log_params), x, tx, T)


def ajustar(x, tx, T, inicios=INICIOS):
    """Máxima verosimilitud desde varios puntos iniciales con L-BFGS-B."""
    arranques = []
    for inicio in inicios:
        res = minimize(menos_loglik, np.log(inicio), args=(x, tx, T),
                       method="L-BFGS-B", bounds=[(-COTA, COTA)] * 4)
        fila = dict(zip(NOMBRES, np.exp(res.x)))
        fila["loglik"] = -res.fun
        fila["convergio"] = res.success
        fila["en_cota"] = bool(np.any(np.abs(res.x) > COTA - 1e-3))
        fila["inicio"] = str(inicio)
        arranques.append(fila)
    arranques = pd.DataFrame(arranques)
    mejor = arranques.loc[arranques["loglik"].idxmax()]
    return mejor, arranques


if __name__ == "__main__":
    rfm = pd.read_csv(RAIZ / "data" / "procesado" / "cdnow_rfm.csv")
    x, tx, T = rfm["x"].values, rfm["tx"].values, rfm["T"].values

    mejor, arranques = ajustar(x, tx, T)

    print("Resultado de cada punto inicial:")
    print(arranques.round(4).to_string(index=False))

    coinciden = (np.abs(arranques["loglik"] - mejor["loglik"]) < 1e-2).sum()
    print(f"\nArranques que llegan al mejor óptimo: {coinciden} de {len(arranques)}")
    print(f"¿El mejor óptimo tiene algún parámetro pegado a la cota? {mejor['en_cota']}")

    print("\nParámetros estimados (CDNOW, calibración):")
    for n in NOMBRES:
        print(f"  {n:>5} = {mejor[n]:.4f}")
    print(f"  log-verosimilitud = {mejor['loglik']:.2f}")

    TABLAS.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([mejor[NOMBRES + ["loglik"]]]).to_csv(TABLAS / "params_cdnow.csv", index=False)
    arranques.to_csv(TABLAS / "ajuste_cdnow_arranques.csv", index=False)
    print("\nGuardado en resultados/tablas/params_cdnow.csv")