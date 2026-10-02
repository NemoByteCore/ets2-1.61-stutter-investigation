# 1.61 DX12 localization ladder

Build:
- ETS2 1.61.1.1
- revision `6949e633e77902f7e023819d3131cc6ccce3707f`
- executable SHA-256 `EB17944139BE4DE3D70D0CD57CDAA7C52C9E326ECF2D0DD3EA2F806545C74A53`
- renderer: DX12

This page condenses the accepted runtime steps that narrowed one reproducible stutter class from broad render timing to `FUN_1402AAA60`.

It is intentionally not a dump of the private probe handoffs.

## 1. Exact frame/RG correlation

The accepted v82 capture established that anomalously long RG elapsed time was a major same-thread contributor to a subset of long frames, while other long frames remained mostly outside RG.

Strongest accepted event:

```text
frame interval  46.626 ms
RG elapsed      32.161 ms
exact overlap   32.161 ms
overlap         68.98%
frame/RG thread same
```

Separate examples existed with only about 3.8-4.6 ms of RG inside 29-35 ms frames.

Conclusion: profile inside RG for the RG-linked class, but do not claim RG explains every stutter.

See [v82 exact evidence](v82-exact-rg/SUMMARY.md).

## 2. Explicit wait/lock hypothesis rejected

The v0.4 RG subphase capture contained:

```text
RG events       44,541
subevents       23,651,287
frame events    44,755
lost events     0
```

The explicit condition-variable wait occurred only 5 times globally:

```text
WAIT_CV total   0.859 ms
WAIT_CV max     0.480 ms
```

No >=25 ms frame in the accepted result contained measurable WAIT_CV time. SRW lock acquisition was also negligible in the relevant long frames.

One important frame remained largely unclassified inside RG:

```text
frame           41.394 ms
RG              27.567 ms
T1               2.796 ms
WAIT_CV          0
unclassified RG 24.770 ms
```

Conclusion: the obvious SRW wait was not the observed long-RG mechanism in that run.

## 3. Post-T1 localization

v0.5 replaced the multi-gigabyte per-subevent stream with one compact row per RG call.

Accepted capture:

```text
RG events       51,283
frame events    53,061
lost events     0
```

Strongest post-T1 example:

```text
frame           61.196 ms
RG              49.720 ms
T1 total         3.652 ms
pre-T1           0.002 ms
inter-T1 gaps    0.037 ms
post-T1         46.028 ms
```

A separate T1-heavy class also existed:

```text
frame           32.921 ms
RG              18.232 ms
T1 total        16.517 ms
max single T1   15.168 ms
```

Conclusion: the major previously unclassified RG class was overwhelmingly after the final T1 call. Inter-T1 gaps were not the mechanism.

## 4. Measurement correction: DX11 tail probe

A v0.6 experiment initially patched six DX11 device-vtable slots while the accepted runtime was actually DX12.

All six counters stayed zero.

That result is not evidence that those phases were fast. The game log confirmed the active renderer was DX12, so the zero counters were a backend mismatch.

The backend-independent RG/T1 localization remained valid. The active DX12 backend was mapped before the next run.

This correction is kept here deliberately because it is part of the evidence discipline: a bad attribution was detected and rejected instead of being forced into the theory.

## 5. Active DX12 tail -> +0x108

The corrected v0.7 probe instrumented the active DX12 post-T1 virtual calls.

Accepted capture:

```text
RG rows                         15,551
rg_lost                              0
DX12 tail active in RG rows       100%
```

Worst RG event:

```text
RG              27.086 ms
T1               0.510 ms
post-T1         26.497 ms
DX12 +0x108     26.346 ms
```

`+0x108 -> FUN_1402A06D0` was the only measured tail phase with >=8 ms events in that capture.

Conclusion: for the post-T1 RG-linked class, `FUN_1402A06D0` was the dominant measured DX12 phase.

## 6. +0x108 -> FUN_1402AAA60

v0.8 split only `FUN_1402A06D0` using exact callsite instrumentation.

Accepted capture:

```text
RG rows             108,724
subphase rows       108,724
rg_lost                   0
```

Strongest event:

```text
RG                      39.731 ms
T1                       0.527 ms
post-T1                 39.110 ms
FUN_1402A06D0           38.408 ms
measured subphase union 35.902 ms
residual                 2.506 ms
FUN_1402AAA60           32.255 ms
```

Other large `FUN_1402A06D0` events were likewise dominated by `FUN_1402AAA60`:

```text
A06D0       AAA60
31.987 ms   30.803 ms
29.991 ms   29.069 ms
16.817 ms   15.669 ms
14.571 ms   14.138 ms
```

Across that capture:

```text
AAA60 max       32.255 ms
AAA60 >=8 ms    10 RG rows
AAA60 >=16 ms    3 RG rows
```

At this point broad localization for this class was complete:

```text
RG
-> post-T1
-> DX12 +0x108 / FUN_1402A06D0
-> FUN_1402AAA60
```

The next experiments therefore targeted the PSO lookup/wait behavior inside AAA60 rather than widening telemetry again.

## Scope limit

This ladder documents one investigated DX12 stutter class. It does not erase:
- the separate T1-heavy class;
- long frames with low RG contribution;
- other possible stutter mechanisms.

The final cold-PSO conclusion applies to the class that was narrowed through this ladder.
