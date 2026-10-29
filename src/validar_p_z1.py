from pathlib import Path
import numpy as np
import pandas as pd
from bgnbd import prob_comprar
from simulador import simular_cohorte_bgnbd

RAIZ = Path(__file__).resolve().parents[1]


def simular_holdout_y_validar_deciles(params, n_clientes=20000, tau=39.0, seed=123):
    r, alpha, a, b = params
    rng = np.random.default_rng(seed)

    print("=" * 70)
    print(" VALIDACIÓN DE P(Z=1) POR SIMULACIÓN Y DECILES (TAREA D7.T4 / INCISO 4.4)")
    print("=" * 70)

    # 1. Generar distribuciones de clientes
    lambdas = rng.gamma(shape=r, scale=1.0 / alpha, size=n_clientes)
    ps = rng.beta(a=a, b=b, size=n_clientes)
    Ts = rng.uniform(27.0, 39.0, size=n_clientes)

    xs = np.zeros(n_clientes, dtype=int)
    txs = np.zeros(n_clientes, dtype=float)
    zs = np.zeros(n_clientes, dtype=int)

    # 2. Simular Calibración (T) y Holdout (tau)
    for i in range(n_clientes):
        lam = lambdas[i]
        p = ps[i]
        T = Ts[i]

        t = 0.0
        x = 0
        tx = 0.0
        vivo = True

        # Periodo de Calibración T
        while True:
            wait = rng.exponential(scale=1.0 / lam)
            if t + wait > T:
                break
            t += wait
            x += 1
            tx = t
            if rng.random() < p:
                vivo = False
                break

        xs[i] = x
        txs[i] = tx

        # Periodo de Holdout tau (T a T + tau)
        if vivo:
            t_hold = 0.0
            compras_hold = 0
            while True:
                wait = rng.exponential(scale=1.0 / lam)
                if t_hold + wait > tau:
                    break
                t_hold += wait
                compras_hold += 1
                if rng.random() < p:
                    break
            zs[i] = 1 if compras_hold > 0 else 0
        else:
            zs[i] = 0

    # 3. Calcular P(Z=1) teórica usando la función importada de bgnbd.py
    p_z1_teorica = prob_comprar(params, xs, txs, Ts, tau)

    df = pd.DataFrame({
        "p_z1_teorica": p_z1_teorica,
        "z_real_simulado": zs
    })

    # 4. Agrupar por deciles de probabilidad teórica
    df["decil"] = pd.qcut(df["p_z1_teorica"], q=10, labels=False) + 1

    resumen = df.groupby("decil").agg(
        Clientes=("z_real_simulado", "count"),
        Prob_Teorica_Promedio=("p_z1_teorica", "mean"),
        Fraccion_Real_Compro=("z_real_simulado", "mean")
    ).reset_index()

    resumen["Diferencia_Absoluta"] = np.abs(resumen["Prob_Teorica_Promedio"] - resumen["Fraccion_Real_Compro"])

    print(resumen.round(4).to_string(index=False))

    # Guardar resultados
    out_dir = RAIZ / "resultados" / "tablas"
    out_dir.mkdir(parents=True, exist_ok=True)
    archivo_salida = out_dir / "validacion_p_z1_deciles.csv"
    resumen.round(4).to_csv(archivo_salida, index=False)

    print(f"\nResultados guardados exitosamente en: {archivo_salida}\n")


if __name__ == "__main__":
    params_cdnow = (0.2426, 4.4136, 0.7929, 2.4259)
    simular_holdout_y_validar_deciles(params_cdnow)