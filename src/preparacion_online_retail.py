
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
PROCESADO = RAIZ / "data" / "procesado"

ARCHIVO = PROCESADO / "online_retail_transacciones.csv"

DIA0 = pd.Timestamp("2010-12-01")
FIN_CAL = pd.Timestamp("2011-06-30")
INICIO_HOLD = pd.Timestamp("2011-07-01")
FIN_HOLD = pd.Timestamp("2011-12-08")

# Leer las transacciones diarias con venta neta positiva
trans = pd.read_csv(
    ARCHIVO,
    dtype={"CustomerID": str},
    parse_dates=["InvoiceDate"]
)

trans = trans.rename(columns={
    "CustomerID": "id",
    "InvoiceDate": "fecha",
    "Total": "monto"
})

print("=== PREPARACION ONLINE RETAIL ===")
print("Transacciones originales:", len(trans))
print("Clientes:", trans["id"].nunique())

# Validar una transaccion por cliente y dia
assert not trans.duplicated(["id", "fecha"]).any()
assert (trans["monto"] > 0).all()
assert trans["fecha"].notna().all()

# Limitar el periodo al solicitado
trans = trans[
    (trans["fecha"] >= DIA0) &
    (trans["fecha"] <= FIN_HOLD)
].copy()

# Tiempo en semanas desde el inicio del dataset
trans["semana"] = (
    (trans["fecha"] - DIA0).dt.total_seconds()
    / (7 * 24 * 60 * 60)
)

# Separar calibracion y holdout
cal = trans[
    trans["fecha"] <= FIN_CAL
].copy()

hold = trans[
    (trans["fecha"] >= INICIO_HOLD) &
    (trans["fecha"] <= FIN_HOLD)
].copy()

print("\nTransacciones en calibracion:", len(cal))
print("Transacciones en holdout:", len(hold))

# Cohorte: clientes que compraron durante calibracion
g = cal.groupby("id")["fecha"]

rfm = pd.DataFrame({
    "primera": g.min(),
    "ultima": g.max(),
    "n_cal": g.count()
})

# Compras repetidas: no incluye la primera compra
rfm["x"] = rfm["n_cal"] - 1

# Recencia desde la primera hasta la ultima compra
rfm["tx"] = (
    (rfm["ultima"] - rfm["primera"]).dt.days / 7
)

# Edad del cliente hasta el final de calibracion
# Usamos el inicio del 1 de julio como frontera temporal
FRONTERA_CAL = pd.Timestamp("2011-07-01")

rfm["T"] = (
    (FRONTERA_CAL - rfm["primera"]).dt.days / 7
)

# Compras en holdout solamente para la cohorte calibrada
rfm["x_star"] = (
    hold.groupby("id")
    .size()
    .reindex(rfm.index, fill_value=0)
)

rfm["semana_primera"] = (
    (rfm["primera"] - DIA0).dt.days / 7
)

rfm = rfm.drop(columns="n_cal").reset_index()

# Validaciones
assert not rfm["id"].duplicated().any()
assert (rfm["x"] >= 0).all()
assert (rfm["tx"] >= 0).all()
assert (rfm["T"] > 0).all()
assert (rfm["tx"] <= rfm["T"]).all()
assert (rfm["x_star"] >= 0).all()
assert (rfm.loc[rfm["x"] == 0, "tx"] == 0).all()

# Verificar que los totales sean consistentes
assert rfm["x_star"].sum() == hold[
    hold["id"].isin(rfm["id"])
].shape[0]

print("\nVerificaciones de consistencia superadas.")

# Guardar archivos que usan los siguientes programas
trans.to_csv(
    PROCESADO / "online_retail_trans.csv",
    index=False
)

rfm.to_csv(
    PROCESADO / "online_retail_rfm.csv",
    index=False
)

print("\n=== RESULTADOS RFM ===")
print("Clientes en calibracion:", len(rfm))
print("Compras repetidas en calibracion:", rfm["x"].sum())
print(
    "Compras en holdout de clientes calibrados:",
    rfm["x_star"].sum()
)
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
