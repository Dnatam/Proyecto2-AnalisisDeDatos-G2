# Parte 3 — Respuestas

## 3.1 Pronóstico bottom-up

Para cada cliente $i$, con primera compra en la semana $s_i$, el número esperado de
compras repetidas acumuladas al final de la semana $w$ es $E[X(w - s_i)]$ (cero si el
cliente aún no había llegado). Sumando sobre los 2,357 clientes obtenemos la curva
esperada de la cohorte para las semanas 1 a 78 (`src/bottom_up.py`).

![Curva bottom-up](../resultados/graficas/curva_bottom_up.png)

| | Pronóstico BG/NBD | Real |
|---|---|---|
| Acumulado a la semana 39 (calibración) | 2,501.5 | 2,457 |
| Acumulado a la semana 78 | 4,165.7 | 4,339 |
| **Total del holdout (semanas 40–78)** | **1,664.1** | **1,882** |

**¿Qué tan bien le atina al total del holdout?** El modelo pronostica 1,664 compras
repetidas en el holdout contra 1,882 reales: **subestima en 11.6 %**, con un error
absoluto medio de 9.8 compras por semana. En calibración la curva esperada prácticamente
se encima con la real, y en el holdout reproduce bien su forma (la desaceleración
conforme los clientes se van muriendo), pero se va quedando por debajo. Es decir, el
modelo predice que la cohorte se "muere" un poco más rápido de lo que en realidad pasó.

Lo notable es que el modelo logra esta curva **solo con tres números por cliente
$(x, t_x, T)$ y su fecha de primera compra**, sin ver nunca la serie agregada. La
comparación con los métodos top-down está en 3.3.