import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from bgnbd import prob_comprar

warnings.filterwarnings("ignore", message="Setting penalty=None")

RAIZ = Path(__file__).resolve().parents[1]
TABLAS = RAIZ / "resultados" / "tablas"
GRAFICAS = RAIZ / "resultados" / "graficas"
NOMBRES = ["r", "alpha", "a", "b"]
FIN_CAL = 39            # la calibración termina en la semana 39
N_SEMILLAS = 20


def logistica():
    """Modelo de 6.1: x, tx, T estandarizados y sin penalización."""
    return make_pipeline(StandardScaler(), LogisticRegression(C=np.inf, max_iter=1000))


def prediccion_fuera_de_muestra(X, y, n_semillas=N_SEMILLAS):
    """Promedio de las predicciones fuera de muestra de 5 folds en varias semillas."""
    pred = np.zeros(len(y))
    for semilla in range(n_semillas):
        folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=semilla)
        for entreno, prueba in folds.split(X, y):
            modelo = logistica().fit(X[entreno], y[entreno])
            pred[prueba] += modelo.predict_proba(X[prueba])[:, 1]
    return pred / n_semillas


def calibracion_deciles(p, z):
    """Probabilidad media y fracción real por decil de probabilidad."""
    decil = pd.qcut(pd.Series(p).rank(method="first"), 10, labels=False) + 1
    return (pd.DataFrame({"decil": decil, "p": p, "z": z})
              .groupby("decil")
              .agg(prob_media=("p", "mean"), fraccion_real=("z", "mean")))


if __name__ == "__main__":
    rfm = pd.read_csv(RAIZ / "data" / "procesado" / "cdnow_rfm.csv")
    trans = pd.read_csv(RAIZ / "data" / "procesado" / "cdnow_trans.csv")
    params = pd.read_csv(TABLAS / "params_cdnow.csv").iloc[0][NOMBRES].values.astype(float)

    # Etiquetas: compra en las 39 semanas del holdout y en las primeras 13
    z39 = (rfm["x_star"] >= 1).astype(int).values
    en_13 = trans[(trans["semana"] >= FIN_CAL) & (trans["semana"] < FIN_CAL + 13)]
    z13 = rfm["id"].isin(en_13["id"]).astype(int).values

    X = rfm[["x", "tx", "T"]].values
    x, tx, T = rfm["x"].values, rfm["tx"].values, rfm["T"].values

    p_logit = prediccion_fuera_de_muestra(X, z39)          # entrenada con Z de 39 semanas
    p_bg39 = prob_comprar(params, x, tx, T, 39)
    p_bg13 = prob_comprar(params, x, tx, T, 13)            # solo cambia τ

    print(f"Tasa real de compra en 39 semanas: {z39.mean():.4f}")
    print(f"Tasa real de compra en 13 semanas: {z13.mean():.4f}\n")

    filas = []
    for horizonte, z, modelos in [
        (39, z39, [("Logística (Z de 39 semanas)", p_logit), ("BG/NBD, τ = 39", p_bg39)]),
        (13, z13, [("Logística tal cual (Z de 39 semanas)", p_logit), ("BG/NBD, τ = 13", p_bg13)]),
    ]:
        for nombre, p in modelos:
            filas.append({
                "horizonte": horizonte,
                "modelo": nombre,
                "prob_media": p.mean(),
                "tasa_real": z.mean(),
                "auc": roc_auc_score(z, p),
                "brier": brier_score_loss(z, p),
                "brier_tasa_base": brier_score_loss(z, np.full(len(z), z.mean())),
            })
    metricas = pd.DataFrame(filas)
    print(metricas.round(4).to_string(index=False))

    calib = pd.concat({
        "logistica": calibracion_deciles(p_logit, z13),
        "bgnbd_tau13": calibracion_deciles(p_bg13, z13),
    }, axis=1)
    print("\nCalibración por deciles para el horizonte de 13 semanas:")
    print(calib.round(3).to_string())

    TABLAS.mkdir(parents=True, exist_ok=True)
    metricas.to_csv(TABLAS / "cambio_horizonte_metricas.csv", index=False)
    calib.to_csv(TABLAS / "cambio_horizonte_calibracion.csv")

    GRAFICAS.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.5, 6))
    ax.plot([0, 1], [0, 1], ls="--", color="gray", label="Calibración perfecta")
    ax.plot(calib["logistica"]["prob_media"], calib["logistica"]["fraccion_real"], "o-",
            color="#7d3c98", lw=2, label="Logística de 6.1 tal cual")
    ax.plot(calib["bgnbd_tau13"]["prob_media"], calib["bgnbd_tau13"]["fraccion_real"], "s-",
            color="#c0392b", lw=2, label="BG/NBD con τ = 13")
    ax.set_xlabel("Probabilidad media predicha (por decil)")
    ax.set_ylabel("Fracción real que compró en 13 semanas")
    ax.set_title("CDNOW: calibración para el horizonte de 13 semanas")
    lim = max(calib.xs("prob_media", axis=1, level=1).max().max(), 0.8) + 0.05
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    ax.legend(loc="upper left")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(GRAFICAS / "cambio_horizonte_calibracion.png", dpi=150)
    print("\nGuardado en resultados/tablas/cambio_horizonte_*.csv y "
          "resultados/graficas/cambio_horizonte_calibracion.png")