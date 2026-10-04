# Guion de YouTube — investigación del stuttering DX12 en ETS2 1.61

**Duración aproximada:** 8–12 minutos  
**Investigación técnica original:** NemoByteCore  
**Propósito:** guion comunitario listo para creadores; puede adaptarse libremente siempre que se mantengan el alcance y las limitaciones de la evidencia.

> Antes de publicar, conviene revisar el repositorio por si NemoByteCore ha actualizado la redacción, las evidencias o las conclusiones.

## 0:00–0:45 — Gancho

**Visual:** conducción normal en ETS2 con contador de FPS aparentemente estable; luego mostrar un pico de frametime o un tirón.

**Narración:**

Euro Truck Simulator 2 puede parecer que funciona a 60 FPS y, aun así, congelarse durante una fracción de segundo. A esos tirones solemos llamarlos “stuttering”, pero esa palabra puede describir muchos problemas distintos.

Un jugador, NemoByteCore, decidió no limitarse a probar configuraciones al azar. Instrumentó la ruta de renderizado DX12 de ETS2 1.61.1.1, correlacionó los picos de tiempo de frame dentro del renderer y encontró una clase concreta de bloqueo interno que pudo medir y reproducir.

Y esto es importante: este video **no** afirma que haya encontrado la causa de todos los tirones de ETS2 o ATS. Encontró una causa concreta dentro de una ruta documentada, y las evidencias son públicas.

## 0:45–2:10 — Qué es un PSO y por qué importa el tiempo de frame

**Visual:** diagrama sencillo: presupuesto de 16,67 ms a 60 FPS y preparación de PSO ocupando parte del frame.

**Narración:**

El problema involucra algo llamado Graphics Pipeline State Object, o PSO. Simplificando, un PSO reúne configuración que la GPU necesita para realizar un determinado tipo de dibujo.

Si el juego ya tiene ese PSO preparado, puede utilizarlo rápidamente. Pero si está frío y el juego debe crearlo justo cuando el frame lo necesita, ese trabajo puede ser costoso.

NemoByteCore localizó una ruta donde un PSO frío llega al camino de dibujo y el juego ejecuta su creación con una espera síncrona.

La investigación midió repetidamente bloqueos de aproximadamente 10 a más de 40 milisegundos.

A 60 FPS, todo el frame dispone de unos 16,67 milisegundos. Por eso una operación bloqueante de 20, 30 o 40 ms puede producir un tirón claramente visible aunque el promedio de FPS siga pareciendo bueno.

## 2:10–3:20 — La ruta documentada

**Visual:** mostrar la cadena de funciones del repositorio.

```text
FUN_1402A06D0
  -> FUN_1402AAA60
      -> FUN_14029DD00(..., wait=1)
```

**Narración:**

Esta es la ruta relevante que NemoByteCore documentó en ETS2 1.61.1.1. Los nombres son identificadores de ingeniería inversa, no nombres oficiales publicados por SCS.

El detalle clave es `wait=1`. Cuando hay un fallo de caché, la ruta de dibujo espera a que termine la creación del PSO antes de poder continuar.

Pero NemoByteCore encontró algo todavía más interesante: el mismo ejecutable ya contiene otra ruta capaz de solicitar preparación de PSO sin bloquear al llamador.

```text
FUN_14029E0F0
  -> FUN_14029DD00(..., wait=0)
```

Así que la siguiente pregunta era obvia: ¿los PSO que después provocan los bloqueos síncronos lentos están pasando previamente por esa ruta asíncrona?

## 3:20–4:30 — El resultado 27/27

**Visual:** “27 / 27” en grande y los cuatro contadores.

```text
async_total = 0
slow_total  = 27
slow_seen   = 0
slow_unseen = 27
```

**Narración:**

En la ejecución final de cobertura aceptada, NemoByteCore registró 27 PSO lentos en la ruta síncrona.

Los 27 no habían sido vistos previamente por la ruta de preparación asíncrona monitorizada antes de su primer uso.

Ese es el resultado 27 de 27 que probablemente verás citado.

No significa que todos los PSO de ETS2 estén afectados. Significa que, en esa ejecución medida, todos los PSO lentos que llegaron a esta ruta de bloqueo lo hicieron sin cobertura previa observada del mecanismo asíncrono integrado.

## 4:30–5:35 — La prueba que parece una solución, pero no lo es

**Visual:** `wait=1` cambia a `wait=0`; después describir o mostrar los flashes negros/renderizado incompleto.

**Narración:**

NemoByteCore probó la idea evidente: ¿qué pasa si simplemente dejamos de esperar?

Cambió la llamada relevante de `wait=1`, síncrona, a `wait=0`, asíncrona.

Los grandes bloqueos síncronos desaparecieron.

Pero el renderizado se rompió. Los PSO fríos podían seguir preparándose cuando el juego ya los necesitaba, por lo que algunas operaciones de dibujo se omitían y aparecían flashes negros o elementos sin renderizar.

Por eso esto no es un parche de una línea para jugadores.

El experimento demuestra algo más útil: el trabajo costoso puede hacerse de forma asíncrona, pero debe comenzar con suficiente anticipación para que el PSO esté listo **antes del primer dibujo que lo necesita**.

## 5:35–6:25 — Qué está demostrado y qué no

**Visual:** pantalla dividida “DEMOSTRADO / NO DEMOSTRADO”.

**Narración:**

Aquí está la limitación más importante.

Las evidencias permiten concluir que NemoByteCore demostró una clase de stuttering interna al motor en ETS2 1.61.1.1 bajo DX12, donde la creación de PSO fríos bloquea síncronamente la ruta de dibujo.

Las evidencias no demuestran que todos los tirones de ETS2 sean este mismo fallo. No demuestran que ATS se comporte exactamente igual. No demuestran que DX11 tenga la misma causa. Y tampoco demuestran que todas las quejas de rendimiento de la comunidad provengan de esta ruta concreta.

Esa limitación no debilita el hallazgo. Lo hace preciso.

## 6:25–7:35 — La respuesta en el foro de SCS

**Visual:** capturas archivadas del foro y enlace a `evidence/forum`.

**Narración:**

NemoByteCore llevó después la investigación al foro oficial de SCS.

La conversación terminó centrada en la ausencia de un `game.log.txt`, el hilo fue bloqueado y su título quedó marcado como “NOT A BUG”. El repositorio conserva capturas y una copia archivada del intercambio.

Un game log puede ser muy útil para diagnosticar hardware, configuración, mods o errores de scripts. Pero no contiene las correlaciones del profiler, los tiempos internos del hilo de renderizado ni la instrumentación de cobertura asíncrona utilizada aquí.

Por eso la petición razonable no es “dejen de pedir logs”. Es: cuando alguien aporta profiling a nivel de funciones y experimentos controlados, evalúen esas evidencias en el nivel técnico en que fueron producidas.

## 7:35–9:00 — ¿Qué debería investigar SCS?

**Visual:** mostrar la pregunta central del proyecto.

**Narración:**

A estas alturas, la pregunta de ingeniería ya no es simplemente “¿dónde ocurre el tirón?”.

Es: ¿por qué los PSO gráficos están llegando fríos a la ruta síncrona de dibujo, mientras un mecanismo de preparación asíncrona que ya existe no los está cubriendo antes del primer uso?

La investigación propone varias direcciones que SCS puede evaluar internamente: detectar y preparar los PSO con mayor anticipación, ampliar el uso de la ruta asíncrona existente, utilizar una caché persistente adecuada si la arquitectura lo permite y evitar que el hilo de renderizado tenga que esperar por PSO fríos durante la conducción normal.

La solución exacta corresponde a SCS porque solo SCS controla el motor.

## 9:00–10:10 — El problema más amplio

**Visual:** evolución de ETS2/ATS, actualizaciones gráficas y referencias a Prism3D.

**Narración:**

Y por eso esta historia importa más allá de una sola ruta DX12.

SCS ha reconocido públicamente la antigüedad y la deuda técnica acumulada de su motor. Eso no demuestra que todos los problemas de rendimiento tengan la misma causa, pero convierte la modernización del renderer y la estabilidad de los tiempos de frame en preguntas totalmente legítimas para el futuro de ETS2 y ATS.

La comunidad no necesita que SCS acepte automáticamente cada interpretación del repositorio. Una respuesta técnica útil podría reproducir el resultado, refutarlo con evidencias, corregir el camino de preparación o explicar cómo se está modificando el renderer.

Lo importante es que evidencia técnica reciba una respuesta técnica.

## 10:10–final — Cierre y crédito

**Visual:** repositorio de NemoByteCore, carpetas de evidencias y enlace/QR.

**Narración:**

La investigación original fue realizada por NemoByteCore. Su repositorio contiene las mediciones, las notas de instrumentación, las evidencias runtime, los caminos que no funcionaron y el alcance exacto del resultado.

Si quieres juzgar el caso por ti mismo, no te quedes solamente con este video. Revisa el repositorio.

Y recuerda la conclusión correctamente: NemoByteCore no demostró la causa de todos los tirones de ETS2. Demostró una clase medible de stuttering interna al motor en ETS2 1.61.1.1 bajo DX12, y dejó suficientes evidencias para que SCS —o cualquier persona que reproduzca esa misma versión— pueda examinarla.

El enlace a la investigación original está en la descripción.

---

## Bloque de crédito para la descripción

> **Investigación técnica original:** NemoByteCore  
> Repositorio: `NemoByteCore/ets2-1.61-stutter-investigation`  
> Este video/guion es una explicación comunitaria de la investigación pública. El repositorio sigue siendo la fuente técnica canónica.
