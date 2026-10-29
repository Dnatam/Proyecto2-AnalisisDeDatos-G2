
from pathlib import Path
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ORIGINAL = RAIZ / "data" / "original" / "Online Retail.xlsx"
PROCESADO = RAIZ / "data" / "procesado"


def limpiar_online_retail():
    PROCESADO.mkdir(parents=True, exist_ok=True)

    df = pd.read_excel(ORIGINAL)

    print("=== LIMPIEZA DE ONLINE RETAIL ===")
    print(f"Lineas originales: {len(df)}")

    resumen = []

    def registrar(etapa, antes, despues):
        resumen.append({
            "etapa": etapa,
            "registros_antes": antes,
            "registros_eliminados": antes - despues,
            "registros_despues": despues
        })
        print(
            f"{etapa}: eliminados {antes - despues}, "
            f"restantes {despues}"
        )

    # 1. Conservar registros con cliente identificado.
    antes = len(df)
    df = df.dropna(subset=["CustomerID"]).copy()
    registrar("Sin CustomerID", antes, len(df))

    # 2. Convertir y validar las fechas.
    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"], errors="coerce"
    )

    antes = len(df)
    df = df.dropna(subset=["InvoiceDate"]).copy()
    registrar("Sin fecha valida", antes, len(df))

    # 3. Convertir cantidades y precios a valores numericos.
    df["Quantity"] = pd.to_numeric(
        df["Quantity"], errors="coerce"
    )
    df["UnitPrice"] = pd.to_numeric(
        df["UnitPrice"], errors="coerce"
    )

    antes = len(df)
    df = df.dropna(subset=["Quantity", "UnitPrice"]).copy()
    df = df[
        np.isfinite(df["Quantity"]) &
        np.isfinite(df["UnitPrice"])
    ].copy()
    registrar("Cantidad o precio invalido", antes, len(df))

    # 4. Normalizar identificadores.
    df["CustomerID"] = df["CustomerID"].astype(int).astype(str)
    df["InvoiceNo"] = df["InvoiceNo"].astype(str)

    # 5. Calcular el importe de cada linea.
    # Se conservan cantidades negativas para reflejar devoluciones.
    df["Importe"] = df["Quantity"] * df["UnitPrice"]

    # 6. Obtener el dia calendario de cada registro.
    df["FechaDia"] = df["InvoiceDate"].dt.normalize()

    # 7. Guardar las lineas validas para trazabilidad.
    df = df.sort_values(
        ["CustomerID", "InvoiceDate", "InvoiceNo"]
    )

    df.to_csv(
        PROCESADO / "online_retail_limpio.csv",
        index=False
    )

    # 8. Calcular la venta neta por cliente y dia.
    transacciones = (
        df.groupby(
            ["CustomerID", "FechaDia"], as_index=False
        )
        .agg(Total=("Importe", "sum"))
    )

    dias_antes = len(transacciones)

    # 9. Una transaccion existe solo si la venta neta es positiva.
    transacciones = transacciones[
        transacciones["Total"] > 0
    ].copy()

    dias_descartados = dias_antes - len(transacciones)

    # 10. Mantener los nombres esperados por el siguiente script.
    transacciones = transacciones.rename(
        columns={"FechaDia": "InvoiceDate"}
    )

    transacciones = transacciones.sort_values(
        ["CustomerID", "InvoiceDate"]
    ).reset_index(drop=True)

    # 11. Verificaciones.
    assert not transacciones.duplicated(
        ["CustomerID", "InvoiceDate"]
    ).any(), "Existen transacciones duplicadas por cliente y dia"

    assert (
        transacciones["Total"] > 0
    ).all(), "Existen ventas netas no positivas"

    assert (
        transacciones["InvoiceDate"].dt.normalize()
        == transacciones["InvoiceDate"]
    ).all(), "Las fechas deben representar dias completos"

    # 12. Guardar transacciones diarias.
    transacciones.to_csv(
        PROCESADO / "online_retail_transacciones.csv",
        index=False
    )

    pd.DataFrame(resumen).to_csv(
        PROCESADO / "resumen_limpieza_online_retail.csv",
        index=False
    )

    print("\n=== RESULTADOS FINALES ===")
    print(f"Lineas validas: {len(df)}")
    print(f"Clientes identificados: {df['CustomerID'].nunique()}")
    print(f"Dias cliente evaluados: {dias_antes}")
    print(f"Dias con venta neta no positiva: {dias_descartados}")
    print(f"Transacciones diarias validas: {len(transacciones)}")
    print(
        "Clientes con transacciones positivas:",
        transacciones["CustomerID"].nunique()
    )
    print(
        "Rango de fechas:",
        transacciones["InvoiceDate"].min(),
        "a",
        transacciones["InvoiceDate"].max()
    )

    print("\nArchivos guardados:")
    print("data/procesado/online_retail_limpio.csv")
    print("data/procesado/online_retail_transacciones.csv")
    print("data/procesado/resumen_limpieza_online_retail.csv")


if __name__ == "__main__":
    limpiar_online_retail()
