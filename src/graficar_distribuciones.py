from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import gamma, beta

RAIZ = Path(__file__).resolve().parents[1]
TABLAS = RAIZ / "resultados" / "tablas"
GRAFICAS = RAIZ / "resultados" / "graficas"

GRAFICAS.mkdir(parents=True, exist_ok=True)

# Cargar parámetros estimados de CDNOW
parametros = pd.read_csv(TABLAS / "params_cdnow.csv").iloc[0]

r = float(parametros["r"])
alpha = float(parametros["alpha"])
a = float(parametros["a"])
b = float(parametros["b"])

# Verificar que todos los parámetros sean positivos
assert all(valor > 0 for valor in [r, alpha, a, b])

# Calcular las medias de ambas distribuciones
media_lambda = r / alpha
media_p = a / (a + b)

# DISTRIBUCIÓN GAMMA: TASAS DE COMPRA

# Scipy utiliza escala, por lo que scale = 1 / alpha
limite_lambda = gamma.ppf(0.999, a=r, scale=1 / alpha)

valores_lambda = np.linspace(1e-6, limite_lambda, 1000)
densidad_lambda = gamma.pdf(
    valores_lambda,
    a=r,
    scale=1 / alpha
)

plt.figure(figsize=(9, 5))

plt.plot(
    valores_lambda,
    densidad_lambda,
    color="royalblue",
    linewidth=2,
    label="Distribución Gamma"
)

plt.axvline(
    media_lambda,
    color="darkorange",
    linestyle="--",
    linewidth=2,
    label=f"Media = {media_lambda:.4f}"
)

# Limitar la altura visible para apreciar mejor la curva
plt.ylim(0, 50)

plt.xlabel("Tasa de compra (compras por semana)")
plt.ylabel("Densidad de probabilidad")
plt.title("Distribución de tasas de compra - CDNOW")

plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    GRAFICAS / "distribucion_lambda.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# DISTRIBUCIÓN BETA: PROBABILIDADES DE ABANDONO

valores_p = np.linspace(1e-6, 1 - 1e-6, 1000)

densidad_p = beta.pdf(
    valores_p,
    a=a,
    b=b
)

plt.figure(figsize=(9, 5))

plt.plot(
    valores_p,
    densidad_p,
    color="royalblue",
    linewidth=2,
    label="Distribución Beta"
)

plt.axvline(
    media_p,
    color="darkorange",
    linestyle="--",
    linewidth=2,
    label=f"Media = {media_p:.4f} ({media_p * 100:.2f}%)"
)

plt.xlabel("Probabilidad de abandono después de una compra")
plt.ylabel("Densidad de probabilidad")
plt.title("Distribución de probabilidades de abandono - CDNOW")

plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    GRAFICAS / "distribucion_p.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# RESUMEN DE RESULTADOS

print("=== DISTRIBUCIONES BG/NBD ===")

print("\nParámetros estimados:")
print(f"r = {r:.4f}")
print(f"alpha = {alpha:.4f}")
print(f"a = {a:.4f}")
print(f"b = {b:.4f}")

print("\nDistribución Gamma:")
print(f"Media de lambda: {media_lambda:.6f}")

print("\nDistribución Beta:")
print(f"Media de p: {media_p:.6f}")
print(f"Probabilidad media de abandono: {media_p * 100:.2f}%")

print("\nGráficas guardadas correctamente:")
print(GRAFICAS / "distribucion_lambda.png")
print(GRAFICAS / "distribucion_p.png")
