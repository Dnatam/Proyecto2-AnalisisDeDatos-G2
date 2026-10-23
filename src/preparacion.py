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