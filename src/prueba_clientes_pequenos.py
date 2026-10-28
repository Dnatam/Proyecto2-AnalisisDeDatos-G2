import numpy as np
from bgnbd import loglik
from ajuste_cdnow import ajustar

# Conjunto pequeño de 10 clientes ficticios
# x: número de compras repetidas
# tx: tiempo de la última compra repetida
# T: tiempo total de observación

x = np.array([0, 1, 2, 3, 0, 4, 1, 2, 5, 0])
tx = np.array([0, 5, 10, 15, 0, 20, 8, 12, 25, 0], dtype=float)
T = np.array([30] * 10, dtype=float)

# Parámetros iniciales del modelo
parametros_iniciales = np.array([1.0, 1.0, 1.0, 1.0])

# Calcular log-verosimilitud inicial
loglik_inicial = loglik(parametros_iniciales, x, tx, T)

# Ajustar el modelo utilizando múltiples inicializaciones
mejor, arranques = ajustar(x, tx, T)

# Recuperar parámetros estimados
parametros_estimados = np.array([
    mejor["r"],
    mejor["alpha"],
    mejor["a"],
    mejor["b"]
])

# Calcular log-verosimilitud con los parámetros estimados
loglik_final = loglik(parametros_estimados, x, tx, T)

# Mostrar resultados
print("=== PRUEBA CON 10 CLIENTES ===")

print("\nLog-verosimilitud inicial:", round(loglik_inicial, 4))
print("Log-verosimilitud final:", round(loglik_final, 4))

print("\nParámetros estimados:")
for nombre, valor in zip(["r", "alpha", "a", "b"], parametros_estimados):
    print(f"{nombre}: {valor:.4f}")

print("\nResultados de las inicializaciones:")
print(arranques.round(4).to_string(index=False))

print("\nVerificaciones:")
print("¿Mejoró la log-verosimilitud?", loglik_final >= loglik_inicial)
print("¿Todos los parámetros son positivos?", np.all(parametros_estimados > 0))
print("¿Convergió el mejor ajuste?", mejor["convergio"])
print("¿El mejor ajuste está en una cota?", mejor["en_cota"])
