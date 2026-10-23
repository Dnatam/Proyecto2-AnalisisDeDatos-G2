# Parte 0 — Respuestas

**0.4 ¿Qué fracción no volvió a comprar en calibración?**
El 59.9 % de los clientes (1,411 de 2,357) tiene x = 0: no hizo ninguna compra
repetida entre su primera compra y el 30 de septiembre de 1997.

**¿Por qué T es distinto para cada cliente?**
Porque los clientes hicieron su primera compra en días distintos del primer
trimestre de 1997, pero la calibración termina el mismo día para todos
(30 de septiembre). T mide cuánto tiempo observamos a cada cliente desde su
primera compra: quien llegó el 1 de enero tiene T = 38.86 semanas y el último
cliente de la cohorte (25 de marzo) tiene T = 27.

Intuitivamente, un cliente con x = 0 y T grande debería ser más "sospechoso" de
haberse ido que uno con x = 0 y T pequeño, porque hemos tenido más tiempo para
verlo volver. Sin embargo, el BG/NBD no puede capturar esto: como un cliente
solo puede morir justo después de una compra repetida, todo cliente con x = 0
tiene P(vivo) = 1 sin importar su T (ver inciso 4.2).