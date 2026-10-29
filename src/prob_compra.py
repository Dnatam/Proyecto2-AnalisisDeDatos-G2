from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from bgnbd import prob_comprar, prob_vivo

RAIZ = Path(__file__).resolve().parents[1]
TABLAS = RAIZ / "resultados" / "tablas"
GRAFICAS = RAIZ / "resultados" / "graficas"
NOMBRES = ["r", "alpha", "a", "b"]
TAU = 39

if __name__ == "__main__":
    params = pd.read_csv(TABLAS / "params_cdnow.csv").iloc[0][NOMBRES].values
    rfm = pd.read_csv(RAIZ / "data" / "procesado" / "cdnow_rfm.csv")
    x, tx, T = rfm["x"], rfm["tx"], rfm["T"]

    rfm["p_vivo"] = prob_vivo(params, x, tx, T)
    rfm["p_compra"] = prob_comprar(params, x, tx, T, TAU)
    rfm["Z"] = (rfm["x_star"] >= 1).astype(int)

    print(f"Tasa base (fracción que compró en el holdout): {rfm['Z'].mean():.4f}")
    print(f"Promedio de P(vivo):  {rfm['p_vivo'].mean():.4f}")
    print(f"Promedio de P(Z = 1): {rfm['p_compra'].mean():.4f}")

    print("\nPor grupo de frecuencia en calibración:")
    rfm["grupo"] = np.where(rfm["x"] >= 7, "7+", rfm["x"].astype(str))
    orden = [str(i) for i in range(7)] + ["7+"]
    resumen = (rfm.groupby("grupo")
                  .agg(clientes=("id", "size"),
                       p_vivo=("p_vivo", "mean"),
                       p_compra=("p_compra", "mean"),
                       tasa_real=("Z", "mean"))
                  .reindex(orden))
    print(resumen.round(4).to_string())

    TABLAS.mkdir(parents=True, exist_ok=True)
    rfm[["id", "x", "tx", "T", "x_star", "Z", "p_vivo", "p_compra"]].to_csv(
        TABLAS / "prob_compra.csv", index=False)

    # Gráfica: P(vivo) contra P(Z = 1)
    GRAFICAS.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.5, 6))
    sc = ax.scatter(rfm["p_vivo"], rfm["p_compra"], c=np.minimum(rfm["x"], 10),
                    cmap="viridis", s=12, alpha=0.7)
    ax.plot([0, 1], [0, 1], ls="--", color="gray", lw=1, label="P(Z = 1) = P(vivo)")
    ax.set_xlabel("P(vivo) al final de la calibración")
    ax.set_ylabel("P(Z = 1): comprar al menos una vez en 39 semanas")
    ax.set_title("CDNOW: estar vivo no es lo mismo que comprar")
    fig.colorbar(sc, ax=ax, label="x en calibración (10 = 10 o más)")
    ax.legend(loc="upper left")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(GRAFICAS / "pvivo_vs_pz.png", dpi=150)
    print("\nGuardado en resultados/tablas/prob_compra.csv y resultados/graficas/pvivo_vs_pz.png")