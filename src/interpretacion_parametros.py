from pathlib import Path
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ARCHIVO = RAIZ / "resultados" / "tablas" / "params_cdnow.csv"

# Cargar parámetros estimados del modelo BG/NBD
parametros = pd.read_csv(ARCHIVO).iloc[0]

r = float(parametros["r"])
alpha = float(parametros["alpha"])
a = float(parametros["a"])
b = float(parametros["b"])

# Verificar que los parámetros sean positivos
assert all(valor > 0 for valor in [r, alpha, a, b])

# Distribución Gamma: tasa de compra lambda
media_lambda = r / alpha
varianza_lambda = r / (alpha ** 2)
desviacion_lambda = np.sqrt(varianza_lambda)

# Distribución Beta: probabilidad de abandono p
media_p = a / (a + b)
varianza_p = (a * b) / ((a + b) ** 2 * (a + b + 1))
desviacion_p = np.sqrt(varianza_p)

# Mostrar resultados
print("=== INTERPRETACIÓN DE PARÁMETROS BG/NBD ===")

print("\nParámetros estimados de CDNOW:")
print(f"r = {r:.4f}")
print(f"alpha = {alpha:.4f}")
print(f"a = {a:.4f}")
print(f"b = {b:.4f}")

print("\nDistribución Gamma - Tasa de compra:")
print(f"Media: {media_lambda:.6f} compras por semana")
print(f"Varianza: {varianza_lambda:.6f}")
print(f"Desviación estándar: {desviacion_lambda:.6f}")

print("\nDistribución Beta - Probabilidad de abandono:")
print(f"Media: {media_p:.6f}")
print(f"Media porcentual: {media_p * 100:.2f}%")
print(f"Varianza: {varianza_p:.6f}")
print(f"Desviación estándar: {desviacion_p:.6f}")

print("\nInterpretación:")
print("La tasa de compra varía entre clientes y se modela con Gamma.")
print("La probabilidad de abandono varía entre clientes y se modela con Beta.")
print("El abandono se considera después de una compra, no cada semana.")