from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from bgnbd import compras_esperadas

RAIZ = Path(__file__).resolve().parents[1]
TABLAS = RAIZ / "resultados" / "tablas"
GRAFICAS = RAIZ / "resultados" / "graficas"
NOMBRES = ["r", "alpha", "a", "b"]
SEMANAS = np.arange(1, 79)   # semanas 1 a 78
FIN_CAL = 39                 # la semana 39 es la última de calibración

if __name__ == "__main__":
    params = pd.read_csv(TABLAS / "params_cdnow.csv").iloc[0][NOMBRES].values
    rfm = pd.read_csv(RAIZ / "data" / "procesado" / "cdnow_rfm.csv")
    trans = pd.read_csv(RAIZ / "data" / "procesado" / "cdnow_trans.csv", parse_dates=["fecha"])

    # Curva esperada (bottom-up)
    # Matriz clientes x semanas con el tiempo transcurrido desde la primera compra
    s = rfm["semana_primera"].values[:, None]          # (2357, 1)
    t = SEMANAS[None, :] - s                            # (2357, 78); negativo si aún no llega
    esperada_acum = compras_esperadas(params, t).sum(axis=0)

    # Curva real
    # Compras repetidas = todas las transacciones menos la primera de cada cliente
    primera = trans.groupby("id")["fecha"].transform("min")
    repetidas = trans[trans["fecha"] > primera]
    # Al final de la semana w cuentan las compras con semana < w (días 0 a 7w - 1)
    real_acum = np.array([(repetidas["semana"] < w).sum() for w in SEMANAS])

    curva = pd.DataFrame({
        "semana": SEMANAS,
        "esperada_acum": esperada_acum,
        "real_acum": real_acum,
        "esperada_semanal": np.diff(esperada_acum, prepend=0.0),
        "real_semanal": np.diff(real_acum, prepend=0),
    })

    # Total del holdout
    esp_hold = esperada_acum[-1] - esperada_acum[FIN_CAL - 1]
    real_hold = real_acum[-1] - real_acum[FIN_CAL - 1]
    error_pct = 100 * (esp_hold - real_hold) / real_hold

    print(f"Compras repetidas acumuladas en la semana 39: esperadas = {esperada_acum[FIN_CAL - 1]:.1f}, "
          f"reales = {real_acum[FIN_CAL - 1]}")
    print(f"Compras repetidas acumuladas en la semana 78: esperadas = {esperada_acum[-1]:.1f}, "
          f"reales = {real_acum[-1]}")
    print(f"\nTotal del holdout (semanas 40-78): pronóstico = {esp_hold:.1f}, real = {real_hold}, "
          f"error = {error_pct:+.2f} %")
    mae = np.abs(curva["esperada_semanal"] - curva["real_semanal"])[FIN_CAL:].mean()
    print(f"MAE semanal en el holdout: {mae:.2f} compras por semana")

    TABLAS.mkdir(parents=True, exist_ok=True)
    curva.to_csv(TABLAS / "curva_bottom_up.csv", index=False)

    # Gráfica
    GRAFICAS.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(SEMANAS, real_acum, color="black", lw=2, label="Real")
    ax.plot(SEMANAS, esperada_acum, color="#c0392b", lw=2, ls="--", label="BG/NBD (bottom-up)")
    ax.axvline(FIN_CAL, color="gray", ls=":", lw=1.5)
    ax.text(FIN_CAL - 1, ax.get_ylim()[1] * 0.95, "fin de calibración",
            ha="right", va="top", color="gray")
    ax.set_xlabel("Semana (desde el 1 de enero de 1997)")
    ax.set_ylabel("Compras repetidas acumuladas")
    ax.set_title("CDNOW: compras repetidas acumuladas de la cohorte")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(GRAFICAS / "curva_bottom_up.png", dpi=150)
    print("\nGuardado en resultados/tablas/curva_bottom_up.csv y resultados/graficas/curva_bottom_up.png")