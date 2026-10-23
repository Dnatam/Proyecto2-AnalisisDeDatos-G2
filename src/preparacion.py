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