from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, accuracy_score, log_loss, brier_score_loss

RAIZ = Path(__file__).resolve().parents[1]


def evaluar_ventana_temporal(rfm_trans, t_corte, tau=39.0):
    """
    Filtra las transacciones hasta t_corte semanas, calcula variables RFM
    y evalúa el modelo logístico prediciendo compras en el holdout de tau semanas.
    """
    # 1. Filtrar transacciones en la ventana de calibración [0, t_corte]
    cal = rfm_trans[rfm_trans["semana"] <= t_corte].copy()
    hold = rfm_trans[(rfm_trans["semana"] > t_corte) & (rfm_trans["semana"] <= t_corte + tau)].copy()

    # Agrupar por cliente en calibración
    g = cal.groupby("id")["semana"]
    rfm_cal = pd.DataFrame({
        "primera": g.min(),
        "ultima": g.max(),
        "n_cal": g.count()
    })

    rfm_cal["x"] = rfm_cal["n_cal"] - 1
    rfm_cal["tx"] = rfm_cal["ultima"] - rfm_cal["primera"]
    rfm_cal["T"] = t_corte - rfm_cal["primera"]

    # Compras reales en holdout (Z = 1 si compro en holdout, 0 si no)
    hold_counts = hold.groupby("id").size()
    rfm_cal["x_star"] = hold_counts.reindex(rfm_cal.index, fill_value=0)
    rfm_cal["Z"] = (rfm_cal["x_star"] >= 1).astype(int)

    # Matriz de características X
    X = np.column_stack([
        rfm_cal["x"].values,
        rfm_cal["tx"].values,
        rfm_cal["T"].values,
        rfm_cal["x"].values / np.maximum(rfm_cal["T"].values, 1e-5)
    ])
    y = rfm_cal["Z"].values

    # Entrenar Regresión Logística
    clf = LogisticRegression(solver="lbfgs", max_iter=1000, random_state=42)
    clf.fit(X, y)

    y_prob = clf.predict_proba(X)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)

    return {
        "Ventana_Calibracion": f"{int(t_corte)} semanas",
        "Clientes": len(rfm_cal),
        "Tasa_Base_Holdout_%": round(np.mean(y) * 100, 2),
        "AUC-ROC": round(roc_auc_score(y, y_prob), 4),
        "Accuracy": round(accuracy_score(y, y_pred), 4),
        "Log-Loss": round(log_loss(y, y_prob), 4),
        "Brier_Score": round(brier_score_loss(y, y_prob), 4)
    }


def ejecutar_comparacion_temporal():
    print("=" * 75)
    print(" COMPARACIÓN TEMPORAL HONESTA (13 Y 26 SEMANAS) - REGRESIÓN LOGÍSTICA (D9.T3)")
    print("=" * 75)

    trans_path = RAIZ / "data" / "procesado" / "cdnow_transacciones.csv"
    if not trans_path.exists():
        # Intento de ruta alternativa común
        trans_path = RAIZ / "data" / "procesado" / "cdnow_trans.csv"
        if not trans_path.exists():
            raise FileNotFoundError("No se encontró el archivo de transacciones de CDNOW. Ejecuta preparacion.py primero.")

    df_trans = pd.read_csv(trans_path)

    # Convertir fechas a semanas desde la fecha mínima
    if "semana" not in df_trans.columns:
        df_trans["fecha"] = pd.to_datetime(df_trans["fecha"])
        fecha_min = df_trans["fecha"].min()
        df_trans["semana"] = (df_trans["fecha"] - fecha_min).dt.total_seconds() / (7 * 24 * 3600)

    resultados = []
    ventanas = [13.0, 26.0, 39.0]

    for t_corte in ventanas:
        res = evaluar_ventana_temporal(df_trans, t_corte=t_corte, tau=39.0)
        resultados.append(res)

    df_res = pd.DataFrame(resultados)

    print("\n" + "=" * 75)
    print(" RESULTADOS POR VENTANA TEMPORAL DE CALIBRACIÓN")
    print("=" * 75)
    print(df_res.to_string(index=False))

    # Guardar en resultados/tablas/
    out_dir = RAIZ / "resultados" / "tablas"
    out_dir.mkdir(parents=True, exist_ok=True)
    archivo_salida = out_dir / "comparacion_temporal_logit.csv"
    df_res.to_csv(archivo_salida, index=False)

    print(f"\nResultados guardados exitosamente en: {archivo_salida}\n")


if __name__ == "__main__":
    ejecutar_comparacion_temporal()