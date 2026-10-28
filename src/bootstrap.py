from pathlib import Path
import numpy as np
import pandas as pd
import scipy.optimize as opt
from bgnbd import loglik

RAIZ = Path(__file__).resolve().parents[1]


def neg_loglik_log_params(log_params, x, tx, T):
    """Función objetivo a minimizar en espacio logarítmico para L-BFGS-B."""
    params = np.exp(log_params)
    return -loglik(params, x, tx, T)


def ejecutar_bootstrap(n_iterations=100, seed=42):
    # 1. Cargar el dataset de calibración de CDNOW
    rfm_path = RAIZ / "data" / "procesado" / "cdnow_rfm.csv"
    if not rfm_path.exists():
        raise FileNotFoundError("No se encontró cdnow_rfm.csv. Asegúrate de haber ejecutado preparacion.py.")

    rfm = pd.read_csv(rfm_path)
    x = rfm["x"].values
    tx = rfm["tx"].values
    T = rfm["T"].values
    n_clientes = len(rfm)

    # Parámetros reportados en el artículo como valores iniciales
    params_init = np.log([0.243, 4.414, 0.793, 2.426])

    rng = np.random.default_rng(seed)
    bootstrap_estimates = []

    print("=" * 65)
    print(" EJECUTANDO BOOTSTRAP POR CLIENTES SOBRE CDNOW (TAREA D5.T5)")
    print("=" * 65)
    print(f"Total de clientes en muestra: {n_clientes}")
    print(f"Número de iteraciones bootstrap: {n_iterations}\n")

    for i in range(n_iterations):
        # Remuestreo de clientes con reemplazo
        idx_resample = rng.choice(n_clientes, size=n_clientes, replace=True)
        x_boot = x[idx_resample]
        tx_boot = tx[idx_resample]
        T_boot = T[idx_resample]

        # Estimación de máxima verosimilitud para la muestra bootstrap
        res = opt.minimize(
            neg_loglik_log_params,
            params_init,
            args=(x_boot, tx_boot, T_boot),
            method="L-BFGS-B",
            bounds=[(-10, 10)] * 4,
        )

        params_est = np.exp(res.x)
        bootstrap_estimates.append(params_est)

        if (i + 1) % 20 == 0 or i == n_iterations - 1:
            print(f" Iteración {i+1:03d}/{n_iterations} completada -> "
                  f"r={params_est[0]:.4f}, alpha={params_est[1]:.4f}, "
                  f"a={params_est[2]:.4f}, b={params_est[3]:.4f}")

    bootstrap_estimates = np.array(bootstrap_estimates)

    # 2. Calcular la media y el Error Estándar (SE) de cada parámetro
    means = np.mean(bootstrap_estimates, axis=0)
    se = np.std(bootstrap_estimates, axis=0)

    nombres = ["r", "alpha", "a", "b"]

    print("\n" + "=" * 65)
    print(" RESULTADOS DEL BOOTSTRAP (ERRORES ESTÁNDAR ESTIMADOS)")
    print("=" * 65)

    res_summary = []
    for k in range(4):
        print(f"Parámetro {nombres[k]:<5}: Media Bootstrap = {means[k]:.4f} | Error Estándar (SE) = {se[k]:.4f}")
        res_summary.append({
            "Parametro": nombres[k],
            "Media_Bootstrap": round(means[k], 4),
            "SE_Bootstrap": round(se[k], 4)
        })

    # 3. Guardar la tabla en resultados/tablas/
    out_dir = RAIZ / "resultados" / "tablas"
    out_dir.mkdir(parents=True, exist_ok=True)
    archivo_salida = out_dir / "bootstrap_cdnow.csv"
    pd.DataFrame(res_summary).to_csv(archivo_salida, index=False)

    print(f"\nResultados guardados exitosamente en: {archivo_salida}\n")


if __name__ == "__main__":
    ejecutar_bootstrap()