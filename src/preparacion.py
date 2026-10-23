from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ORIGINAL = RAIZ / "data" / "original" / "CDNOW_sample.txt"
PROCESADO = RAIZ / "data" / "procesado"

# Lectura del archivo original

df = pd.read_csv(
    ORIGINAL, sep=r"\s+", header=None,
    names=["id_master", "id", "fecha", "cds", "monto"],
    dtype={"id_master": str, "fecha": str},
)
df["fecha"] = pd.to_datetime(df["fecha"], format="%Y%m%d")

print("Líneas originales:", len(df))
print("Clientes:", df["id"].nunique())


# 0.1 Varias compras del mismo cliente el mismo día = una transacción

trans = (df.groupby(["id", "fecha"], as_index=False)
           .agg(cds=("cds", "sum"), monto=("monto", "sum")))

print("Transacciones únicas (cliente-día):", len(trans))
print("Líneas combinadas por ser el mismo día:", len(df) - len(trans))

# 0.2 Tiempo en semanas (día 0 = 1 ene 1997) y separación de periodos

DIA0 = pd.Timestamp("1997-01-01")
FIN_CAL = pd.Timestamp("1997-09-30")   # último día de calibración (inclusive)
FIN_HOLD = pd.Timestamp("1998-06-30")  # último día de holdout (inclusive)

trans["semana"] = (trans["fecha"] - DIA0).dt.days / 7

cal = trans[trans["fecha"] <= FIN_CAL]
hold = trans[(trans["fecha"] > FIN_CAL) & (trans["fecha"] <= FIN_HOLD)]

print("\nTransacciones en calibración:", len(cal))
print("Transacciones en holdout:", len(hold))
print(f"Semanas: calibración hasta {cal['semana'].max():.2f}, "
      f"holdout hasta {hold['semana'].max():.2f}")


# 0.3 Estadísticos por cliente: x, tx, T (calibración) y x* (holdout)

g = cal.groupby("id")["fecha"]
rfm = pd.DataFrame({
    "primera": g.min(),
    "ultima": g.max(),
    "n_cal": g.count(),
})
rfm["x"] = rfm["n_cal"] - 1
rfm["tx"] = (rfm["ultima"] - rfm["primera"]).dt.days / 7
rfm["T"] = (FIN_CAL - rfm["primera"]).dt.days / 7
rfm["x_star"] = hold.groupby("id").size().reindex(rfm.index, fill_value=0)
rfm["semana_primera"] = (rfm["primera"] - DIA0).dt.days / 7   # lo usaremos en 3.1
rfm = rfm.drop(columns="n_cal").reset_index()

# Chequeos de consistencia: si alguno falla, el programa se detiene con un error
assert len(rfm) == 2357, "Deberían ser 2,357 clientes"
assert (rfm["primera"] <= pd.Timestamp("1997-03-31")).all(), "Todos llegaron en el 1er trimestre"
assert ((rfm["tx"] >= 0) & (rfm["tx"] <= rfm["T"])).all(), "Debe cumplirse 0 <= tx <= T"
assert ((rfm["x"] == 0) == (rfm["tx"] == 0)).all(), "x = 0 si y solo si tx = 0"

print("\nPrimeros clientes:")
print(rfm[["id", "x", "tx", "T", "x_star"]].head().round(2).to_string(index=False))
print("Compras repetidas en calibración:", rfm["x"].sum())
print("Compras en holdout:", rfm["x_star"].sum())