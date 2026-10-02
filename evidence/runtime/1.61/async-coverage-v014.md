# Built-in async PSO preparation coverage — v0.14

This was the final targeted coverage experiment.

## Question

ETS2 already contains an asynchronous PSO preparation path:

```text
FUN_14029E0F0
-> FUN_14029DD00(..., wait=0)
```

The synchronous draw path is:

```text
FUN_1402AAA60
-> FUN_14029DD00(..., wait=1)
```

The v0.14 probe recorded keys submitted through the built-in async path and compared them with PSOs that later produced slow synchronous AAA60 lookups.

The probe did not change rendering behavior.

## Accepted result

One normal run produced:

```text
async_total = 0
slow_total  = 27
slow_seen   = 0
slow_unseen = 27
```

All 27 measured slow AAA60 PSOs reached synchronous first use without prior observation on the built-in async preparation path.

Representative synchronous stalls from that run included:

```text
9.958 ms
10.331 ms
11.247 ms
11.617 ms
11.990 ms
12.821 ms
13.303 ms
14.674 ms
16.416 ms
19.936 ms
22.351 ms
```

## Interpretation

For this accepted run, the measured slow states were not being prepared by the existing async path before first draw.

That is the final engineering question left by this investigation:

> Why are graphics PSOs reaching `FUN_1402AAA60` cold and forcing `FUN_14029DD00(..., wait=1)`, while the existing `FUN_14029E0F0` asynchronous preparation path is not covering those PSOs before first use?

## Evidence limitation

The private project history preserves the probe definition and the accepted summarized result, but the raw v0.14 runtime CSV is not present in the repository archive being published from.

Accordingly, this page does not claim that a raw v0.14 capture is available here.

The result is one accepted normal drive covering 27 measured slow PSOs. It should not be generalized into a claim about every PSO in every possible workload.
