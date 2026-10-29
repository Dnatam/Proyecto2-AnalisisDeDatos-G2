# Parte 4 — Respuestas

## 4.3 La probabilidad correcta: $P(Z = 1)$

La demostración completa está en `documentos/derivacion_bgnbd.md` (sección 4.3). El
resultado, con $\tau = 39$ semanas, es

$$
P(Z = 1 \mid x, t_x, T) = P(\text{vivo} \mid x, t_x, T) \left[ 1 - \left(\frac{\alpha+T}{\alpha+T+\tau}\right)^{r+x} \right]
$$

Se implementó en `src/bgnbd.py` (`prob_vivo`, `prob_comprar`) y se calculó para cada
cliente en `src/prob_compra.py`.

![P(vivo) contra P(Z = 1)](../resultados/graficas/pvivo_vs_pz.png)

| $x$ en calibración | Clientes | Promedio $P(\text{vivo})$ | Promedio $P(Z = 1)$ | Fracción real que compró |
|---|---|---|---|---|
| 0 | 1,411 | 1.000 | 0.161 | 0.137 |
| 1 | 439 | 0.474 | 0.281 | 0.358 |
| 2 | 214 | 0.540 | 0.432 | 0.584 |
| 3 | 100 | 0.552 | 0.499 | 0.590 |
| 4 | 62 | 0.617 | 0.587 | 0.790 |
| 5 | 38 | 0.611 | 0.597 | 0.684 |
| 6 | 29 | 0.691 | 0.683 | 0.655 |
| 7+ | 64 | 0.722 | 0.720 | 0.875 |
| **Total** | **2,357** | **0.813** | **0.262** | **0.290** |

**Estar vivo no es lo mismo que comprar.** $P(\text{vivo})$ promedia 0.81 cuando solo el
29 % de los clientes compró en el holdout. $P(Z = 1)$, que multiplica $P(\text{vivo})$
por la probabilidad de que un cliente vivo compre al menos una vez en 39 semanas,
promedia 0.26, mucho más cerca de la tasa real. La diferencia se concentra en los
clientes con $x = 0$: el modelo los considera vivos con probabilidad 1, pero como su
tasa de compra posterior es muy baja ($\lambda \mid \text{vivo} \sim \text{Gamma}(r, \alpha + T)$,
con media cercana a 0.006 compras por semana), su probabilidad de comprar es solo de
0.14 a 0.18, cerca del 13.7 % observado. En cambio, para los clientes frecuentes
$P(Z = 1) \approx P(\text{vivo})$: si están vivos, casi seguro compran.

La evaluación formal de $P(Z = 1)$ como clasificador (AUC, Brier y calibración) está en 4.5.