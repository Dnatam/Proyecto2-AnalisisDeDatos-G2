# Supuestos Teóricos del Modelo BG/NBD

El modelo BG/NBD (Beta-Geometric / Negative Binomial Distribution) desarrollado por Fader, Hardie y Lee (2005) describe el comportamiento del cliente en un entorno **no contractual y continuo** mediante cinco supuestos fundamentales:

---

### Supuesto 1: Proceso de compra Poisson
Mientras un cliente $i$ se encuentra **activo**, el número de transacciones que realiza sigue un **proceso de Poisson** con tasa de compra $\lambda_i$.
* **Implicación:** El tiempo entre compras consecutivas sigue una distribución exponencial con parámetro $\lambda_i$, lo que implica que las compras ocurren de forma independiente a una tasa promedio constante mientras el cliente siga con la empresa.

---

### Supuesto 2: Heterogeneidad en la tasa de compra ($\lambda$)
Las tasas de compra $\lambda_i$ varían entre clientes según una **distribución Gamma** con parámetro de forma $r$ y parámetro de escala/tasa $\alpha$:
$$\lambda \sim \text{Gamma}(r, \alpha)$$
* **Implicación:** Permite capturar que algunos clientes son inherentemente más frecuentes en sus compras que otros. La mezcla entre el proceso de Poisson y la distribución Gamma da origen a la Distribución Binomial Negativa (NBD) para el conteo de compras.

---

### Supuesto 3: Proceso de abandono ("muerte") geométrico
Después de **cada compra**, el cliente se vuelve inactivo ("muere") con una probabilidad constante $p_i$.
* **Implicación:** La oportunidad de abandonar la empresa únicamente ocurre en el instante posterior a una transacción (no en cualquier punto del tiempo continuo). Esto implica que el número de compras hasta que el cliente decide no volver a comprar sigue una distribución geométrica con parámetro $p_i$.

---

### Supuesto 4: Heterogeneidad en la probabilidad de abandono ($p$)
La probabilidad de abandono $p_i$ varía entre clientes según una **distribución Beta** con parámetros de forma $a$ y $b$:
$$p \sim \text{Beta}(a, b)$$
* **Implicación:** Modela el hecho de que algunos clientes son muy leales (tienen un $p$ cercano a 0) mientras que otros tienden a abandonar la marca rápidamente después de pocas transacciones (tienen un $p$ cercano a 1).

---

### Supuesto 5: Independencia entre parámetros
La tasa de compra $\lambda_i$ y la probabilidad de abandono $p_i$ varían entre clientes de forma **mutuamente independiente**.
* **Implicación:** Saber qué tan frecuentemente compra un cliente ($\lambda$) no proporciona información sobre su probabilidad de abandonar la empresa ($p$), lo que simplifica la integración y la verosimilitud conjunta del modelo.