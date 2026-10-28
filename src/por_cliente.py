from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from bgnbd import compras_condicionales

RAIZ = Path(__file__).resolve().parents[1]
TABLAS = RAIZ / "resultados" / "tablas"
GRAFICAS = RAIZ / "resultados" / "graficas"
NOMBRES = ["r", "alpha", "a", "b"]
TAU = 39 

if __name__ == "__main__":
    params = pd.read_csv(TABLAS / "params_cdnow.csv").iloc[0][NOMBRES].values
    rfm = pd.read_csv(RAIZ / "data" / "procesado" / "cdnow_rfm.csv")

    rfm["esperado"] = compras_condicionales(params, rfm["x"], rfm["tx"], rfm["T"], TAU)
    rfm["grupo"] = np.where(rfm["x"] >= 7, "7+", rfm["x"].astype(str))

    orden = [str(i) for i in range(7)] + ["7+"]
    tabla = (rfm.groupby("grupo")
                .agg(clientes=("id", "size"),
                     esperado_prom=("esperado", "mean"),
                     real_prom=("x_star", "mean"))
                .reindex(orden)
                .reset_index())
    tabla["diferencia"] = tabla["esperado_prom"] - tabla["real_prom"]
    tabla["error_%"] = 100 * tabla["diferencia"] / tabla["real_prom"]

    print("Promedio de compras en el holdout por grupo de frecuencia en calibración:")
    print(tabla.round(3).to_string(index=False))
    print(f"\nTotal pronosticado (suma de E[Y(39)]): {rfm['esperado'].sum():.1f} | "
          f"real: {rfm['x_star'].sum()}")

    TABLAS.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(TABLAS / "pronostico_por_frecuencia.csv", index=False)

    GRAFICAS.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    pos = np.arange(len(orden))
    ax.plot(pos, tabla["real_prom"], "o-", color="black", lw=2, label="Real (promedio de x*)")
    ax.plot(pos, tabla["esperado_prom"], "s--", color="#c0392b", lw=2,
            label="BG/NBD (promedio de E[Y(39)])")
    ax.set_xticks(pos, orden)
    ax.set_xlabel("Compras repetidas en calibración (x)")
    ax.set_ylabel("Compras promedio en el holdout (39 semanas)")
    ax.set_title("CDNOW: pronóstico condicional por grupo de frecuencia")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(GRAFICAS / "pronostico_por_frecuencia.png", dpi=150)
    print("\nGuardado en resultados/tablas/pronostico_por_frecuencia.csv y "
          "resultados/graficas/pronostico_por_frecuencia.png")