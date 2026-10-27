from pathlib import Path

import numpy as np
import pandas as pd

from bgnbd import loglik

RAIZ = Path(__file__).resolve().parents[1]
TABLAS = RAIZ / "resultados" / "tablas"
NOMBRES = ["r", "alpha", "a", "b"]

# Valores reportados en el artículo (redondeados a 3 decimales)
ARTICULO = {"r": 0.243, "alpha": 4.414, "a": 0.793, "b": 2.426}
LL_ARTICULO = -9582.4

if __name__ == "__main__":
    nuestros = pd.read_csv(TABLAS / "params_cdnow.csv").iloc[0]
    rfm = pd.read_csv(RAIZ / "data" / "procesado" / "cdnow_rfm.csv")
    x, tx, T = rfm["x"].values, rfm["tx"].values, rfm["T"].values

    # 1. Parámetros: diferencia absoluta, relativa y comparación al mismo redondeo
    tabla = pd.DataFrame({
        "parametro": NOMBRES,
        "nuestro": [nuestros[n] for n in NOMBRES],
        "articulo": [ARTICULO[n] for n in NOMBRES],
    })
    tabla["diferencia"] = tabla["nuestro"] - tabla["articulo"]
    tabla["dif_relativa_%"] = 100 * tabla["diferencia"] / tabla["articulo"]
    tabla["nuestro_3_dec"] = tabla["nuestro"].round(3)
    tabla["coincide_3_dec"] = np.isclose(tabla["nuestro_3_dec"], tabla["articulo"])

    print("Comparación de parámetros:")
    print(tabla.round(5).to_string(index=False))

    # 2. Log-verosimilitud
    ll_nuestro = nuestros["loglik"]
    ll_en_params_articulo = loglik([ARTICULO[n] for n in NOMBRES], x, tx, T)
    print(f"\nLog-verosimilitud en nuestro óptimo:                  {ll_nuestro:.4f}")
    print(f"Log-verosimilitud reportada en el artículo:           {LL_ARTICULO:.1f}")
    print(f"Nuestra loglik evaluada en los parámetros del artículo: {ll_en_params_articulo:.4f}")
    print(f"Diferencia (nuestro óptimo − parámetros del artículo):  "
          f"{ll_nuestro - ll_en_params_articulo:.4f}")

    # 3. Medias implicadas (las usará D5.T3)
    print(f"\nTasa media r/α:       nuestra = {nuestros['r'] / nuestros['alpha']:.4f} | "
          f"artículo = {ARTICULO['r'] / ARTICULO['alpha']:.4f}")
    print(f"Prob. media a/(a+b):  nuestra = {nuestros['a'] / (nuestros['a'] + nuestros['b']):.4f} | "
          f"artículo = {ARTICULO['a'] / (ARTICULO['a'] + ARTICULO['b']):.4f}")

    tabla.to_csv(TABLAS / "comparacion_articulo.csv", index=False)
    print("\nGuardado en resultados/tablas/comparacion_articulo.csv")