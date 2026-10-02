# Cold-key behavior and PSO prewarm negative results

These experiments tested whether a static list of previously slow PSO keys could be prepared ahead of gameplay.

They are preserved as negative evidence. They are not recommended fixes.

## Targeted meta-blit check

A short side branch tested whether earlier rare 8-9 ms meta-blit events were reproducible as `FUN_1402A9AF0` PSO-creation stalls.

First-use pairs observed in the targeted run took:

```text
640 us
54 us
617 us
30 us
224 us
37 us
```

No `FUN_1402A9AF0` call reached 1 ms.

Conclusion: that targeted run did not reproduce meta-blit PSO creation as the primary stall source, so the investigation returned to AAA60.

## v0.11 — cold-key pattern

Accepted capture:

```text
RG events                    24,369
rg_lost                           0
AAA60 PSO lookup calls   50,530,630
slow calls >=1 ms                26
unique slow keys                 26
duplicate slow keys               0
>=4 ms                            16
>=8 ms                            12
>=16 ms                            3
max                           22.997 ms
```

All slow calls used `wait=1` and returned concrete pipeline-state indices.

No captured slow key was observed becoming slow a second time in the run.

Interpretation: strong cold first-use behavior.

## v0.12 — prewarm fired before dependencies were ready

The first static prewarm attempt queued the 26 known keys too early.

At trigger time:

```text
shader pipeline registry count   548
highest required captured index  881
minimum count needed              882
```

The engine reported out-of-range shader-pipeline indices and the run crashed.

This experiment was rejected immediately.

Its useful result was the readiness constraint: a PSO key cannot safely be prepared merely because the lookup function is reachable; the dependent registries must already contain everything referenced by that key.

## v0.13 — gated synchronous prewarm

The next experiment waited until:
- shader pipeline count reached 882;
- that count remained stable for 512 consecutive AAA60 lookups;
- per-key dependencies validated.

It then prewarmed at most one known PSO per AAA60 lookup using normal synchronous `wait=1` behavior.

Result:

```text
previously captured keys prewarmed   26 / 26
prewarm failures                      0

slow prewarm calls:
6.649 ms
7.152 ms
35.062 ms
```

Despite successfully warming every previously captured key, the later drive still contained 20 slow current-draw PSO calls >=1 ms.

They were different cold keys from the previous run.

Representative new stalls included:

```text
42.128 ms
38.193 ms
34.922 ms
24.594 ms
18.762 ms
14.207 ms
13.096 ms
12.790 ms
12.529 ms
12.473 ms
12.390 ms
12.283 ms
```

## Conclusion

A static previous-drive key list is not a general solution:
- the cold PSO set changes with workload/content;
- synchronous prewarm can simply move the compile stall earlier;
- preparation has real dependency/readiness requirements.

This does not disprove engine-side prewarming in general.

It rejects the external hard-coded key-list approach and points toward generic discovery/preparation before first render-thread use, or an appropriate persistent cache mechanism.
