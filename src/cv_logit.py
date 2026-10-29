from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score, accuracy_score, log_loss, brier_score_loss

RAIZ = Path(__file__).resolve().parents[1]


def ejecutar_cv_regresion_logistica(n_splits=5, n_seeds=20):
    print("=" * 75)
    print(f" VALIDACIÓN CRUZADA ({n_splits} FOLDS x {n_seeds} SEMILLAS) - REGRESIÓN LOGÍSTICA (D9.T1)")
    print("=" * 75)

    # 1. Cargar datos de CDNOW
    rfm_path = RAIZ / "data" / "procesado" / "cdnow_rfm.csv"
    if not rfm_path.exists():
        raise FileNotFoundError("No se encontró cdnow_rfm.csv. Ejecuta preparacion.py primero.")

    rfm = pd.read_csv(rfm_path)

    # Definir la variable objetivo Z (1 si volvió a comprar en holdout, 0 si no)
    # En cdnow_rfm.csv, x_star son las compras en holdout
    y = (rfm["x_star"] >= 1).astype(int).values

    # Construir matriz de características X: [x, tx, T, x/T]
    X = np.column_stack([
        rfm["x"].values,
        rfm["tx"].values,
        rfm["T"].values,
        rfm["x"].values / np.maximum(rfm["T"].values, 1e-5)
    ])

    print(f"Total de clientes: {len(rfm)}")
    print(f"Tasa base de recompra Z=1: {np.mean(y)*100:.2f}%\n")

    auc_list = []
    acc_list = []
    logloss_list = []
    brier_list = []

    # 2. Bucle sobre las 20 semillas aleatorias
    for seed in range(n_seeds):
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)

        for train_idx, val_idx in skf.split(X, y):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]

            # Entrenar Regresión Logística
            clf = LogisticRegression(solver="lbfgs", max_iter=1000)
            clf.fit(X_train, y_train)

            # Predicciones
            y_prob = clf.predict_proba(X_val)[:, 1]
            y_pred = (y_prob >= 0.5).astype(int)

            # Calcular métricas
            auc_list.append(roc_auc_score(y_val, y_prob))
            acc_list.append(accuracy_score(y_val, y_pred))
            logloss_list.append(log_loss(y_val, y_prob))
            brier_list.append(brier_score_loss(y_val, y_prob))

    # 3. Resumen Estadístico de las Métricas
    resumen = [
        {"Métrica": "AUC-ROC", "Media": np.mean(auc_list), "Desv_Est": np.std(auc_list)},
        {"Métrica": "Accuracy", "Media": np.mean(acc_list), "Desv_Est": np.std(acc_list)},
        {"Métrica": "Log-Loss", "Media": np.mean(logloss_list), "Desv_Est": np.std(logloss_list)},
        {"Métrica": "Brier Score", "Media": np.mean(brier_list), "Desv_Est": np.std(brier_list)},
    ]

    df_res = pd.DataFrame(resumen)

    print("=" * 60)
    print(" RESULTADOS CONSOLIDADOS (100 EVALUACIONES EN TOTAL)")
    print("=" * 60)
    for row in resumen:
        print(f" {row['Métrica']:<12}: Media = {row['Media']:.4f} | Desv. Est. = {row['Desv_Est']:.4f}")

    # 4. Guardar tabla en resultados/tablas/
    out_dir = RAIZ / "resultados" / "tablas"
    out_dir.mkdir(parents=True, exist_ok=True)
    archivo_salida = out_dir / "cv_logit_resultados.csv"
    df_res.round(4).to_csv(archivo_salida, index=False)

    print(f"\nResultados guardados exitosamente en: {archivo_salida}\n")


if __name__ == "__main__":
    ejecutar_cv_regresion_logistica()