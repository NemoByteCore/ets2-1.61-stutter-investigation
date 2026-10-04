# Stuttering DX12 en ETS2 1.61 — guía para creadores

**Recurso comunitario de divulgación basado en la investigación original de NemoByteCore.**

La investigación técnica resumida aquí fue realizada y publicada por **NemoByteCore**. La ingeniería inversa, instrumentación, correlación con profiler, pruebas A/B, mediciones y archivo de evidencias son trabajo suyo. Este documento existe únicamente para facilitar que ese trabajo pueda explicarse correctamente a una audiencia más amplia.

> **Importante:** este documento no sustituye al registro técnico canónico. Para verificar los datos, consulta la [investigación principal](../../README.md) y las [evidencias runtime aceptadas de 1.61](../../evidence/runtime/1.61/README.md).

## La versión corta

NemoByteCore investigó picos recurrentes en los tiempos de frame de **Euro Truck Simulator 2 1.61.1.1 usando DX12** y localizó una clase reproducible de stuttering en la **creación síncrona, dentro de la ruta de dibujo, de Graphics Pipeline State Objects (PSO) que todavía estaban fríos**.

Ante un fallo de caché, la ruta documentada llega a:

```text
FUN_1402A06D0
  -> FUN_1402AAA60
      -> FUN_14029DD00(..., wait=1)
```

Con `wait=1`, la ruta de dibujo espera a que termine la creación del PSO antes de continuar. La investigación midió repetidamente bloqueos de PSO fríos en el rango aproximado de **10 a más de 40 ms**.

A 60 FPS, el presupuesto nominal por frame es de unos **16,67 ms**. Un trabajo inesperado de 20, 30 o 40 ms en la ruta crítica puede producir un tirón visible aunque el contador promedio de FPS siga pareciendo normal.

## Por qué importa el resultado 27/27

La misma versión de ETS2 contiene una ruta de preparación asíncrona de PSO:

```text
FUN_14029E0F0
  -> FUN_14029DD00(..., wait=0)
```

NemoByteCore instrumentó esa ruta y la comparó con los PSO que posteriormente producían bloqueos lentos en la ruta síncrona.

La ejecución final aceptada registró:

```text
async_total = 0
slow_total  = 27
slow_seen   = 0
slow_unseen = 27
```

En esa ejecución, **27 de 27 PSO lentos medidos no habían sido observados pasando por la ruta asíncrona integrada antes de su primer uso**.

Eso no significa que “todos los PSO del juego estén rotos”. Significa que, para la clase de stuttering medida en esa ejecución, los PSO que después bloquearon la ruta de dibujo estaban llegando fríos en vez de ser preparados previamente por el mecanismo asíncrono existente.

## La prueba A/B

NemoByteCore también cambió la consulta relevante de:

```text
FUN_14029DD00(..., wait=1)
```

a:

```text
FUN_14029DD00(..., wait=0)
```

Los grandes bloqueos síncronos desaparecieron.

Pero **no era una solución utilizable**. Un PSO frío puede seguir sin estar listo mientras la compilación/preparación continúa, lo que provocó operaciones de dibujo omitidas, flashes negros y renderizado incompleto.

El valor del experimento es que acota el problema de ingeniería:

- el trabajo costoso puede sacarse de la ruta crítica de dibujo;
- simplemente negarse a esperar no basta;
- los PSO necesarios deben descubrirse y prepararse **antes de su primer uso**.

Eso requiere una solución dentro del motor, no un ajuste de configuración del usuario.

## Qué demuestra la investigación

Es correcto afirmar que:

- NemoByteCore demostró una **clase de stuttering interna al motor** y reproducible en ETS2 1.61.1.1 bajo DX12;
- se observó creación de PSO gráficos fríos bloqueando síncronamente la ruta de dibujo;
- esos bloqueos fueron medibles y suficientemente grandes para alterar la regularidad de los frames;
- la versión investigada ya contiene un mecanismo de preparación asíncrona de PSO;
- en la ejecución final de cobertura, los 27 PSO lentos medidos llegaron posteriormente a la ruta síncrona sin cobertura previa observada de esa ruta asíncrona;
- forzar a que la consulta final fuera asíncrona eliminó los grandes bloqueos, pero rompió el renderizado, demostrando que la preparación debe ocurrir antes y no simplemente eliminar la espera;
- la clase de bloqueo fue reproducida tanto en ETS2 sin mods como con mods, por lo que los mods no eran necesarios para provocarla.

## Qué **no** demuestra

No conviertas el resultado en afirmaciones como:

- “NemoByteCore encontró la causa de todo el stuttering de ETS2”.
- “Todos los tirones de ATS tienen la misma causa”.
- “Se demostró que DX11 tiene exactamente este mismo fallo de PSO”.
- “27/27 significa que todos los PSO de ETS2 están afectados”.
- “Cambiar `wait=1` por `wait=0` es una solución para jugadores”.
- “La investigación demuestra que todas las quejas de rendimiento de la comunidad provienen de esta ruta”.

El alcance demostrado es más limitado y, precisamente por eso, más sólido: **una clase concreta, medible y reproducible de stuttering fue localizada dentro de la ruta de renderizado DX12 de ETS2 1.61.1.1**.

## Qué ocurrió en el foro de SCS

NemoByteCore publicó los hallazgos en el foro oficial de SCS. El hilo terminó recibiendo una nota de moderación centrada en la ausencia de `game.log.txt`, fue bloqueado y su título quedó marcado como **[NOT A BUG]**. El repositorio conserva capturas y un archivo externo del intercambio.

Un `game.log.txt` es útil para muchas tareas de soporte: identificar hardware, configuración, mods, errores de scripts y el entorno general. Pero no contiene por sí mismo los tiempos internos del hilo de renderizado, la correlación a nivel de funciones ni las mediciones de cobertura asíncrona utilizadas en esta investigación.

Por eso el mensaje correcto no es “los logs no sirven”. Es:

> Cuando un reporte incluye evidencias de profiler, pruebas A/B controladas e instrumentación de la ruta de renderizado, esas evidencias merecen una respuesta técnica del mismo nivel.

Consulta el [archivo de evidencias del foro](../../evidence/forum/README.md).

## La cuestión más amplia de Prism3D

La investigación trata de una clase específica de bloqueo en DX12, pero también plantea una pregunta más amplia sobre la arquitectura del renderer y la deuda técnica.

SCS ha hablado públicamente de la antigüedad y la deuda técnica acumulada de su motor. Eso **no** demuestra por sí solo que todos los problemas de rendimiento compartan la misma causa arquitectónica. Sí hace razonable preguntar cómo piensa SCS impedir que trabajo costoso y sensible a la latencia termine bloqueando el frame a medida que ETS2 y ATS continúan evolucionando.

La pregunta de ingeniería que deja planteada el proyecto es muy concreta:

> ¿Por qué los PSO gráficos llegan fríos a la ruta síncrona de dibujo mientras la ruta asíncrona existente no los está cubriendo antes del primer uso?

Entre las posibles direcciones señaladas por la investigación están mejorar la detección y precarga de PSO, utilizar antes la ruta asíncrona existente, persistir una caché adecuada cuando la arquitectura lo permita y evitar esperas del hilo de renderizado por creación de PSO fríos durante la conducción normal.

## Qué puede pedir razonablemente la comunidad a SCS

Una respuesta técnicamente seria no obliga a SCS a aceptar automáticamente todas las conclusiones. Podría consistir en:

- reproducir o refutar la ruta medida;
- explicar por qué la interpretación de cobertura asíncrona es incorrecta, si lo es;
- corregir el camino de preparación;
- mostrar mejoras medibles en los tiempos de frame;
- documentar el futuro previsto de los renderizadores DX11/DX12;
- explicar cómo se detectan regresiones de rendimiento y picos de frametime;
- describir cómo se está modernizando la arquitectura gráfica de Prism3D cuando resulte necesario.

La petición no es “denle la razón a la comunidad”. La petición es **responder evidencia técnica con evidencia técnica**.

## Guía para creadores

### Formulaciones recomendables

Puedes decir:

- “NemoByteCore demostró una fuente concreta de stuttering interno al motor en ETS2 1.61.1.1 bajo DX12”.
- “La investigación midió creación de PSO fríos bloqueando la ruta de dibujo”.
- “En la ejecución final de cobertura, 27/27 PSO lentos medidos no habían sido vistos previamente en la ruta asíncrona integrada”.
- “La prueba que eliminó la espera también rompió el renderizado, así que no es un parche simple para usuarios”.
- “El hallazgo no explica todos los tirones de ETS2 ni ATS”.

### Evita

Evita titulares o narraciones como:

- “Por fin descubrieron la causa del stuttering de ETS2”.
- “SCS hace que el juego tenga stuttering a propósito”.
- “Esto demuestra que todo problema de rendimiento es culpa de Prism3D”.
- “Esta es la solución de una línea que SCS se niega a aplicar”.

La evidencia ya es fuerte. Exagerarla solo facilita que alguien descarte el resultado real.

## Títulos sugeridos

- **Un jugador rastreó un stutter de ETS2 1.61 hasta el renderer DX12**
- **NemoByteCore encontró un stuttering medible dentro del motor de ETS2 1.61**
- **27/27: qué encontró realmente la investigación del stuttering DX12 de ETS2**
- **ETS2 puede marcar 60 FPS y aun así dar tirones: esta es una causa demostrada**

## Fuentes primarias

Para consultar las evidencias completas y el texto vigente:

- [README principal de la investigación](../../README.md)
- [Evidencias runtime aceptadas de 1.61](../../evidence/runtime/1.61/README.md)
- [Manifesto](../../MANIFESTO.md)
- [What we want from SCS](../../WHAT_WE_WANT_FROM_SCS.md)
- [Rastreador comunitario de stuttering](../../COMMUNITY_STUTTER_TRACKER.md)
- [Archivo de evidencias del foro](../../evidence/forum/README.md)

## Atribución

Si utilizas o compartes esta guía, deja clara la fuente original:

> **Investigación técnica original: NemoByteCore — `ets2-1.61-stutter-investigation`**

Enlazar directamente al repositorio permite que espectadores y lectores revisen las evidencias por sí mismos.
