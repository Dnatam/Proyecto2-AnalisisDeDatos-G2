from pathlib import Path

import numpy as np
import pandas as pd

from ajuste_cdnow import ajustar, NOMBRES
from bgnbd import loglik_individual

RAIZ = Path(__file__).resolve().parents[1]
PROCESADO = RAIZ / "data" / "procesado"
TABLAS = RAIZ / "resultados" / "tablas"

# Leer las variables RFM de Online Retail
rfm = pd.read_csv(PROCESADO / "online_retail_rfm.csv")

x = rfm["x"].to_numpy(dtype=float)
tx = rfm["tx"].to_numpy(dtype=float)
T = rfm["T"].to_numpy(dtype=float)

print("=== AJUSTE BG/NBD - ONLINE RETAIL ===")
print("Clientes en calibración:", len(rfm))
print("Compras repetidas:", int(x.sum()))
print("Clientes sin compras repetidas:", int((x == 0).sum()))

# Verificar los datos antes del ajuste
assert len(rfm) > 0, "No hay clientes para ajustar"
assert np.isfinite(x).all(), "Existen frecuencias inválidas"
assert np.isfinite(tx).all(), "Existen recencias inválidas"
assert np.isfinite(T).all(), "Existen tiempos de observación inválidos"
assert (x >= 0).all(), "Existen frecuencias negativas"
assert (tx >= 0).all(), "Existen recencias negativas"
assert (T > 0).all(), "Los tiempos de observación deben ser positivos"
assert (tx <= T).all(), "Debe cumplirse tx <= T"

# Estimar parámetros con los cinco puntos iniciales
mejor, arranques = ajustar(x, tx, T)

print("\n=== RESULTADOS POR PUNTO INICIAL ===")
print(arranques.round(4).to_string(index=False))

# Revisar convergencia y coincidencia de soluciones
validos = arranques[
    arranques["convergio"] &
    np.isfinite(arranques["loglik"]) &
    ~arranques["en_cota"]
]

if validos.empty:
    raise RuntimeError(
        "Ningún ajuste convergió satisfactoriamente fuera de las cotas."
    )

mejor = validos.loc[validos["loglik"].idxmax()]

coinciden = (
    np.abs(validos["loglik"] - mejor["loglik"]) < 1e-2
).sum()

print("\n=== VALIDACIÓN DEL AJUSTE ===")
print("Arranques válidos:", len(validos), "de", len(arranques))
print("Arranques que coinciden con el mejor:", coinciden)
print("¿Convergió el mejor ajuste?:", mejor["convergio"])
print("¿Algún parámetro en la cota?:", mejor["en_cota"])

# Obtener los parámetros estimados
params = mejor[NOMBRES].to_numpy(dtype=float)

print("\n=== PARÁMETROS ESTIMADOS ===")
for nombre in NOMBRES:
    print(f"{nombre:>5} = {mejor[nombre]:.6f}")

print(f"Log-verosimilitud = {mejor['loglik']:.4f}")

# Comprobar que la log-verosimilitud individual sea finita
ll_individual = loglik_individual(params, x, tx, T)

assert np.isfinite(ll_individual).all(), (
    "Existen log-verosimilitudes individuales no finitas"
)

assert np.isclose(
    ll_individual.sum(), mejor["loglik"], atol=1e-2
), "La log-verosimilitud calculada no coincide"

# Guardar resultados
TABLAS.mkdir(parents=True, exist_ok=True)

pd.DataFrame([
    {
        **{nombre: mejor[nombre] for nombre in NOMBRES},
        "loglik": mejor["loglik"]
    }
]).to_csv(
    TABLAS / "params_online_retail.csv",
    index=False
)

arranques.to_csv(
    TABLAS / "ajuste_online_retail_arranques.csv",
    index=False
)

print("\n=== ARCHIVOS GUARDADOS ===")
print("resultados/tablas/params_online_retail.csv")
print("resultados/tablas/ajuste_online_retail_arranques.csv")
print("\nAjuste finalizado correctamente.")
