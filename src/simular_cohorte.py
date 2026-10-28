from pathlib import Path
import pandas as pd
from simulador import simular_cohorte_bgnbd

RAIZ = Path(__file__).resolve().parents[1]

def generar_y_guardar_cohorte_simulada():
    # Parámetros seleccionados del inciso 1.3
    r = 0.25
    alpha = 4.0
    a = 0.8
    b = 2.5
    n_clientes = 2357
    seed = 42  # Semilla fija para esta simulación base

    print("=" * 60)
    print(" GENERANDO DATASET SIMULADO DE 2,357 CLIENTES (D4.T1)")
    print("=" * 60)

    # 1. Ejecutar la simulación usando nuestro módulo de D3.T4
    x_sim, tx_sim, T_sim, lams, ps = simular_cohorte_bgnbd(
        r=r, alpha=alpha, a=a, b=b, n_clientes=n_clientes, seed=seed
    )

    # 2. Estructurar el DataFrame resultante
    df_sim = pd.DataFrame({
        "id": range(1, n_clientes + 1),
        "x": x_sim,
        "tx": tx_sim,
        "T": T_sim,
        "lambda_verdadero": lams,
        "p_verdadero": ps
    })

    # 3. Guardar el resultado en data/procesado/
    out_dir = RAIZ / "data" / "procesado"
    out_dir.mkdir(parents=True, exist_ok=True)
    archivo_salida = out_dir / "cdnow_simulado_base.csv"
    df_sim.to_csv(archivo_salida, index=False)

    # Mostrar estadísticos de la cohorte
    print(f"\nCohorte simulada exitosamente con semilla = {seed}:")
    print(f" - Clientes totales: {len(df_sim)}")
    print(f" - Promedio de compras repetidas (x): {df_sim['x'].mean():.4f}")
    print(f" - Fracción de clientes sin re-compra (x=0): {(df_sim['x'] == 0).mean():.4f}")
    print(f" - Tiempo T promedio: {df_sim['T'].mean():.2f} semanas")
    print(f"\nArchivo guardado en: {archivo_salida}\n")

if __name__ == "__main__":
    generar_y_guardar_cohorte_simulada()