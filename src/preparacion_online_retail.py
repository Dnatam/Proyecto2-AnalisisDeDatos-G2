from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
PROCESADO = RAIZ / "data" / "procesado"

ARCHIVO = PROCESADO / "online_retail_transacciones.csv"

DIA0 = pd.Timestamp("2010-12-01")
FIN_CAL = pd.Timestamp("2011-08-31 23:59:59")
FIN_HOLD = pd.Timestamp("2011-12-09 23:59:59")

# Leer transacciones limpias
trans = pd.read_csv(
    ARCHIVO,
    dtype={"CustomerID": str, "InvoiceNo": str},
    parse_dates=["InvoiceDate"]
)

trans = trans.rename(columns={
    "CustomerID": "id",
    "InvoiceDate": "fecha",
    "InvoiceNo": "factura",
    "Total": "monto"
})

print("=== PREPARACIÓN ONLINE RETAIL ===")
print("Transacciones:", len(trans))
print("Clientes:", trans["id"].nunique())

# Verificar que cada factura sea una transacción
assert not trans.duplicated(["id", "factura"]).any()
assert (trans["monto"] > 0).all()

# Calcular tiempo en semanas
trans["semana"] = (
    trans["fecha"] - DIA0
).dt.total_seconds() / (7 * 24 * 60 * 60)

# Separar calibración y holdout
cal = trans[
    (trans["fecha"] >= DIA0) &
    (trans["fecha"] <= FIN_CAL)
].copy()

hold = trans[
    (trans["fecha"] > FIN_CAL) &
    (trans["fecha"] <= FIN_HOLD)
].copy()

print("\nTransacciones en calibración:", len(cal))
print("Transacciones en holdout:", len(hold))

# Construir variables por cliente
g = cal.groupby("id")["fecha"]

rfm = pd.DataFrame({
    "primera": g.min(),
    "ultima": g.max(),
    "n_cal": g.count()
})

rfm["x"] = rfm["n_cal"] - 1

rfm["tx"] = (
    rfm["ultima"] - rfm["primera"]
).dt.total_seconds() / (7 * 24 * 60 * 60)

rfm["T"] = (
    FIN_CAL - rfm["primera"]
).dt.total_seconds() / (7 * 24 * 60 * 60)

rfm["x_star"] = (
    hold.groupby("id")
    .size()
    .reindex(rfm.index, fill_value=0)
)

rfm["semana_primera"] = (
    rfm["primera"] - DIA0
).dt.total_seconds() / (7 * 24 * 60 * 60)

rfm = rfm.drop(columns="n_cal").reset_index()

# Verificaciones de consistencia
assert not rfm["id"].duplicated().any(), "Existen clientes duplicados"
assert (rfm["x"] >= 0).all(), "La frecuencia no puede ser negativa"
assert (rfm["T"] >= 0).all(), "El tiempo de observación no puede ser negativo"
assert (rfm["tx"] >= 0).all(), "La recencia no puede ser negativa"
assert (rfm["tx"] <= rfm["T"]).all(), "Debe cumplirse tx <= T"
assert (rfm["x_star"] >= 0).all(), "Las compras en holdout no pueden ser negativas"
assert (rfm.loc[rfm["x"] == 0, "tx"] == 0).all(), "Si x = 0, tx debe ser 0"

# Identificar compras repetidas registradas en el mismo instante
casos_simultaneos = rfm[
    (rfm["x"] > 0) & (rfm["tx"] == 0)
]

print("\n=== VALIDACIÓN RFM ===")
print("Clientes con compras simultáneas:", len(casos_simultaneos))

if not casos_simultaneos.empty:
    print("Advertencia: algunos clientes tienen x > 0 y tx = 0.")
    print("Se conservan las facturas distintas sin alterar sus fechas.")
    print(
        casos_simultaneos[
            ["id", "primera", "ultima", "x", "tx", "T"]
        ].to_string(index=False)
    )

print("Verificaciones de consistencia superadas.")

# Guardar archivos
trans.to_csv(
    PROCESADO / "online_retail_trans.csv",
    index=False
)

rfm.to_csv(
    PROCESADO / "online_retail_rfm.csv",
    index=False
)

print("\n=== RESULTADOS RFM ===")
print("Clientes en calibración:", len(rfm))
print("Compras repetidas en calibración:", rfm["x"].sum())
print("Compras en holdout de clientes calibrados:", rfm["x_star"].sum())
print("Clientes sin compras repetidas:", (rfm["x"] == 0).sum())

print("\nPrimeros clientes:")
print(
    rfm[["id", "x", "tx", "T", "x_star"]]
    .head()
    .round(3)
    .to_string(index=False)
)

print("\nArchivos guardados:")
print("data/procesado/online_retail_trans.csv")
print("data/procesado/online_retail_rfm.csv")
