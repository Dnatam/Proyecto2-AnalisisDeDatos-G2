from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.metrics import (
    roc_auc_score,
    roc_curve,
    brier_score_loss
)

RAIZ = Path(__file__).resolve().parents[1]
TABLAS = RAIZ / "resultados" / "tablas"
GRAFICAS = RAIZ / "resultados" / "graficas"

# Leer resultados de la probabilidad de compra
df = pd.read_csv(TABLAS / "prob_compra.csv")

columnas = ["id", "x", "tx", "T", "x_star", "Z", "p_compra"]
assert not df[columnas].isna().any().any(), "Existen valores faltantes"
assert df["Z"].isin([0, 1]).all(), "Z debe ser binaria"
assert df["p_compra"].between(0, 1).all(), "Probabilidades fuera de rango"
assert (df["tx"] <= df["T"]).all(), "Recencia mayor que T"

# Variable real y probabilidades del modelo
y = df["Z"].to_numpy(dtype=int)
p_bgnbd = df["p_compra"].to_numpy(dtype=float)

# Métodos de referencia
# Recencia: menor tiempo desde última compra implica mayor puntuación
df["tiempo_sin_comprar"] = df["T"] - df["tx"]
df["score_recencia"] = -df["tiempo_sin_comprar"]

# Frecuencia: mayor cantidad de compras repetidas implica mayor puntuación
df["score_frecuencia"] = df["x"]

# Tasa base: misma probabilidad para todos
tasa_base = y.mean()
p_base = np.full(len(df), tasa_base)

modelos = {
    "BG/NBD": p_bgnbd,
    "Recencia": df["score_recencia"].to_numpy(),
    "Frecuencia": df["score_frecuencia"].to_numpy(),
    "Tasa base": p_base
}

print("=== EVALUACIÓN DE PROBABILIDAD DE COMPRA ===")
print("Clientes:", len(df))
print("Clientes que compraron:", y.sum())
print(f"Tasa base: {tasa_base:.4f}")

# Calcular AUC y Brier
resultados = []

for nombre, score in modelos.items():
    auc = roc_auc_score(y, score)

    # Brier solo para probabilidades, no para puntuaciones arbitrarias
    brier = (
        brier_score_loss(y, score)
        if nombre in ["BG/NBD", "Tasa base"]
        else np.nan
    )

    resultados.append({
        "metodo": nombre,
        "auc": auc,
        "brier": brier
    })

comparacion = pd.DataFrame(resultados)

print("\n=== COMPARACIÓN DE MÉTODOS ===")
print(comparacion.round(4).to_string(index=False))

brier_modelo = brier_score_loss(y, p_bgnbd)
brier_base = brier_score_loss(y, p_base)
mejora = 1 - brier_modelo / brier_base

print(f"\nMejora relativa de Brier frente a tasa base: {mejora:.2%}")

# Calibración por grupos de probabilidad
# Se usan intervalos fijos de amplitud 0.1
limites = np.linspace(0, 1, 11)

df["intervalo"] = pd.cut(
    df["p_compra"],
    bins=limites,
    include_lowest=True
)

calibracion = (
    df.groupby("intervalo", observed=False)
    .agg(
        clientes=("Z", "size"),
        probabilidad_media=("p_compra", "mean"),
        frecuencia_real=("Z", "mean")
    )
    .reset_index()
)

calibracion = calibracion[calibracion["clientes"] > 0].copy()
calibracion["intervalo"] = calibracion["intervalo"].astype(str)

print("\n=== CALIBRACIÓN ===")
print(calibracion.round(4).to_string(index=False))

# Guardar tablas
TABLAS.mkdir(parents=True, exist_ok=True)
GRAFICAS.mkdir(parents=True, exist_ok=True)

comparacion.to_csv(
    TABLAS / "evaluacion_prob_compra.csv",
    index=False
)

calibracion.to_csv(
    TABLAS / "calibracion_prob_compra.csv",
    index=False
)

# Gráfica ROC
plt.figure(figsize=(7, 5.5))

for nombre, score in modelos.items():
    if nombre == "Tasa base":
        continue

    fpr, tpr, _ = roc_curve(y, score)
    auc = roc_auc_score(y, score)

    plt.plot(
        fpr, tpr,
        label=f"{nombre} (AUC = {auc:.3f})"
    )

plt.plot(
    [0, 1], [0, 1],
    linestyle="--",
    color="gray",
    label="Azar (AUC = 0.500)"
)

plt.xlabel("Tasa de falsos positivos")
plt.ylabel("Tasa de verdaderos positivos")
plt.title("CDNOW: comparación de curvas ROC")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(
    GRAFICAS / "roc_comparacion_compra.png",
    dpi=150
)
plt.close()

# Gráfica de calibración
plt.figure(figsize=(7, 5.5))

plt.plot(
    [0, 1], [0, 1],
    linestyle="--",
    color="gray",
    label="Calibración perfecta"
)

plt.plot(
    calibracion["probabilidad_media"],
    calibracion["frecuencia_real"],
    marker="o",
    label="BG/NBD"
)

plt.xlabel("Probabilidad media estimada")
plt.ylabel("Fracción real que compró")
plt.title("CDNOW: calibración de P(Z = 1)")
plt.xlim(0, 1)
plt.ylim(0, 1)
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(
    GRAFICAS / "calibracion_prob_compra.png",
    dpi=150
)
plt.close()

print("\n=== ARCHIVOS GUARDADOS ===")
print("resultados/tablas/evaluacion_prob_compra.csv")
print("resultados/tablas/calibracion_prob_compra.csv")
print("resultados/graficas/roc_comparacion_compra.png")
print("resultados/graficas/calibracion_prob_compra.png")
print("\nEvaluación finalizada correctamente.")