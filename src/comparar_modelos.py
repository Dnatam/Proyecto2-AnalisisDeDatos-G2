from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import brier_score_loss, roc_auc_score, roc_curve

import bgnbd
import mbgnbd

RAIZ = Path(__file__).resolve().parents[1]
TABLAS = RAIZ / "resultados" / "tablas"
GRAFICAS = RAIZ / "resultados" / "graficas"
NOMBRES = ["r", "alpha", "a", "b"]
SEMANAS = np.arange(1, 79)
FIN_CAL = 39


def total_holdout(modulo, params, semana_primera):
    """Total de compras repetidas pronosticado para las semanas 40-78 (bottom-up)."""
    acum = modulo.compras_esperadas(params, SEMANAS[None, :] - semana_primera[:, None]).sum(axis=0)
    return acum[-1] - acum[FIN_CAL - 1]


if __name__ == "__main__":
    p_bg = pd.read_csv(TABLAS / "params_cdnow.csv").iloc[0]
    p_mbg = pd.read_csv(TABLAS / "params_mbgnbd_cdnow.csv").iloc[0]
    bg = pd.read_csv(TABLAS / "prob_compra.csv")
    mbg = pd.read_csv(TABLAS / "predicciones_mbgnbd_cdnow.csv")
    rfm = pd.read_csv(RAIZ / "data" / "procesado" / "cdnow_rfm.csv")

    # Las tres tablas deben estar en el mismo orden de clientes
    assert (bg["id"].values == mbg["id"].values).all() and (bg["id"].values == rfm["id"].values).all()

    y = bg["Z"].values
    sin_rep = bg["x"].values == 0
    real = rfm["x_star"].sum()

    filas = []
    for nombre, modulo, params, pv, pz in [
        ("BG/NBD", bgnbd, p_bg, bg["p_vivo"], bg["p_compra"]),
        ("MBG/NBD", mbgnbd, p_mbg, mbg["p_vivo_mbg"], mbg["p_compra_mbg"]),
    ]:
        total = total_holdout(modulo, params[NOMBRES].values.astype(float),
                              rfm["semana_primera"].values)
        filas.append({
            "modelo": nombre,
            "loglik": params["loglik"],
            "p_vivo_x0_prom": pv[sin_rep].mean(),
            "auc_p_vivo": roc_auc_score(y, pv),
            "auc_p_compra": roc_auc_score(y, pz),
            "brier_p_compra": brier_score_loss(y, pz),
            "p_compra_prom": pz.mean(),
            "total_holdout": total,
            "error_total_%": 100 * (total - real) / real,
        })
    tabla = pd.DataFrame(filas)

    print(f"Tasa base: {y.mean():.4f} | Compras reales en el holdout: {real}")
    print(f"Brier de predecir la tasa base a todos: {brier_score_loss(y, np.full(len(y), y.mean())):.4f}\n")
    print(tabla.round(4).T.to_string(header=False))

    # ¿Elegirían a los mismos clientes para una promoción?
    rho = spearmanr(bg["p_compra"], mbg["p_compra_mbg"]).correlation
    k = int(0.2 * len(bg))
    top_bg = set(bg.nlargest(k, "p_compra")["id"])
    top_mbg = set(mbg.nlargest(k, "p_compra_mbg")["id"])
    coincidencia = len(top_bg & top_mbg) / k
    print(f"\nCorrelación de Spearman entre los P(Z = 1) de ambos modelos: {rho:.4f}")
    print(f"Clientes en común en el 20 % con mayor P(Z = 1): {coincidencia:.1%} ({len(top_bg & top_mbg)} de {k})")

    TABLAS.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(TABLAS / "comparacion_bg_mbg.csv", index=False)

    # Gráfica: ROC de P(vivo) y de P(Z = 1) para ambos modelos
    GRAFICAS.mkdir(parents=True, exist_ok=True)
    fig, ejes = plt.subplots(1, 2, figsize=(12, 5.2))
    for ax, (titulo, col_bg, col_mbg) in zip(ejes, [
        ("P(vivo)", bg["p_vivo"], mbg["p_vivo_mbg"]),
        ("P(Z = 1)", bg["p_compra"], mbg["p_compra_mbg"]),
    ]):
        for nombre, score, color in [("BG/NBD", col_bg, "#c0392b"), ("MBG/NBD", col_mbg, "#2471a3")]:
            fpr, tpr, _ = roc_curve(y, score)
            ax.plot(fpr, tpr, color=color, lw=2,
                    label=f"{nombre} (AUC = {roc_auc_score(y, score):.3f})")
        ax.plot([0, 1], [0, 1], ls="--", color="gray", label="Azar (AUC = 0.500)")
        ax.set_title(f"ROC de {titulo} como clasificador de Z")
        ax.set_xlabel("Tasa de falsos positivos")
        ax.set_ylabel("Tasa de verdaderos positivos")
        ax.legend(loc="lower right")
        ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(GRAFICAS / "roc_bg_mbg.png", dpi=150)
    print("\nGuardado en resultados/tablas/comparacion_bg_mbg.csv y resultados/graficas/roc_bg_mbg.png")