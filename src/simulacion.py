from pathlib import Path
import numpy as np
import pandas as pd
import scipy.optimize as opt
from bgnbd import loglik
from simulador import simular_cohorte_bgnbd

RAIZ = Path(__file__).resolve().parents[1]


# 1. Configuración de Parámetros, Semillas y Criterios
PARAMETROS_VERDADEROS = {
    "r": 0.25,
    "alpha": 4.0,
    "a": 0.8,
    "b": 2.5
}
N_CLIENTES = 2357
T_MIN = 27.0
T_MAX = 39.0
N_SEMILLAS = 30


# 2. Simulador de Comportamiento Individual BG/NBD
def simular_cliente(lam, p, T, rng):
    """
    Simula las compras repetidas de un cliente con tasa lam y prob. de muerte p
    durante un periodo T.
    """
    t = 0.0
    x = 0
    tx = 0.0
    
    while True:
        # Tiempo entre compras ~ Exponencial(lam)
        wait = rng.exponential(scale=1.0 / lam)
        if t + wait > T:
            break
        
        t += wait
        x += 1
        tx = t
        
        # Proceso de muerte justo después de la compra con probabilidad p
        if rng.random() < p:
            break
            
    return x, tx


def generar_dataset(r, alpha, a, b, n_clientes=N_CLIENTES, rng=None):
    """Genera (x, tx, T) para n_clientes sintéticos."""
    if rng is None:
        rng = np.random.default_rng()
        
    lambdas = rng.gamma(shape=r, scale=1.0 / alpha, size=n_clientes)
    ps = rng.beta(a=a, b=b, size=n_clientes)
    Ts = rng.uniform(T_MIN, T_MAX, size=n_clientes)
    
    xs = np.zeros(n_clientes, dtype=int)
    txs = np.zeros(n_clientes, dtype=float)
    
    for i in range(n_clientes):
        xs[i], txs[i] = simular_cliente(lambdas[i], ps[i], Ts[i], rng)
        
    return xs, txs, Ts



# 3. Función Objetivo y Estimación por Máxima Verosimilitud
def neg_loglik_log_params(log_params, x, tx, T):
    """Transformación a log-parámetros para asegurar estabilidad y límites positivos."""
    params = np.exp(log_params)
    return -loglik(params, x, tx, T)


def estimar_parametros(x, tx, T):
    """Optimiza los parámetros arrancando desde un punto razonable."""
    log_init = np.log([0.5, 2.0, 1.0, 1.0])
    res = opt.minimize(
        neg_loglik_log_params,
        log_init,
        args=(x, tx, T),
        method="L-BFGS-B",
        bounds=[(-10, 10)] * 4
    )
    return np.exp(res.x), res.success



# 4. Experimento Monte Carlo (30 Semillas)
def ejecutar_simulacion():
    r_v = PARAMETROS_VERDADEROS["r"]
    alpha_v = PARAMETROS_VERDADEROS["alpha"]
    a_v = PARAMETROS_VERDADEROS["a"]
    b_v = PARAMETROS_VERDADEROS["b"]
    verdaderos = np.array([r_v, alpha_v, a_v, b_v])
    
    resultados = []
    print("=" * 60)
    print(" EJECUTANDO SIMULACIÓN MONTE CARLO (TAREA D1.T5 / INCISO 1.3)")
    print("=" * 60)
    print(f"Parámetros Verdaderos: r={r_v}, alpha={alpha_v}, a={a_v}, b={b_v}")
    print(f"Semillas a evaluar: 0 a {N_SEMILLAS - 1}\n")
    
    for s in range(N_SEMILLAS):
        rng = np.random.default_rng(seed=s)
        x_sim, tx_sim, T_sim = generar_dataset(r_v, alpha_v, a_v, b_v, rng=rng)
        params_est, exito = estimar_parametros(x_sim, tx_sim, T_sim)
        
        resultados.append(params_est)
        print(f"Semilla {s:02d} [{ 'OK' if exito else 'FAIL' }] -> "
              f"r={params_est[0]:.4f}, alpha={params_est[1]:.4f}, "
              f"a={params_est[2]:.4f}, b={params_est[3]:.4f}")
        
    resultados = np.array(resultados)
    medias = np.mean(resultados, axis=0)
    stds = np.std(resultados, axis=0)
    
    print("\n" + "=" * 60)
    print(" RESUMEN ESTADÍSTICO DE ESTIMACIÓN (30 SEMILLAS)")
    print("=" * 60)
    nombres = ["r", "alpha", "a", "b"]
    
    res_summary = []
    for i in range(4):
        print(f"Parámetro {nombres[i]:<5}: Verdadero = {verdaderos[i]:<6.4f} | "
              f"Media = {medias[i]:<6.4f} | DesvEst = {stds[i]:<6.4f}")
        res_summary.append({
            "Parametro": nombres[i],
            "Verdadero": verdaderos[i],
            "Media_Estimada": round(medias[i], 4),
            "Desv_Estandar": round(stds[i], 4)
        })
        
    # Guardar resultados numéricos en resultados/tablas/
    out_dir = RAIZ / "resultados" / "tablas"
    out_dir.mkdir(parents=True, exist_ok=True)
    df_semillas = pd.DataFrame(resultados, columns=["r", "alpha", "a", "b"])
    df_semillas.insert(0, "semilla", range(N_SEMILLAS))
    df_semillas.to_csv(out_dir / "sim_estimaciones.csv", index=False)
    df_res = pd.DataFrame(res_summary)
    archivo_salida = out_dir / "simulacion_30_semillas.csv"
    df_res.to_csv(archivo_salida, index=False)
    print(f"\nResultados guardados exitosamente en: {archivo_salida}")


if __name__ == "__main__":
    ejecutar_simulacion()