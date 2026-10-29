from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, brier_score_loss

from bgnbd import prob_comprar

RAIZ = Path(__file__).resolve().parents[1]
TABLAS = RAIZ / "resultados" / "tablas"
PROCESADO = RAIZ / "data" / "procesado"

NOMBRES = ["r", "alpha", "a", "b"]
TAU = 13.0

# Leer predicciones de la regresión logística temporal
df = pd.read_csv(
    TABLAS / "predicciones_logistica_temporal.csv"
)

# Leer parámetros BG/NBD ajustados con CDNOW
params = (
    pd.read_csv(TABLAS / "params_cdnow.csv")
    .iloc[0][NOMBRES]
    .to_numpy(dtype=float)
)

# Verificar que la evaluación corresponde al mismo corte
rfm = pd.read_csv(PROCESADO / "cdnow_rfm.csv")

assert len(df) == len(rfm), "Los conjuntos tienen tamaños diferentes"
assert df["id"].is_unique, "Existen clientes duplicados"
assert set(df["id"]) == set(rfm["id"]), "Los clientes no coinciden"

comparacion_rfm = df.merge(
    rfm[["id", "x", "tx", "T"]],
    on="id",
    suffixes=("_logit", "_bgnbd"),
    validate="one_to_one"
)

# Comprobar que las variables RFM coinciden
for variable in ["x", "tx", "T"]:
    assert np.allclose(
        comparacion_rfm[f"{variable}_logit"],
        comparacion_rfm[f"{variable}_bgnbd"],
        atol=1e-6
    ), f"La variable {variable} no coincide entre los modelos"

print("Validación RFM correcta: x, tx y T coinciden.")  

# Probabilidad BG/NBD de comprar en 13 semanas
df["p_bgnbd"] = prob_comprar(
    params,
    df["x"].to_numpy(dtype=float),
    df["tx"].to_numpy(dtype=float),
    df["T"].to_numpy(dtype=float),
    TAU
)

assert df["p_bgnbd"].between(0, 1).all()
assert df["p_logit"].between(0, 1).all()

y = df["Z"].to_numpy(dtype=int)

# Comparar modelos sobre las mismas observaciones
resultados = []

for nombre, columna in [
    ("Regresion logistica temporal", "p_logit"),
    ("BG/NBD", "p_bgnbd")
]:
    probabilidades = df[columna].to_numpy(dtype=float)

    resultados.append({
        "modelo": nombre,
        "horizonte_semanas": TAU,
        "clientes": len(df),
        "auc": roc_auc_score(y, probabilidades),
        "brier": brier_score_loss(y, probabilidades),
        "probabilidad_media": probabilidades.mean()
    })

resultados = pd.DataFrame(resultados)

print("=== COMPARACIÓN TEMPORAL: LOGÍSTICA VS BG/NBD ===")
print("Clientes evaluados:", len(df))
print("Compradores reales:", y.sum())
print(f"Tasa real de compra: {y.mean():.4f}")
print("\nResultados:")
print(resultados.round(4).to_string(index=False))

# Guardar resultados
resultados.to_csv(
    TABLAS / "comparacion_logistica_bgnbd.csv",
    index=False
)

df[[
    "id", "x", "tx", "T", "Z", "p_logit", "p_bgnbd"
]].to_csv(
    TABLAS / "predicciones_comparacion_logistica_bgnbd.csv",
    index=False
)

print("\nArchivos guardados en resultados/tablas/")
