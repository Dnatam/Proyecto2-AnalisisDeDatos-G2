from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, roc_auc_score, ConfusionMatrixDisplay

RAIZ = Path(__file__).resolve().parents[1]
TABLAS = RAIZ / "resultados" / "tablas"
GRAFICAS = RAIZ / "resultados" / "graficas"

TABLAS.mkdir(parents=True, exist_ok=True)
GRAFICAS.mkdir(parents=True, exist_ok=True)

# Cargar datos de clientes y parámetros estimados
rfm = pd.read_csv(RAIZ / "data" / "procesado" / "cdnow_rfm.csv")
parametros = pd.read_csv(TABLAS / "params_cdnow.csv").iloc[0]

r = float(parametros["r"])
alpha = float(parametros["alpha"])
a = float(parametros["a"])
b = float(parametros["b"])

# Calcular la probabilidad de que cada cliente siga vivo
def probabilidad_vivo(x, tx, T, r, alpha, a, b):
    x = np.asarray(x, dtype=float)
    tx = np.asarray(tx, dtype=float)
    T = np.asarray(T, dtype=float)

    probabilidades = np.ones_like(x, dtype=float)
    tiene_recompras = x > 0

    x_rep = x[tiene_recompras]
    tx_rep = tx[tiene_recompras]
    T_rep = T[tiene_recompras]

    termino = (a / (b + x_rep - 1)) * (
        (alpha + T_rep) / (alpha + tx_rep)
    ) ** (r + x_rep)

    probabilidades[tiene_recompras] = 1 / (1 + termino)
    return probabilidades

rfm["p_vivo"] = probabilidad_vivo(
    rfm["x"], rfm["tx"], rfm["T"],
    r, alpha, a, b
)

# Verificar las probabilidades
assert rfm["p_vivo"].between(0, 1).all()
assert (rfm.loc[rfm["x"] == 0, "p_vivo"] == 1).all()

# Etiqueta observable: al menos una compra en el holdout
rfm["compro_holdout"] = (rfm["x_star"] > 0).astype(int)

# Clasificación utilizando umbral de 0.5
UMBRAL = 0.5
rfm["prediccion"] = (rfm["p_vivo"] >= UMBRAL).astype(int)

y_real = rfm["compro_holdout"]
y_pred = rfm["prediccion"]
y_score = rfm["p_vivo"]

# Matriz de confusión
matriz = confusion_matrix(y_real, y_pred, labels=[0, 1])

print("=== CLIENTES ACTIVOS - BG/NBD ===")
print(f"Clientes evaluados: {len(rfm)}")
print(f"Compraron en holdout: {y_real.sum()}")
print(f"No compraron en holdout: {(y_real == 0).sum()}")

print("\nProbabilidad de seguir vivo:")
print(rfm["p_vivo"].describe().round(4).to_string())

print("\nMatriz de confusión:")
print(matriz)

print("\nReporte de clasificación:")
print(classification_report(
    y_real, y_pred,
    labels=[0, 1],
    target_names=["Sin compra", "Con compra"],
    zero_division=0
))

# Calcular curva ROC y AUC
fpr, tpr, umbrales = roc_curve(y_real, y_score)
auc = roc_auc_score(y_real, y_score)

print(f"AUC ROC: {auc:.6f}")

# Guardar resultados por cliente
rfm[[
    "id", "x", "tx", "T", "x_star",
    "p_vivo", "compro_holdout", "prediccion"
]].to_csv(TABLAS / "clientes_activos.csv", index=False)

# Graficar matriz de confusión
fig, ax = plt.subplots(figsize=(7, 5))
visualizacion = ConfusionMatrixDisplay(
    confusion_matrix=matriz,
    display_labels=["Sin compra", "Con compra"]
)
visualizacion.plot(ax=ax, cmap="Blues", colorbar=False)
ax.set_title("Matriz de confusión - BG/NBD")
ax.set_xlabel("Predicción")
ax.set_ylabel("Compra observada en holdout")
fig.tight_layout()
fig.savefig(GRAFICAS / "matriz_confusion_clientes.png", dpi=300)
plt.close(fig)

# Graficar curva ROC
fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(fpr, tpr, linewidth=2, label=f"BG/NBD (AUC = {auc:.4f})")
ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Referencia aleatoria")
ax.set_xlabel("Tasa de falsos positivos")
ax.set_ylabel("Tasa de verdaderos positivos")
ax.set_title("Curva ROC - BG/NBD")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(GRAFICAS / "roc_clientes.png", dpi=300)
plt.close(fig)

print("\nArchivos guardados:")
print(TABLAS / "clientes_activos.csv")
print(GRAFICAS / "matriz_confusion_clientes.png")
print(GRAFICAS / "roc_clientes.png")


# Análisis adicional de las probabilidades estimadas

print("\n=== ANÁLISIS ADICIONAL ===")

print("\nProbabilidad media de seguir vivo según compra en holdout:")
print(
    rfm.groupby("compro_holdout")["p_vivo"]
    .agg(["count", "mean", "median"])
    .round(4)
    .to_string()
)

print("\nClientes sin compras repetidas en calibración (x = 0):")
sin_recompras = rfm[rfm["x"] == 0]
print(f"Total: {len(sin_recompras)}")
print(f"Compraron en holdout: {(sin_recompras['x_star'] > 0).sum()}")
print(f"No compraron en holdout: {(sin_recompras['x_star'] == 0).sum()}")

print("\nEvaluación únicamente para clientes con x > 0:")
con_recompras = rfm[rfm["x"] > 0]

if con_recompras["compro_holdout"].nunique() == 2:
    auc_recompras = roc_auc_score(
        con_recompras["compro_holdout"],
        con_recompras["p_vivo"]
    )
    print(f"AUC ROC para x > 0: {auc_recompras:.6f}")

print("\nProporción de clientes con compras en holdout:")
print(f"{rfm['compro_holdout'].mean() * 100:.2f}%")
