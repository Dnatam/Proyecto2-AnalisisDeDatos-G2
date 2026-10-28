from pathlib import Path
import numpy as np
import pandas as pd
from bgnbd import compras_esperadas
from top_down import obtener_serie_semanal_compras_repetidas

RAIZ = Path(__file__).resolve().parents[1]


def calcular_pronostico_bgnbd_bottom_up(params, rfm):
    """
    Construye la curva esperada de compras repetidas acumuladas
    semana por semana de la semana 1 a la 78 usando la fecha de primera
    compra de cada cliente (Inciso 3.1 / Bottom-Up).
    """
    n_semanas = 78
    semanas_primera = rfm["semana_primera"].values

    # Matriz para almacenar las compras esperadas acumuladas de cada cliente en cada semana
    # t_cli = semana_evaluacion - semana_primera
    esperados_acum = np.zeros((len(rfm), n_semanas))

    for w in range(1, n_semanas + 1):
        t_cli = np.maximum(0.0, w - semanas_primera)
        esperados_acum[:, w - 1] = compras_esperadas(params, t_cli)

    # Sumar entre todos los clientes para obtener la curva agregada acumulada
    curva_acum_total = esperados_acum.sum(axis=0)

    # Convertir acumulado a compras semanales (diferencias finitas)
    semanal_bgnbd = np.diff(np.insert(curva_acum_total, 0, 0.0))
    return semanal_bgnbd


def generar_comparacion_consolidada():
    rfm_path = RAIZ / "data" / "procesado" / "cdnow_rfm.csv"
    if not rfm_path.exists():
        raise FileNotFoundError("Asegúrate de ejecutar preparacion.py primero.")

    rfm = pd.read_csv(rfm_path)
    serie_semanal = obtener_serie_semanal_compras_repetidas()

    # Parámetros del artículo/ajuste de CDNOW (r, alpha, a, b)
    params_bgnbd = (0.2426, 4.4136, 0.7929, 2.4259)

    # 1. Obtener la serie semanal pronosticada por el BG/NBD
    semanal_bgnbd = calcular_pronostico_bgnbd_bottom_up(params_bgnbd, rfm)
    bgnbd_holdout = semanal_bgnbd[39:78]  # Semanas 40 a 78

    # 2. Datos reales del holdout (Semanas 40 a 78)
    holdout_real = serie_semanal.loc[40:78].values
    real_total = holdout_real.sum()

    # 3. Pronósticos Top-Down de la calibración (1 a 39)
    train = serie_semanal.loc[1:39]
    horizonte = 39

    modelos = {}

    # BG/NBD (Bottom-Up)
    modelos["BG/NBD (Bottom-Up)"] = bgnbd_holdout

    # Top-Down
    modelos["Promedio Movil 8w (Top-Down)"] = np.repeat(train.tail(8).mean(), horizonte)
    modelos["Promedio Movil 4w (Top-Down)"] = np.repeat(train.tail(4).mean(), horizonte)
    modelos["Tendencia Lineal 12w (Top-Down)"] = np.polyval(
        np.polyfit(np.arange(28, 40), train.loc[28:39].values, 1),
        np.arange(40, 79)
    )
    modelos["Media Historica (Top-Down)"] = np.repeat(train.mean(), horizonte)
    modelos["Naive Semana 39 (Top-Down)"] = np.repeat(train.iloc[-1], horizonte)
    modelos["Tendencia Lineal Completa (Top-Down)"] = np.polyval(
        np.polyfit(np.arange(1, 40), train.values, 1),
        np.arange(40, 79)
    )

    filas = []
    for nombre, pred in modelos.items():
        pred_total = pred.sum()
        error_pct = ((pred_total - real_total) / real_total) * 100
        mae = np.mean(np.abs(pred - holdout_real))

        filas.append({
            "Metodo": nombre,
            "Total_Pronosticado": round(pred_total, 2),
            "Error_Porcentual_%": round(error_pct, 2),
            "MAE_Semanal": round(mae, 2)
        })

    df_res = pd.DataFrame(filas)

    print("=" * 80)
    print(" TABLA COMPARATIVA CONSOLIDADA DE PRONÓSTICOS (TAREA D6.T3 / INCISO 3.3)")
    print("=" * 80)
    print(f"Total real de compras repetidas en Holdout (Semanas 40-78): {real_total}\n")
    print(df_res.to_string(index=False))

    # Guardar en resultados/tablas/
    out_dir = RAIZ / "resultados" / "tablas"
    out_dir.mkdir(parents=True, exist_ok=True)
    archivo_salida = out_dir / "comparacion_consolidada_3_3.csv"
    df_res.to_csv(archivo_salida, index=False)

    print(f"\nResultados guardados exitosamente en: {archivo_salida}\n")


if __name__ == "__main__":
    generar_comparacion_consolidada()