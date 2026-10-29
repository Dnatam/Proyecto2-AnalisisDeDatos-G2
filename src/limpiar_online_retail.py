from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ORIGINAL = RAIZ / "data" / "original" / "Online Retail.xlsx"
PROCESADO = RAIZ / "data" / "procesado"

def limpiar_online_retail():
    PROCESADO.mkdir(parents=True, exist_ok=True)

    df = pd.read_excel(ORIGINAL)
    print("=== LIMPIEZA DE ONLINE RETAIL ===")
    print(f"Registros originales: {len(df)}")

    resumen = []
    def registrar(etapa, antes, despues):
        resumen.append({
            "etapa": etapa,
            "registros_antes": antes,
            "registros_eliminados": antes - despues,
            "registros_despues": despues
        })
        print(f"{etapa}: eliminados {antes - despues}, restantes {despues}")

    antes = len(df)
    df = df.dropna(subset=["CustomerID"]).copy()
    registrar("Sin CustomerID", antes, len(df))

    antes = len(df)
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")].copy()
    registrar("Facturas canceladas", antes, len(df))

    antes = len(df)
    df = df[df["Quantity"] > 0].copy()
    registrar("Cantidad no positiva", antes, len(df))

    antes = len(df)
    df = df[df["UnitPrice"] > 0].copy()
    registrar("Precio no positivo", antes, len(df))

    antes = len(df)
    df = df.dropna(subset=["InvoiceDate", "InvoiceNo"]).copy()
    registrar("Sin fecha o factura", antes, len(df))

    antes = len(df)
    df = df.drop_duplicates().copy()
    registrar("Duplicados exactos", antes, len(df))

    df["CustomerID"] = df["CustomerID"].astype(int).astype(str)
    df["InvoiceNo"] = df["InvoiceNo"].astype(str)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    df = df.sort_values(["CustomerID", "InvoiceDate", "InvoiceNo"])
    df.to_csv(PROCESADO / "online_retail_limpio.csv", index=False)

    # Una factura puede contener varios productos, pero representa una compra.
    transacciones = (
        df.groupby(["CustomerID", "InvoiceNo"], as_index=False)
        .agg(
            InvoiceDate=("InvoiceDate", "min"),
            Total=("UnitPrice", lambda s: 0.0)
        )
    )

    # Calcular el importe total de cada factura.
    df["Importe"] = df["Quantity"] * df["UnitPrice"]
    importes = (
        df.groupby(["CustomerID", "InvoiceNo"], as_index=False)["Importe"]
        .sum()
        .rename(columns={"Importe": "Total"})
    )

    transacciones = transacciones.drop(columns=["Total"]).merge(
        importes, on=["CustomerID", "InvoiceNo"], how="left"
    )

    transacciones = transacciones.sort_values(
        ["CustomerID", "InvoiceDate", "InvoiceNo"]
    )
    transacciones.to_csv(
        PROCESADO / "online_retail_transacciones.csv", index=False
    )

    pd.DataFrame(resumen).to_csv(
        PROCESADO / "resumen_limpieza_online_retail.csv", index=False
    )

    print("\n=== RESULTADOS FINALES ===")
    print(f"Líneas limpias: {len(df)}")
    print(f"Clientes: {df['CustomerID'].nunique()}")
    print(f"Transacciones: {len(transacciones)}")
    print(f"Facturas distintas: {transacciones['InvoiceNo'].nunique()}")
    print(f"Rango de fechas: {df['InvoiceDate'].min()} a {df['InvoiceDate'].max()}")
    print("\nArchivos guardados en data/procesado/")

if __name__ == "__main__":
    limpiar_online_retail()
