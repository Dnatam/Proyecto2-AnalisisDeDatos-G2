from pathlib import Path

import numpy as np
import pandas as pd

import mbgnbd
from ajuste_cdnow import NOMBRES, ajustar

RAIZ = Path(__file__).resolve().parents[1]
TABLAS = RAIZ / "resultados" / "tablas"
TAU = 39
SEMANAS = np.arange(1, 79)
FIN_CAL = 39

if __name__ == "__main__":
    rfm = pd.read_csv(RAIZ / "data" / "procesado" / "cdnow_rfm.csv")
    x, tx, T = rfm["x"].values, rfm["tx"].values, rfm["T"].values

    # Ajuste por máxima verosimilitud (mismo optimizador que el BG/NBD)
    mejor, arranques = ajustar(x, tx, T, funcion_loglik=mbgnbd.loglik)
    params = mejor[NOMBRES].values.astype(float)

    print("Resultado de cada punto inicial:")
    print(arranques.round(4).to_string(index=False))
    coinciden = (np.abs(arranques["loglik"] - mejor["loglik"]) < 1e-2).sum()
    print(f"\nArranques que llegan al mejor óptimo: {coinciden} de {len(arranques)}")
    print(f"¿El mejor óptimo tiene algún parámetro pegado a la cota? {mejor['en_cota']}")

    print("\nParámetros estimados del MBG/NBD (CDNOW, calibración):")
    for n in NOMBRES:
        print(f"  {n:>5} = {mejor[n]:.4f}")
    print(f"  log-verosimilitud = {mejor['loglik']:.2f}")
    print(f"  probabilidad media de morir tras una compra a/(a+b) = "
          f"{mejor['a'] / (mejor['a'] + mejor['b']):.4f}")

    # Predicciones por cliente
    rfm["p_vivo_mbg"] = mbgnbd.prob_vivo(params, x, tx, T)
    rfm["p_compra_mbg"] = mbgnbd.prob_comprar(params, x, tx, T, TAU)
    rfm["esperado_mbg"] = mbgnbd.compras_condicionales(params, x, tx, T, TAU)

    sin_rep = rfm["x"] == 0
    print(f"\nP(vivo) de los clientes con x = 0: promedio = {rfm.loc[sin_rep, 'p_vivo_mbg'].mean():.4f}, "
          f"rango = [{rfm.loc[sin_rep, 'p_vivo_mbg'].min():.4f}, {rfm.loc[sin_rep, 'p_vivo_mbg'].max():.4f}]")

    # Total del holdout: bottom-up con E[X(t)] y suma de E[Y(39)]
    s = rfm["semana_primera"].values[:, None]
    acum = mbgnbd.compras_esperadas(params, SEMANAS[None, :] - s).sum(axis=0)
    total_bottom_up = acum[-1] - acum[FIN_CAL - 1]
    real = rfm["x_star"].sum()
    print(f"\nTotal del holdout (bottom-up con E[X(t)]): {total_bottom_up:.1f} | real: {real} | "
          f"error = {100 * (total_bottom_up - real) / real:+.2f} %")
    print(f"Total del holdout (suma de E[Y(39)]):      {rfm['esperado_mbg'].sum():.1f}")

    # Guardar
    TABLAS.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([mejor[NOMBRES + ["loglik"]]]).to_csv(TABLAS / "params_mbgnbd_cdnow.csv", index=False)
    arranques.to_csv(TABLAS / "ajuste_mbgnbd_arranques.csv", index=False)
    rfm[["id", "x", "tx", "T", "x_star", "p_vivo_mbg", "p_compra_mbg", "esperado_mbg"]].to_csv(
        TABLAS / "predicciones_mbgnbd_cdnow.csv", index=False)
    print("\nGuardado en resultados/tablas/params_mbgnbd_cdnow.csv y predicciones_mbgnbd_cdnow.csv")