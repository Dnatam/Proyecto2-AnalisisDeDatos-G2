# Ajuste del BG/NBD con Online Retail (detalle técnico)

Programas: `src/preparacion_online_retail.py` (x, tₓ, T y x\*), `src/ajuste_online_retail.py`
(estimación) y `src/comparar_nbd_online_retail.py` (diagnóstico de 5.1). Las respuestas a
5.1 y 5.2 están en `respuestas_parte5.md`.

## 1. Periodos y cohorte

| Periodo | Fechas | Duración |
|---|---|---|
| Calibración | 1 dic 2010 – 30 jun 2011 | 30.3 semanas |
| Holdout | 1 jul – 8 dic 2011 (sin el 9 de diciembre, incompleto) | 161 días = 23 semanas |

La cohorte son los clientes con al menos una transacción hasta el 30 de junio; su "primera
compra" es la primera que aparece en los datos. Los clientes que aparecen por primera vez
en el holdout no se pronostican. tₓ = (última − primera)/7 y T = (1 de julio − primera)/7,
en días/7.

| Indicador | Valor |
|---|---:|
| Clientes en la cohorte | 2,959 |
| Clientes con x = 0 | 1,416 (47.9 %) |
| Clientes cuya primera compra en los datos es de diciembre de 2010 | 29.8 % |
| Compras de la cohorte en el holdout (Σx\*) | 6,344 |
| T medio | 18.8 semanas (máximo 30.3) |

## 2. Estimación

Se usa la misma función `ajustar` que en CDNOW (L-BFGS-B sobre los logaritmos, cinco puntos
iniciales, cotas en ±10).

| | r | α | a | b | E[p] = a/(a+b) | log-verosimilitud |
|---|---|---|---|---|---|---|
| BG/NBD | 0.739 | 9.199 | 0.0002 | 264 | ≈ 10⁻⁶ | −15,181.72 |
| NBD (nadie se muere) | 0.739 | 9.201 | — | — | 0 | −15,181.72 |

r y α son estables, pero **b no está identificado**: la verosimilitud es prácticamente
plana a lo largo de la dirección a/(a+b) → 0, así que distintos puntos iniciales o
versiones de scipy dan valores de b muy distintos (de cientos a miles) con la misma
log-verosimilitud. Lo que se debe reportar es E[p] ≈ 0, no el valor de b.

## 3. Archivos generados

- `data/procesado/online_retail_trans.csv`, `data/procesado/online_retail_rfm.csv`
- `resultados/tablas/params_online_retail.csv`, `ajuste_online_retail_arranques.csv`
- `resultados/tablas/online_retail_bg_vs_nbd.csv`