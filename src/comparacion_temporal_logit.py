from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss, log_loss

RAIZ = Path(__file__).resolve().parents[1]
PROCESADO = RAIZ / "data" / "procesado"
TABLAS = RAIZ / "resultados" / "tablas"

DIA0 = pd.Timestamp("1997-01-01")
FIN_CAL = pd.Timestamp("1997-09-30")

HORIZONTE = 13.0

CORTE_EVALUACION = (FIN_CAL - DIA0).days / 7

CORTES_ENTRENAMIENTO = [
    CORTE_EVALUACION - 26.0,
    CORTE_EVALUACION - 13.0
]


# Construir una cohorte en una fecha de corte
def construir_cohorte(trans, corte, horizonte):
    cal = trans[trans["semana"] <= corte].copy()
    futuro = trans[
        (trans["semana"] > corte) &
        (trans["semana"] <= corte + horizonte)
    ].copy()

    g = cal.groupby("id")["semana"]

    cohorte = pd.DataFrame({
        "primera": g.min(),
        "ultima": g.max(),
        "n_cal": g.count()
    })

    cohorte["x"] = cohorte["n_cal"] - 1
    cohorte["tx"] = cohorte["ultima"] - cohorte["primera"]
    cohorte["T"] = corte - cohorte["primera"]

    compras_futuras = futuro.groupby("id").size()
    cohorte["Z"] = (
        compras_futuras.reindex(cohorte.index, fill_value=0) > 0
    ).astype(int)

    cohorte["tasa"] = cohorte["x"] / np.maximum(cohorte["T"], 1e-5)
    cohorte["corte"] = corte

    return cohorte.reset_index()


# Preparar variables predictoras
def preparar_X(df):
    return df[["x", "tx", "T", "tasa"]].to_numpy(dtype=float)


# Leer transacciones de CDNOW
trans = pd.read_csv(PROCESADO / "cdnow_trans.csv")

assert {"id", "semana"}.issubset(trans.columns)
assert trans["semana"].notna().all()

print("=== COMPARACIÓN TEMPORAL CORREGIDA ===")
print("Transacciones:", len(trans))
print("Clientes:", trans["id"].nunique())

# Crear conjuntos históricos de entrenamiento
historicos = [
    construir_cohorte(trans, corte, HORIZONTE)
    for corte in CORTES_ENTRENAMIENTO
]

entrenamiento = pd.concat(historicos, ignore_index=True)

# Crear conjunto de evaluación futura
evaluacion = construir_cohorte(
    trans, CORTE_EVALUACION, HORIZONTE
)

# Comprobar que no se utilicen etiquetas posteriores a la semana 39
assert all(
    corte + HORIZONTE <= CORTE_EVALUACION
    for corte in CORTES_ENTRENAMIENTO
)

X_train = preparar_X(entrenamiento)
y_train = entrenamiento["Z"].to_numpy(dtype=int)

X_test = preparar_X(evaluacion)
y_test = evaluacion["Z"].to_numpy(dtype=int)

assert len(np.unique(y_train)) == 2
assert len(np.unique(y_test)) == 2

# Entrenar regresión logística solo con información histórica
modelo = LogisticRegression(
    solver="lbfgs",
    max_iter=1000,
    random_state=42
)

modelo.fit(X_train, y_train)

# Evaluar únicamente en el período futuro
p_logit = modelo.predict_proba(X_test)[:, 1]

# Calcular métricas
auc_logit = roc_auc_score(y_test, p_logit)
brier_logit = brier_score_loss(y_test, p_logit)
logloss_logit = log_loss(y_test, p_logit)

print("\n=== ENTRENAMIENTO HISTÓRICO ===")
print("Cortes utilizados:", CORTES_ENTRENAMIENTO)
print("Observaciones:", len(entrenamiento))
print("Clientes distintos:", entrenamiento["id"].nunique())

print("\n=== EVALUACIÓN FUTURA ===")
print("Corte:", CORTE_EVALUACION)
print("Horizonte:", HORIZONTE)
print("Clientes:", len(evaluacion))
print("Clientes que compraron:", y_test.sum())
print(f"Tasa real: {y_test.mean():.4f}")

print("\n=== RESULTADOS LOGÍSTICA ===")
print(f"AUC: {auc_logit:.4f}")
print(f"Brier: {brier_logit:.4f}")
print(f"Log-Loss: {logloss_logit:.4f}")

# Guardar resultados
TABLAS.mkdir(parents=True, exist_ok=True)

pd.DataFrame([{
    "modelo": "Logistica temporal",
    "horizonte_semanas": HORIZONTE,
    "clientes_evaluacion": len(evaluacion),
    "tasa_real": y_test.mean(),
    "auc": auc_logit,
    "brier": brier_logit,
    "logloss": logloss_logit
}]).to_csv(
    TABLAS / "logistica_temporal_logit.csv",
    index=False
)

evaluacion[["id", "x", "tx", "T", "Z"]].assign(
    p_logit=p_logit
).to_csv(
    TABLAS / "predicciones_logistica_temporal.csv",
    index=False
)

print("\nArchivos guardados en resultados/tablas/")