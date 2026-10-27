# Parte 2 — Respuestas

## 2.1 Ajuste a CDNOW y comparación con el artículo

Estimamos el BG/NBD por máxima verosimilitud con los datos de calibración de CDNOW
(`src/ajuste_cdnow.py`): optimización sobre log(r, α, a, b) con L-BFGS-B y cinco puntos
iniciales, que convergen todos al mismo óptimo sin tocar las cotas.

| Parámetro | Nuestro | Artículo | Diferencia relativa |
|---|---|---|---|
| r | 0.2426 | 0.243 | −0.17 % |
| α | 4.4136 | 4.414 | −0.01 % |
| a | 0.7929 | 0.793 | −0.01 % |
| b | 2.4259 | 2.426 | −0.005 % |
| **log-verosimilitud** | **−9582.43** | **−9582.4** | |

**Los resultados coinciden con el artículo.** Redondeados a 3 decimales, como los reporta
Fader, Hardie y Lee (2005), nuestros cuatro parámetros son idénticos a los suyos, y la
log-verosimilitud coincide. Las diferencias que quedan se explican por:

- **Redondeo del artículo.** Sus parámetros están redondeados a 3 decimales. Evaluando
  nuestra log-verosimilitud en esos valores obtenemos −9582.4305, apenas 0.0013 por debajo
  de nuestro óptimo: el punto redondeado queda casi, pero no exactamente, en el máximo.
  La diferencia relativa de r parece mayor solo porque r es pequeño.
- **Tolerancia del optimizador.** El optimizador se detiene cuando la mejora es mínima;
  distintos puntos iniciales dan diferencias en el cuarto decimal de b sin cambiar la
  log-verosimilitud, porque la superficie es casi plana en esa dirección.

Que coincidan también confirma que la preparación de los datos es la misma que la del
artículo: compras del mismo día contadas como una, tiempo en semanas (días/7) y
calibración de 39 semanas. Un error en (x, tₓ, T) habría cambiado los estimados y la
log-verosimilitud de forma visible.

Las medias implicadas también coinciden: tasa de compra media de un cliente activo
r/α = 0.0550 (artículo: 0.0551) y probabilidad media de morir después de una compra
a/(a+b) = 0.2463 (artículo: 0.2463). Su interpretación está en 2.2.