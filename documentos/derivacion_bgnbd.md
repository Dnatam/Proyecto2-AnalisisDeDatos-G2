# Derivación de la verosimilitud del BG/NBD

## 1.1 Verosimilitud de un cliente con λ y p conocidas

### Notación

Cada cliente hace su primera compra en el tiempo 0 (medimos el tiempo desde ahí).
En el periodo de calibración observamos:

- $x$: número de compras repetidas (sin contar la primera);
- $t_1 < t_2 < \dots < t_x$: los momentos de esas compras repetidas;
- $t_x$: el momento de la última compra repetida ($t_x = 0$ si $x = 0$);
- $T$: el tiempo total que observamos al cliente desde su primera compra.

### Dos piezas que vamos a usar

**Pieza 1: compras (supuesto i).** Mientras el cliente está vivo, compra según un
proceso de Poisson con tasa $\lambda$. Eso equivale a que los tiempos entre compras
son exponenciales con tasa $\lambda$:

- la densidad de que la siguiente compra ocurra $\Delta$ semanas después es $\lambda e^{-\lambda \Delta}$;
- la probabilidad de que **no** compre durante $\Delta$ semanas es $e^{-\lambda \Delta}$.

**Pieza 2: muerte (supuesto iii).** Justo después de cada compra repetida, el cliente
muere con probabilidad $p$ y sobrevive con probabilidad $1 - p$. Mientras no compra,
no puede morir.

### Historia A: el cliente sigue vivo al final de la calibración

Para que esto ocurra necesitamos que:

1. las $x$ compras repetidas ocurran en $t_1, \dots, t_x$;
2. el cliente sobreviva después de cada una de ellas;
3. no compre entre $t_x$ y $T$.

**Tiempos de compra.** Multiplicamos la densidad de cada tiempo entre compras y,
al final, la probabilidad de no comprar en $(t_x, T]$:

$$
\lambda e^{-\lambda t_1} \cdot \lambda e^{-\lambda (t_2 - t_1)} \cdots \lambda e^{-\lambda (t_x - t_{x-1})} \cdot \underbrace{e^{-\lambda (T - t_x)}}_{\text{no compra en } (t_x,\, T]} = \lambda^x e^{-\lambda T}
$$

Los exponentes se cancelan en cadena (telescopio):
$t_1 + (t_2 - t_1) + \dots + (t_x - t_{x-1}) + (T - t_x) = T$.

**Supervivencia.** Sobrevive a cada una de las $x$ compras con probabilidad $1 - p$,
de forma independiente: $(1 - p)^x$.

Entonces:

$$
L_A = (1 - p)^x \, \lambda^x e^{-\lambda T}
$$

Si $x = 0$, queda $L_A = e^{-\lambda T}$: el cliente estuvo vivo y no compró durante todo $T$.

### Historia B: el cliente murió justo después de su compra en $t_x$

**Supervivencia y muerte.** Sobrevive a las primeras $x - 1$ compras y muere justo
después de la $x$-ésima: $p(1 - p)^{x-1}$.

**Tiempos de compra.** Las compras hasta $t_x$ tienen la misma densidad que antes,
pero el telescopio ahora llega solo hasta $t_x$: $\lambda^x e^{-\lambda t_x}$.

Después de $t_x$ el cliente ya está muerto, así que no comprar entre $t_x$ y $T$
ocurre con probabilidad 1: **no aparece** el factor $e^{-\lambda (T - t_x)}$.

$$
L_B = p(1 - p)^{x-1} \, \lambda^x e^{-\lambda t_x}
$$

### ¿Por qué la historia B no existe si $x = 0$?

En el BG/NBD el cliente **solo puede morir justo después de una compra repetida**.
Si $x = 0$, no hubo ninguna compra repetida después de la cual morir, así que el
cliente necesariamente sigue vivo: solo es posible la historia A.

### Resultado

Las dos historias son mutuamente excluyentes (o está vivo en $T$, o murió en $t_x$)
y producen exactamente los mismos datos observados, así que la verosimilitud es su suma.
Con $\delta_{x>0} = 1$ si $x > 0$ y $0$ si no:

$$
\boxed{L(\lambda, p \mid x, t_x, T) = (1 - p)^x \lambda^x e^{-\lambda T} + \delta_{x>0} \, p(1 - p)^{x-1} \lambda^x e^{-\lambda t_x}}
$$

### Ejemplo con un cliente de CDNOW

El cliente 1 hizo su primera compra el 1 de enero de 1997 y compras repetidas el
18 de enero ($t_1 = 2.43$) y el 2 de agosto ($t_2 = 30.43$). Por lo tanto
$x = 2$, $t_x = 30.43$ y $T = 38.86$:

$$
L = \underbrace{(1-p)^2 \lambda^2 e^{-38.86\lambda}}_{\text{sigue vivo y no compró en 8.4 semanas}}
  + \underbrace{p(1-p)\, \lambda^2 e^{-30.43\lambda}}_{\text{murió después del 2 de agosto}}
$$

Noten que $t_1 = 2.43$ no aparece en ninguna parte.

### Observación: $(x, t_x, T)$ son estadísticos suficientes

Gracias al telescopio, la verosimilitud no depende de $t_1, \dots, t_{x-1}$: solo
importan cuántas compras hubo, cuándo fue la última y cuánto tiempo observamos al
cliente. Por eso el modelo puede trabajar con solo tres números por cliente.

### Preguntas posibles

- **¿Por qué se suman las historias y no se multiplican?** Porque son eventos
  mutuamente excluyentes, y la probabilidad de una unión de eventos disjuntos es
  la suma de sus probabilidades.
- **¿Por qué en la historia B no está $e^{-\lambda(T - t_x)}$?** Porque un cliente
  muerto no compra con probabilidad 1; no hay que "pagar" por no haber comprado.
- **¿Por qué no importan las fechas de las compras intermedias?** Por el telescopio:
  los exponentes se cancelan y solo queda la última fecha.
- **¿Por qué un cliente con $x = 0$ no puede estar muerto?** Porque en el BG/NBD la
  muerte solo ocurre después de una compra repetida. Esta decisión es justo la que
  cambia el MBG/NBD (inciso 4.6).

  ---

## 1.2 Mezcla sobre λ y p

### Planteamiento

Ahora $\lambda$ y $p$ no son conocidas: varían entre clientes según

$$
f(\lambda \mid r, \alpha) = \frac{\alpha^r \lambda^{r-1} e^{-\alpha\lambda}}{\Gamma(r)}, \quad \lambda > 0
\qquad \text{(supuesto ii: Gamma con forma } r \text{ y tasa } \alpha\text{)}
$$

$$
f(p \mid a, b) = \frac{p^{a-1}(1-p)^{b-1}}{B(a,b)}, \quad 0 < p < 1
\qquad \text{(supuesto iv: Beta}(a, b)\text{)}
$$

La verosimilitud de un cliente en función de los parámetros poblacionales es el
promedio de la verosimilitud de 1.1 sobre todos los valores posibles de $\lambda$ y $p$.
Por el supuesto (v), $\lambda$ y $p$ son independientes, así que su densidad conjunta
es el producto $f(\lambda \mid r, \alpha) \, f(p \mid a, b)$:

$$
L(r, \alpha, a, b \mid x, t_x, T) = \int_0^1 \!\! \int_0^\infty L(\lambda, p \mid x, t_x, T) \, f(\lambda \mid r, \alpha) \, f(p \mid a, b) \, d\lambda \, dp
$$

### La integral se separa

Cada término de $L(\lambda, p \mid x, t_x, T)$ es el producto de una función de $p$ por
una función de $\lambda$:

$$
L(\lambda, p \mid x, t_x, T) = \underbrace{(1-p)^x}_{\text{solo } p} \cdot \underbrace{\lambda^x e^{-\lambda T}}_{\text{solo } \lambda}
+ \delta_{x>0} \underbrace{p(1-p)^{x-1}}_{\text{solo } p} \cdot \underbrace{\lambda^x e^{-\lambda t_x}}_{\text{solo } \lambda}
$$

Gracias a la independencia, cada integral doble es el producto de dos integrales simples:

$$
L(r, \alpha, a, b \mid x, t_x, T) =
\underbrace{\int_0^1 (1-p)^x f(p) \, dp}_{(\text{p1})} \cdot \underbrace{\int_0^\infty \lambda^x e^{-\lambda T} f(\lambda) \, d\lambda}_{(\lambda\text{ con } t = T)}
+ \delta_{x>0}
\underbrace{\int_0^1 p(1-p)^{x-1} f(p) \, dp}_{(\text{p2})} \cdot \underbrace{\int_0^\infty \lambda^x e^{-\lambda t_x} f(\lambda) \, d\lambda}_{(\lambda\text{ con } t = t_x)}
$$

Solo hay que resolver una integral en $\lambda$ (para un $t$ genérico) y dos en $p$.

### Integral sobre $\lambda$ (mezcla gamma–Poisson)

Usamos una identidad que sale de que la densidad Gamma$(k, c)$ integra 1:

$$
\int_0^\infty \lambda^{k-1} e^{-c\lambda} \, d\lambda = \frac{\Gamma(k)}{c^k}, \qquad k > 0, \; c > 0.
$$

Para cualquier $t \ge 0$, sustituimos $f(\lambda \mid r, \alpha)$ y juntamos potencias y exponenciales:

$$
\int_0^\infty \lambda^x e^{-\lambda t} \, \frac{\alpha^r \lambda^{r-1} e^{-\alpha\lambda}}{\Gamma(r)} \, d\lambda
= \frac{\alpha^r}{\Gamma(r)} \int_0^\infty \lambda^{(r+x)-1} e^{-(\alpha + t)\lambda} \, d\lambda
= \frac{\alpha^r}{\Gamma(r)} \cdot \frac{\Gamma(r+x)}{(\alpha + t)^{r+x}}
$$

usando la identidad con $k = r + x$ y $c = \alpha + t$.

Se aplica dos veces: con $t = T$ en la historia A y con $t = t_x$ en la historia B.

*Interpretación:* lo que queda dentro de la integral es el núcleo de una
Gamma$(r + x, \, \alpha + t)$. Es la misma cuenta de la mezcla gamma–Poisson
(binomial negativa) de la clase de GLMs.

### Integrales sobre $p$ (definición de la función beta)

Usamos la definición de la función beta:

$$
B(u, v) = \int_0^1 p^{u-1}(1-p)^{v-1} \, dp, \qquad u > 0, \; v > 0.
$$

**(p1) Historia A:** sobrevivir a las $x$ compras.

$$
\int_0^1 (1-p)^x \, \frac{p^{a-1}(1-p)^{b-1}}{B(a,b)} \, dp
= \frac{1}{B(a,b)} \int_0^1 p^{a-1}(1-p)^{(b+x)-1} \, dp
= \frac{B(a, \, b+x)}{B(a,b)}
$$

**(p2) Historia B:** sobrevivir a $x-1$ compras y morir en la $x$-ésima.

$$
\int_0^1 p(1-p)^{x-1} \, \frac{p^{a-1}(1-p)^{b-1}}{B(a,b)} \, dp
= \frac{1}{B(a,b)} \int_0^1 p^{(a+1)-1}(1-p)^{(b+x-1)-1} \, dp
= \frac{B(a+1, \, b+x-1)}{B(a,b)}
$$

**Ojo con $x = 0$:** $B(a+1, b+x-1)$ requiere $b + x - 1 > 0$. Con $x \ge 1$ esto
siempre se cumple, pero con $x = 0$ quedaría $B(a+1, b-1)$, que no existe si $b \le 1$.
No es problema matemático porque ese término va multiplicado por $\delta_{x>0} = 0$,
pero en el código hay que evitar evaluarlo (lo veremos en D3.T2).

### Resultado

Sustituimos las tres integrales y sacamos el factor común $\dfrac{\Gamma(r+x)\,\alpha^r}{\Gamma(r)}$:

$$
\boxed{L(r, \alpha, a, b \mid x, t_x, T) = \frac{\Gamma(r+x)\,\alpha^r}{\Gamma(r)} \left[ \frac{B(a, b+x)}{B(a,b)} \frac{1}{(\alpha+T)^{r+x}} + \delta_{x>0} \frac{B(a+1, b+x-1)}{B(a,b)} \frac{1}{(\alpha+t_x)^{r+x}} \right]}
$$

Cada término conserva su significado: el primero corresponde a la historia A (sigue
vivo) y el segundo a la historia B (murió después de $t_x$).

### Log-verosimilitud de la muestra

Los clientes son independientes, así que la verosimilitud de la muestra es el producto
de las verosimilitudes individuales. En la práctica maximizamos su logaritmo:

$$
\ell(r, \alpha, a, b) = \sum_{i=1}^{N} \log L(r, \alpha, a, b \mid x_i, t_{x,i}, T_i)
$$

Para programarla de forma estable, con
$c_i = \log\Gamma(r + x_i) - \log\Gamma(r) + r \log\alpha$:

$$
\log L_i = c_i + \log\!\Big( e^{A_i} + \delta_{x_i>0}\, e^{B_i} \Big)
$$

$$
A_i = \log B(a, b+x_i) - \log B(a,b) - (r + x_i)\log(\alpha + T_i)
$$

$$
B_i = \log B(a+1, b+x_i-1) - \log B(a,b) - (r + x_i)\log(\alpha + t_{x,i})
$$

En Python: `gammaln` para $\log\Gamma$, `betaln` para $\log B$ y `np.logaddexp(A, B)`
para $\log(e^A + e^B)$, poniendo $B_i = -\infty$ cuando $x_i = 0$.

### Preguntas posibles

- **¿Por qué se puede separar la integral doble?** Porque $\lambda$ y $p$ son
  independientes (supuesto v) y cada término es un producto de una función de $p$ por
  una de $\lambda$. Sin independencia habría que integrar la densidad conjunta completa.
- **¿De dónde sale la identidad de la Gamma?** De que la densidad Gamma$(k, c)$ integra 1.
- **¿Por qué trabajamos con el logaritmo?** Porque $\Gamma(r+x)$ crece muchísimo y
  $(\alpha+T)^{-(r+x)}$ se vuelve diminuto; multiplicarlos directamente desborda la
  computadora. En logaritmos son sumas de números razonables.
- **¿Qué significan $r/\alpha$ y $a/(a+b)$?** Son las medias de las distribuciones de
  $\lambda$ y de $p$: la tasa de compra promedio de un cliente activo y la probabilidad
  promedio de morir después de una compra (inciso 2.2).

  ### Verificación numérica

El script `src/verificar_integral.py` calcula la integral doble numéricamente
(`scipy.integrate.dblquad`) y la compara con la fórmula cerrada, usando los
parámetros del artículo ($r = 0.243$, $\alpha = 4.414$, $a = 0.793$, $b = 2.426$).

| $x$ | $t_x$ | $T$ | Fórmula cerrada | Integral numérica |
|---|---------|-----|-----------------|-------------------|
| 0 | 0.00 | 38.86 | 5.742369e-01 | 5.742369e-01 |
| 1 | 1.71 | 38.86 | 1.145770e-02 | 1.145770e-02 |
| 2 | 30.43 | 38.86 | 7.801524e-05 | 7.801524e-05 |
| 5 | 20.00 | 30.00 | 8.254443e-08 | 8.254443e-08 |

Coinciden en todos los casos, incluido $x = 0$.

## 4.3 Probabilidad de comprar en el holdout, $P(Z = 1)$

Sea $Z = 1$ si el cliente hace al menos una compra en las $\tau$ semanas siguientes al
final de la calibración, es decir, en $(T, T + \tau]$, y $Z = 0$ si no.

### Primero: ¿de dónde sale $P(\text{vivo})$?

Por la regla de Bayes, la probabilidad de estar vivo dados los datos es el peso de la
historia A dentro de la verosimilitud total de 1.2:

$$
P(\text{vivo} \mid x, t_x, T) = \frac{\text{término A}}{\text{término A} + \delta_{x>0}\,\text{término B}}
= \left[ 1 + \delta_{x>0} \frac{B(a+1, b+x-1)}{B(a, b+x)} \left(\frac{\alpha+T}{\alpha+t_x}\right)^{r+x} \right]^{-1}
$$

y como $\dfrac{B(a+1, b+x-1)}{B(a, b+x)} = \dfrac{\Gamma(a+1)\,\Gamma(b+x-1)}{\Gamma(a)\,\Gamma(b+x)} = \dfrac{a}{b+x-1}$:

$$
P(\text{vivo} \mid x, t_x, T) = \left[ 1 + \delta_{x>0} \frac{a}{b+x-1} \left(\frac{\alpha+T}{\alpha+t_x}\right)^{r+x} \right]^{-1}
$$

Con $x = 0$ solo existe la historia A, así que $P(\text{vivo}) = 1$.

### Paso 1: separar por el estado del cliente en $T$

Al final de la calibración el cliente está vivo o muerto:

$$
P(Z = 0) = \underbrace{P(\text{muerto})}_{1 - P(\text{vivo})} \cdot \underbrace{P(Z = 0 \mid \text{muerto})}_{= 1}
+ P(\text{vivo}) \cdot P(Z = 0 \mid \text{vivo})
$$

Un cliente muerto no compra con probabilidad 1.

### Paso 2: un cliente vivo que no compra sigue vivo (pista 1)

En el BG/NBD solo se muere justo después de una compra. Si el cliente no compra en
$(T, T + \tau]$, no tiene ninguna oportunidad de morir, así que sigue comprando con
tasa $\lambda$ durante todo el intervalo. Para un $\lambda$ conocido, cero compras en
$\tau$ semanas de un proceso de Poisson ocurre con probabilidad

$$
P(Z = 0 \mid \text{vivo}, \lambda) = e^{-\lambda \tau}.
$$

Si compra, puede morir después, pero eso ya no importa: $Z = 1$.

### Paso 3: distribución de $\lambda$ dado que está vivo (pista 2)

No conocemos $\lambda$, pero la historia del cliente nos da información sobre ella.
Por Bayes, si el cliente está vivo en $T$, su historia es la historia A de 1.1:

$$
f(\lambda \mid \text{vivo}, x, t_x, T) \;\propto\;
\underbrace{\int_0^1 (1-p)^x f(p)\, dp}_{\text{constante en } \lambda}
\cdot \lambda^x e^{-\lambda T} \cdot \frac{\alpha^r \lambda^{r-1} e^{-\alpha\lambda}}{\Gamma(r)}
\;\propto\; \lambda^{(r+x)-1} e^{-(\alpha + T)\lambda}
$$

La integral sobre $p$ no depende de $\lambda$ gracias a la independencia (supuesto v),
así que se va en la constante. Lo que queda es el núcleo de una Gamma:

$$
\lambda \mid \text{vivo}, x, t_x, T \;\sim\; \text{Gamma}(r + x,\; \alpha + T)
$$

*Interpretación:* cada compra suma 1 a la forma y cada semana observada suma 1 a la
tasa. Un cliente que compró mucho en poco tiempo tiene una $\lambda$ posterior alta.

### Paso 4: promediar sobre $\lambda$ (pista 3)

Con la identidad de 1.2, $\int_0^\infty \lambda^{k-1} e^{-c\lambda}\, d\lambda = \Gamma(k)/c^k$:

$$
P(Z = 0 \mid \text{vivo}) = \int_0^\infty e^{-\lambda\tau}
\frac{(\alpha+T)^{r+x} \lambda^{r+x-1} e^{-(\alpha+T)\lambda}}{\Gamma(r+x)}\, d\lambda
= \frac{(\alpha+T)^{r+x}}{\Gamma(r+x)} \cdot \frac{\Gamma(r+x)}{(\alpha+T+\tau)^{r+x}}
= \left(\frac{\alpha+T}{\alpha+T+\tau}\right)^{r+x}
$$

Es la probabilidad de cero de una binomial negativa: la mezcla gamma–Poisson.

### Paso 5: juntar

$$
P(Z = 0) = 1 - P(\text{vivo}) + P(\text{vivo}) \left(\frac{\alpha+T}{\alpha+T+\tau}\right)^{r+x}
$$

y por lo tanto

$$
\boxed{P(Z = 1 \mid x, t_x, T) = P(\text{vivo} \mid x, t_x, T) \left[ 1 - \left(\frac{\alpha+T}{\alpha+T+\tau}\right)^{r+x} \right]}
$$

**Comprobaciones:** con $\tau = 0$ da $0$ (no hay tiempo para comprar); conforme
$\tau \to \infty$ tiende a $P(\text{vivo})$ (un vivo tarde o temprano compra); y
siempre $P(Z = 1) \le P(\text{vivo})$.

### Preguntas posibles

- **¿Por qué $P(\text{vivo})$ no sirve como probabilidad de comprar?** Porque estar vivo
  es necesario pero no suficiente: un cliente vivo con $\lambda$ pequeña puede pasar 39
  semanas sin comprar. El factor entre corchetes es justamente la probabilidad de que un
  vivo compre al menos una vez.
- **¿Por qué es importante que un vivo que no compra siga vivo?** Porque garantiza que
  la tasa $\lambda$ no cambia durante el holdout mientras no compre, y eso permite usar
  directamente $e^{-\lambda\tau}$. En un modelo donde se puede morir en cualquier
  momento, como el Pareto/NBD, esta cuenta cambiaría.
- **¿Por qué la posterior de $\lambda$ no depende de $t_x$?** Porque, dado que está vivo,
  la historia es la A, cuya parte en $\lambda$ es $\lambda^x e^{-\lambda T}$: solo
  importan $x$ y $T$. La información de $t_x$ ya entró a través de $P(\text{vivo})$.
- **¿Por qué la fórmula sigue valiendo para el MBG/NBD (4.6)?** Porque los pasos 1 a 4
  solo usan que un vivo que no compra sigue vivo y que, dado vivo, la parte en $\lambda$
  es $\lambda^x e^{-\lambda T}$. Ambos se cumplen también en el MBG/NBD; solo cambia
  $P(\text{vivo})$.