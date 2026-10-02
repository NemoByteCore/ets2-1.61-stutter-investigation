# Controlled PSO wait-flag A/B

This experiment tested the mechanism inside the already-localized `FUN_1402AAA60` path.

## Relevant paths

Normal draw path:

```text
FUN_1402A06D0
-> FUN_1402AAA60
-> FUN_14029DD00(..., wait=1)
```

The engine also supports a non-blocking form of the same lookup:

```text
FUN_14029DD00(..., wait=0)
```

The proof-of-concept changed only the AAA60 lookup from synchronous waiting to the existing asynchronous behavior.

## Accepted A/B

Capture integrity:

```text
RG rows    27,626
rg_lost         0
```

Baseline v0.8:

```text
AAA60 max        32.255 ms
AAA60 >=8 ms     10
AAA60 >=16 ms     3
v108 max         38.408 ms
```

Forced `wait=0`:

```text
AAA60 max         5.494 ms
AAA60 >=8 ms      0
AAA60 >=16 ms     0
v108 max         13.769 ms
```

The large synchronous AAA60 stalls disappeared.

## Why this is evidence, not a final fix

On a cold PSO, the non-blocking path can return `0xFFFF` while compilation is pending. AAA60 then cannot issue that draw normally.

During the A/B run, brief black/missing-render flashes were observed.

So the experiment demonstrates that the large AAA60 stalls are tied to synchronous PSO completion on first use, but simply switching the draw call to non-blocking behavior is not a valid user-facing solution.

The PSO must be prepared before first draw if rendering is to remain complete without blocking the latency-critical draw path.
