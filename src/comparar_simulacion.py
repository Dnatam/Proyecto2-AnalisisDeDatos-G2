from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
TABLAS = RAIZ / "resultados" / "tablas"
GRAFICAS = RAIZ / "resultados" / "graficas"

VERDADEROS = {"r": 0.25, "alpha": 4.0, "a": 0.8, "b": 2.5}
ETIQUETAS = {"r": "r", "alpha": r"$\alpha$", "a": "a", "b": "b"}


def tabla_comparacion(est):
    """Sesgo, dispersión y error de cada parámetro a lo largo de las semillas."""
    filas = []
    for p, v in VERDADEROS.items():
        media = est[p].mean()
        desv = est[p].std(ddof=1)
        filas.append({
            "parametro": p,
            "verdadero": v,
            "media": media,
            "desv_est": desv,
            "sesgo": media - v,
            "sesgo_rel_%": 100 * (media - v) / v,
            "cv_%": 100 * desv / media,                     
            "rmse": ((est[p] - v) ** 2).mean() ** 0.5,
            "minimo": est[p].min(),
            "maximo": est[p].max(),
        })
    return pd.DataFrame(filas)


def grafica(est, ruta):
    """Histograma de los estimados de cada parámetro con el valor verdadero."""
    fig, ejes = plt.subplots(1, 4, figsize=(14, 3.6))
    for ax, (p, v) in zip(ejes, VERDADEROS.items()):
        ax.hist(est[p], bins=10, color="#7aa6c2", edgecolor="white")
        ax.axvline(v, color="crimson", lw=2, label="verdadero")
        ax.axvline(est[p].mean(), color="black", ls="--", lw=1.5, label="media estimada")
        ax.set_title(ETIQUETAS[p])
        ax.set_xlabel("estimado")
    ejes[0].set_ylabel("número de semillas")
    ejes[0].legend(fontsize=8)
    fig.suptitle(f"Recuperación de parámetros: {len(est)} semillas de 2,357 clientes simulados")
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)


if __name__ == "__main__":
    est = pd.read_csv(TABLAS / "sim_estimaciones.csv")
    tabla = tabla_comparacion(est)
    print(f"Semillas: {len(est)}\n")
    print(tabla.round(4).to_string(index=False))

    tabla.to_csv(TABLAS / "sim_comparacion.csv", index=False)
    GRAFICAS.mkdir(parents=True, exist_ok=True)
    grafica(est, GRAFICAS / "sim_recuperacion.png")
    print("\nGuardado en resultados/tablas/sim_comparacion.csv y resultados/graficas/sim_recuperacion.png")