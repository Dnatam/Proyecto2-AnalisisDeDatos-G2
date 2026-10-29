from pathlib import Path
import numpy as np
import pandas as pd
from bgnbd import compras_condicionales

RAIZ = Path(__file__).resolve().parents[1]


def evaluar_pronostico_online_retail():
    print("=" * 75)
    print(" EVALUACIÓN DEL PRONÓSTICO BG/NBD EN ONLINE RETAIL (TAREA D8.T5 / INCISO 5.2)")
    print("=" * 75)

    # 1. Cargar datos RFM y parámetros del ajuste
    rfm_path = RAIZ / "data" / "procesado" / "online_retail_rfm.csv"
    params_path = RAIZ / "resultados" / "tablas" / "params_online_retail.csv"

    if not rfm_path.exists():
        raise FileNotFoundError("No se encontró online_retail_rfm.csv. Ejecuta preparacion_online_retail.py primero.")
    if not params_path.exists():
        raise FileNotFoundError("No se encontró params_online_retail.csv. Ejecuta ajuste_online_retail.py primero.")

    rfm = pd.read_csv(rfm_path)
    df_params = pd.read_csv(params_path)

    nombres = ["r", "alpha", "a", "b"]
    params = tuple(df_params.iloc[0][nombres].values)

    print(f"Parámetros cargados (Online Retail): r={params[0]:.4f}, alpha={params[1]:.4f}, a={params[2]:.4f}, b={params[3]:.4f}")
    print(f"Clientes en calibración: {len(rfm)}")

    # 2. Definir la duración del holdout (tau)
    # FIN_CAL = 2011-08-31 23:59:59, FIN_HOLD = 2011-12-09 23:59:59 (aprox 14.2857 semanas)
    dias_holdout = (pd.Timestamp("2011-12-09 23:59:59") - pd.Timestamp("2011-08-31 23:59:59")).total_seconds() / (24 * 3600)
    tau = dias_holdout / 7.0
    print(f"Horizonte de holdout (tau): {tau:.4f} semanas ({dias_holdout:.1f} días)")

    # 3. Calcular compras esperadas en holdout por cliente
    x = rfm["x"].values
    tx = rfm["tx"].values
    T = rfm["T"].values
    x_star_real = rfm["x_star"].values

    x_esperado = compras_condicionales(params, x, tx, T, tau)
    rfm["x_esperado"] = x_esperado

    # 4. Totales y Métricas Globales
    total_real = np.sum(x_star_real)
    total_pred = np.sum(x_esperado)
    error_pct = ((total_pred - total_real) / total_real) * 100
    mae = np.mean(np.abs(x_esperado - x_star_real))

    print("\n" + "-" * 60)
    print(" MÉTRICAS GLOBALES EN HOLDOUT")
    print("-" * 60)
    print(f" Total de compras reales en holdout (x*) : {total_real:,.0f}")
    print(f" Total de compras pronosticadas E[Y(tau)]: {total_pred:,.2f}")
    print(f" Error porcentual acumulado              : {error_pct:+.2f}%")
    print(f" MAE a nivel cliente                     : {mae:.4f}")

    # 5. Evaluación por Segmentos de Frecuencia en Calibración (x = 0, 1, 2, ..., 7+)
    rfm["grupo_x"] = np.where(rfm["x"] >= 7, "7+", rfm["x"].astype(str))
    orden_grupos = [str(i) for i in range(7)] + ["7+"]

    resumen_segmentos = rfm.groupby("grupo_x").agg(
        Clientes=("id", "count"),
        Prom_Compras_Reales=("x_star", "mean"),
        Prom_Compras_Esperadas=("x_esperado", "mean")
    ).reindex(orden_grupos).reset_index()

    resumen_segmentos["Diferencia"] = resumen_segmentos["Prom_Compras_Esperadas"] - resumen_segmentos["Prom_Compras_Reales"]

    print("\n" + "=" * 75)
    print(" COMPARACIÓN POR SEGMENTO DE FRECUENCIA DE CALIBRACIÓN")
    print("=" * 75)
    print(resumen_segmentos.round(4).to_string(index=False))

    # 6. Guardar Resultados
    out_dir = RAIZ / "resultados" / "tablas"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Tabla por segmentos
    archivo_segmentos = out_dir / "online_retail_holdout_segmentos.csv"
    resumen_segmentos.round(4).to_csv(archivo_segmentos, index=False)

    # Resumen global
    df_global = pd.DataFrame([{
        "Total_Real": total_real,
        "Total_Pronosticado": round(total_pred, 2),
        "Error_Porcentual_%": round(error_pct, 2),
        "MAE_Cliente": round(mae, 4)
    }])
    archivo_global = out_dir / "online_retail_holdout_global.csv"
    df_global.to_csv(archivo_global, index=False)

    print(f"\nResultados guardados en:")
    print(f" - {archivo_segmentos}")
    print(f" - {archivo_global}\n")


if __name__ == "__main__":
    evaluar_pronostico_online_retail()