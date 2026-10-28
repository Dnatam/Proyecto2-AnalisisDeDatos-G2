from pathlib import Path
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]


def obtener_serie_semanal_compras_repetidas():
    """
    Construye la serie semanal de compras repetidas de toda la cohorte
    para las semanas 1 a 78.
    """
    trans_path = RAIZ / "data" / "procesado" / "cdnow_trans.csv"
    rfm_path = RAIZ / "data" / "procesado" / "cdnow_rfm.csv"

    if not trans_path.exists() or not rfm_path.exists():
        raise FileNotFoundError("Asegúrate de haber ejecutado preparacion.py primero.")

    trans = pd.read_csv(trans_path)
    rfm = pd.read_csv(rfm_path)
    trans["fecha"] = pd.to_datetime(trans["fecha"])

    DIA0 = pd.Timestamp("1997-01-01")
    # Número de semana desde el día 0 (1-indexed para semanas)
    trans["semana"] = (trans["fecha"] - DIA0).dt.days // 7 + 1

    # Mapear la semana de la primera compra de cada cliente
    map_primera = rfm.set_index("id")["semana_primera"].to_dict()
    trans["semana_primera_cli"] = trans["id"].map(map_primera)

    # Filtrar solo transacciones repetidas (compras posteriores a la primera)
    trans_repetidas = trans[trans["semana"] > (trans["semana_primera_cli"] // 1 + 1)]

    # Serie agregada semanal para las 78 semanas
    serie_completa = trans_repetidas.groupby("semana").size().reindex(range(1, 79), fill_value=0)
    return serie_completa


def generar_pronosticos_top_down():
    serie_semanal = obtener_serie_semanal_compras_repetidas()

    # Separar en calibración (1 a 39) y holdout (40 a 78)
    train = serie_semanal.loc[1:39]
    holdout = serie_semanal.loc[40:78]
    real_total_holdout = holdout.sum()

    horizonte = 39  # Semanas 40 a 78

    pronosticos = {}

    # Método 1: Media Histórica Completa
    pronosticos["Media_Historica"] = np.repeat(train.mean(), horizonte)

    # Método 2: Naïve (Último valor observado en la semana 39)
    pronosticos["Naive_Semana39"] = np.repeat(train.iloc[-1], horizonte)

    # Método 3: Promedio Móvil (Ventana 1: 4 semanas | Ventana 2: 8 semanas)
    pronosticos["Promedio_Movil_4w"] = np.repeat(train.tail(4).mean(), horizonte)
    pronosticos["Promedio_Movil_8w"] = np.repeat(train.tail(8).mean(), horizonte)

    # Método 4: Tendencia Lineal
    # Ventana 1: Serie completa de calibración (Semanas 1 a 39)
    x_full = np.arange(1, 40)
    poly_full = np.polyfit(x_full, train.values, 1)
    x_future = np.arange(40, 79)
    pronosticos["Tendencia_Lineal_Completa"] = np.polyval(poly_full, x_future)

    # Ventana 2: Últimas 12 semanas de calibración (Semanas 28 a 39)
    x_12w = np.arange(28, 40)
    poly_12w = np.polyfit(x_12w, train.loc[28:39].values, 1)
    pronosticos["Tendencia_Lineal_12w"] = np.polyval(poly_12w, x_future)

    print("=" * 75)
    print(" EVALUACIÓN DE PRONÓSTICOS TOP-DOWN (TAREA D6.T2 / INCISO 3.2)")
    print("=" * 65)
    print(f"Total real de compras repetidas en Holdout (Semanas 40-78): {real_total_holdout}\n")

    filas = []
    for nombre, pred in pronosticos.items():
        total_pred = pred.sum()
        error_pct = ((total_pred - real_total_holdout) / real_total_holdout) * 100
        mae_semanal = np.mean(np.abs(pred - holdout.values))

        filas.append({
            "Metodo": nombre,
            "Total_Pronosticado": round(total_pred, 2),
            "Error_Porcentual_%": round(error_pct, 2),
            "MAE_Semanal": round(mae_semanal, 2)
        })

    df_res = pd.DataFrame(filas)
    print(df_res.to_string(index=False))

    # Guardar en resultados/tablas/
    out_dir = RAIZ / "resultados" / "tablas"
    out_dir.mkdir(parents=True, exist_ok=True)
    archivo_salida = out_dir / "comparacion_top_down.csv"
    df_res.to_csv(archivo_salida, index=False)

    print(f"\nResultados guardados exitosamente en: {archivo_salida}\n")


if __name__ == "__main__":
    generar_pronosticos_top_down()