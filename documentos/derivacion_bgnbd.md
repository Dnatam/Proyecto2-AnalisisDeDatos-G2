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