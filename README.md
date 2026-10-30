# Proyecto 2 — Contando clientes con modelos *Buy 'Til You Die*

Análisis y Ciencia de Datos · Facultad de Ingeniería · Universidad del Istmo de Guatemala

**Grupo 2:** Sofía Blanco · Katherine Diéguez · Daniela Natareno

Implementamos desde cero el modelo **BG/NBD** (Fader, Hardie y Lee, 2005): derivamos su verosimilitud, la programamos con `scipy.special` (`gammaln`, `betaln`, `hyp2f1`), la estimamos por máxima verosimilitud con `scipy.optimize.minimize` y la usamos para pronosticar compras y estimar qué clientes siguen activos. Lo aplicamos a CDNOW y a Online Retail, y lo comparamos con pronósticos top-down, con el MBG/NBD y con una regresión logística. Las librerías `lifetimes` y PyMC-Marketing no se usan en ningún resultado.

## Resultados principales

| Parte | Resultado |
|---|---|
| 1. Simulación | Con 30 semillas se recuperan los cuatro parámetros con sesgo menor al 3 %; la compra (r, α) se estima mucho mejor que la muerte (a, b). |
| 2. Ajuste a CDNOW | r = 0.243, α = 4.414, a = 0.793, b = 2.426; log-verosimilitud −9582.43, igual que el artículo. |
| 3. Pronóstico | El BG/NBD (bottom-up) tiene el menor error semanal (MAE 9.83) y subestima el holdout en 11.6 %; los métodos top-down sobreestiman entre 10 % y 40 %. |
| 4. ¿Quién sigue vivo? | P(vivo) ordena peor que el azar (AUC 0.316) porque vale 1 para todo cliente sin compras repetidas; P(Z = 1) llega a AUC 0.757 y Brier 0.161. |
| 4.6 MBG/NBD | Ajusta igual (log L −9582.14); P(vivo) sí ordena (AUC 0.687) y P(Z = 1) empata con el BG/NBD. |
| 5. Online Retail | El modelo apaga la muerte (a ≈ 0) y queda igual a un NBD; el error es −1.4 % de julio a octubre y −38 % en noviembre por estacionalidad. |
| 6. Logística | Gana solo con fuga de información; en la comparación honesta a 13 semanas empata en orden y el BG/NBD estima mejor los niveles. |

## Requisitos

Python 3.10 o superior con `numpy`, `scipy`, `pandas`, `scikit-learn`, `matplotlib` y `openpyxl` (para leer `Online Retail.xlsx`):

```bash
pip install numpy scipy pandas scikit-learn matplotlib openpyxl
```

## Cómo correrlo

Todo parte de los archivos originales de `data/original/` (`CDNOW_sample.txt` y `Online Retail.xlsx`). Los scripts se corren desde la carpeta `src/`, en este orden; cada uno guarda sus tablas en `resultados/tablas/` y sus gráficas en `resultados/graficas/`.

```bash
cd src
# Parte 0 y 1: preparación, verificación de la verosimilitud y simulación
python preparacion.py
python verificar_integral.py        # integral doble numérica (tarda ~2 min)
python bgnbd.py                     # pruebas del modelo
python simulador.py
python simular_cohorte.py
python simulacion.py
python comparar_simulacion.py
python prueba_clientes_pequenos.py
# Parte 2: ajuste a CDNOW
python ajuste_cdnow.py
python comparar_articulo.py
python interpretacion_parametros.py
python graficar_distribuciones.py
python bootstrap.py
# Parte 3: pronósticos
python bottom_up.py
python top_down.py
python comparar_pronosticos.py
python por_cliente.py
# Parte 4: ¿quién sigue vivo?
python clientes_activos.py
python prob_compra.py
python validar_p_z1.py
python evaluar_prob_compra.py
python mbgnbd.py                    # pruebas del MBG/NBD (tarda ~2 min)
python ajuste_mbgnbd.py
python comparar_modelos.py
# Parte 5: Online Retail
python limpiar_online_retail.py
python preparacion_online_retail.py
python ajuste_online_retail.py
python comparar_nbd_online_retail.py
python comparar_online_retail.py
python analisis_mensual_online_retail.py
# Parte 6: regresión logística
python cv_logit.py
python comparacion_temporal_logit.py
python comparar_logistica_bgnbd.py
python cambio_horizonte.py
```

## Estructura

```
data/original/     archivos originales (CDNOW y Online Retail)
data/procesado/    datos intermedios generados por los scripts
src/               un script por inciso; bgnbd.py y mbgnbd.py contienen los modelos
documentos/        derivaciones, respuestas por parte e interpretaciones
resultados/        tablas (.csv) y gráficas (.png)
presentacion/      diapositivas en PDF y su fuente LaTeX
```

## Dónde está cada inciso

| Inciso | Respuesta | Código principal |
|---|---|---|
| 0.1–0.4 Preparación | `respuestas_parte0.md` | `preparacion.py` |
| 1.1–1.2 Derivación | `derivacion_bgnbd.md`, `supuestos_bgnbd.md` | `verificar_integral.py`, `bgnbd.py` |
| 1.3 Simulación | `respuestas_parte1.md`, `interpretacion_recuperacion_parametros.md` | `simulador.py`, `simulacion.py`, `comparar_simulacion.py` |
| 2.1 Ajuste a CDNOW | `respuestas_parte2.md`, `validacion_optimizador.md` | `ajuste_cdnow.py`, `comparar_articulo.py` |
| 2.2 Interpretación | `interpretacion_parametros.md`, `distribuciones_parametros.md` | `interpretacion_parametros.py`, `graficar_distribuciones.py` |
| 2.3 Bootstrap (bono) | `resultados/tablas/bootstrap_cdnow.csv` | `bootstrap.py` |
| 3.1 Bottom-up | `respuestas_parte3.md` | `bottom_up.py` |
| 3.2–3.3 Top-down y comparación | `interpretacion_pronosticos.md` | `top_down.py`, `comparar_pronosticos.py` |
| 3.4 Por cliente | `respuestas_parte3.md` | `por_cliente.py` |
| 4.1–4.2 P(vivo) | `clientes_activos.md`, `compartimiento_x0.md` | `clientes_activos.py` |
| 4.3 P(Z = 1) | `respuestas_parte4.md` | `prob_compra.py` |
| 4.4 Verificación por simulación | `resultados/tablas/validacion_p_z1_deciles.csv` | `validar_p_z1.py` |
| 4.5 Evaluación con datos reales | `evaluacion_prob_compra.md` | `evaluar_prob_compra.py` |
| 4.6 MBG/NBD | `respuestas_parte4.md` | `mbgnbd.py`, `ajuste_mbgnbd.py`, `comparar_modelos.py` |
| 5.1–5.2 Online Retail | `respuestas_parte5.md`, `limpieza_online_retail.md`, `ajuste_online_retail.md` | `limpiar_online_retail.py`, `preparacion_online_retail.py`, `ajuste_online_retail.py`, `comparar_nbd_online_retail.py`, `comparar_online_retail.py`, `analisis_mensual_online_retail.py` |
| 6.1 Comparación ingenua | `conclusion_logistica_bgnbd.md` (sección 2) | `cv_logit.py` |
| 6.2 Fuga de información | `fuga_informacion_logit.md` | — |
| 6.3 Versión honesta | `conclusion_logistica_bgnbd.md` | `comparacion_temporal_logit.py`, `comparar_logistica_bgnbd.py` |
| 6.4 Cambio de horizonte | `respuestas_parte6.md` | `cambio_horizonte.py` |
| 6.5 Veredicto | `conclusion_logistica_bgnbd.md` | — |

Los documentos están en `documentos/`, los scripts en `src/` y las tablas en `resultados/tablas/`.

## Presentación

`presentacion/presentacion.pdf` contiene las diapositivas. Para recompilarlas desde `presentacion/`: `python figuras.py` (genera tres figuras propias) y `xelatex presentacion.tex` (las fuentes están en `presentacion/fonts/`).

## Referencias

- P. S. Fader, B. G. S. Hardie y K. L. Lee. "Counting Your Customers" the Easy Way: An Alternative to the Pareto/NBD Model. *Marketing Science*, 24(2):275–284, 2005.
- E. P. Batislam, M. Denizel y A. Filiztekin. Empirical Validation and Comparison of Models for Customer Base Analysis. *International Journal of Research in Marketing*, 24(3):201–209, 2007.
- R. J. Hyndman y G. Athanasopoulos. *Forecasting: Principles and Practice*, 2.ª ed., §10.3–10.4. OTexts, 2018.
- Datos: CDNOW (B. Hardie, brucehardie.com/datasets) y Online Retail (UCI Machine Learning Repository).
