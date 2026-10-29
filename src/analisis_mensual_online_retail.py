
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from bgnbd import compras_condicionales

RAIZ = Path(__file__).resolve().parents[1]
DATOS = RAIZ / "data" / "procesado"
TABLAS = RAIZ / "resultados" / "tablas"
GRAFICAS = RAIZ / "resultados" / "graficas"

TABLAS.mkdir(parents=True, exist_ok=True)
GRAFICAS.mkdir(parents=True, exist_ok=True)

INICIO_HOLD = pd.Timestamp("2011-07-01")
FIN_EXCLUSIVO = pd.Timestamp("2011-12-09")

# 1. Cargar datos y parametros
rfm = pd.read_csv(
    DATOS / "online_retail_rfm.csv",
    dtype={"id": str}
)

trans = pd.read_csv(
    DATOS / "online_retail_trans.csv",
    dtype={"id": str},
    parse_dates=["fecha"]
)

p = pd.read_csv(TABLAS / "params_online_retail.csv")
params = tuple(
    float(p.iloc[0][c])
    for c in ["r", "alpha", "a", "b"]
)

# 2. Seleccionar solamente clientes de calibracion
cohorte = set(rfm["id"])

hold = trans[
    (trans["fecha"] >= INICIO_HOLD) &
    (trans["fecha"] < FIN_EXCLUSIVO) &
    (trans["id"].isin(cohorte))
].copy()

# 3. Variables BG/NBD
x = rfm["x"].to_numpy(dtype=float)
tx = rfm["tx"].to_numpy(dtype=float)
T = rfm["T"].to_numpy(dtype=float)

def pronostico_acumulado(fecha):
    tau = (fecha - INICIO_HOLD).days / 7.0

    if tau == 0:
        return 0.0

    esperado = compras_condicionales(
        params, x, tx, T, tau
    )

    if not np.all(np.isfinite(esperado)):
        raise ValueError(
            "El pronostico contiene valores no finitos."
        )

    return float(np.sum(esperado))

# 4. Definir meses del holdout
periodos = [
    ("Julio", "2011-07-01", "2011-08-01"),
    ("Agosto", "2011-08-01", "2011-09-01"),
    ("Septiembre", "2011-09-01", "2011-10-01"),
    ("Octubre", "2011-10-01", "2011-11-01"),
    ("Noviembre", "2011-11-01", "2011-12-01"),
    ("Diciembre (1-8)", "2011-12-01", "2011-12-09")
]

resultados = []

for nombre, inicio_str, fin_str in periodos:
    inicio = pd.Timestamp(inicio_str)
    fin = pd.Timestamp(fin_str)

    real = int(
        ((hold["fecha"] >= inicio) &
         (hold["fecha"] < fin)).sum()
    )

    pred = (
        pronostico_acumulado(fin)
        - pronostico_acumulado(inicio)
    )

    resultados.append({
        "Mes": nombre,
        "Dias": (fin - inicio).days,
        "Real": real,
        "Pronosticado": pred,
        "Diferencia": pred - real,
        "Error_Porcentual": (
            100 * (pred - real) / real
            if real > 0 else np.nan
        )
    })

res = pd.DataFrame(resultados)

# 5. Validar totales
total_real = int(res["Real"].sum())
total_pred = float(res["Pronosticado"].sum())

assert total_real == int(rfm["x_star"].sum()), (
    "Las compras mensuales no coinciden con x_star."
)

pred_directo = pronostico_acumulado(FIN_EXCLUSIVO)

assert np.isclose(
    total_pred, pred_directo, rtol=1e-8, atol=1e-5
), "Los pronosticos mensuales no suman el global."

# 6. Guardar tabla
res.to_csv(
    TABLAS / "online_retail_comparacion_mensual.csv",
    index=False
)

# 7. Grafica de compras reales y pronosticadas
fig, ax = plt.subplots(figsize=(11, 5.5))

pos = np.arange(len(res))
ancho = 0.36

ax.bar(
    pos - ancho / 2,
    res["Real"],
    width=ancho,
    label="Compras reales"
)

ax.bar(
    pos + ancho / 2,
    res["Pronosticado"],
    width=ancho,
    label="BG/NBD"
)

ax.set_xticks(pos)
ax.set_xticklabels(res["Mes"], rotation=15)
ax.set_ylabel("Numero de compras")
ax.set_title(
    "Online Retail: compras reales vs pronosticadas"
)
ax.legend()
ax.grid(axis="y", alpha=0.25)

fig.tight_layout()
fig.savefig(
    GRAFICAS / "online_retail_mensual.png",
    dpi=200
)
plt.close(fig)

# 8. Grafica de error mensual
fig, ax = plt.subplots(figsize=(10, 5))

ax.bar(
    res["Mes"],
    res["Error_Porcentual"]
)

ax.axhline(0, linewidth=1)
ax.set_ylabel("Error porcentual (%)")
ax.set_title("Online Retail: error por mes")
ax.tick_params(axis="x", rotation=15)
ax.grid(axis="y", alpha=0.25)

fig.tight_layout()
fig.savefig(
    GRAFICAS / "online_retail_error_mensual.png",
    dpi=200
)
plt.close(fig)

# 9. Reportar resultados
print("\n=== COMPARACION MENSUAL ONLINE RETAIL ===")
print(
    res.round(2).to_string(index=False)
)

print("\n=== COMPROBACION GLOBAL ===")
print(f"Clientes de la cohorte: {len(rfm)}")
print(f"Compras reales: {total_real}")
print(f"Compras pronosticadas: {total_pred:.2f}")

error_global = 100 * (
    total_pred - total_real
) / total_real

print(f"Error global: {error_global:+.2f}%")

noviembre = res.loc[
    res["Mes"] == "Noviembre"
].iloc[0]

print("\n=== NOVIEMBRE ===")
print(f"Compras reales: {noviembre['Real']:.0f}")
print(
    "Compras pronosticadas:",
    f"{noviembre['Pronosticado']:.2f}"
)
print(
    "Error porcentual:",
    f"{noviembre['Error_Porcentual']:+.2f}%"
)

print("\nArchivos generados:")
print(
    "resultados/tablas/"
    "online_retail_comparacion_mensual.csv"
)
print(
    "resultados/graficas/"
    "online_retail_mensual.png"
)
print(
    "resultados/graficas/"
    "online_retail_error_mensual.png"
)
