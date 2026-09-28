# Static diff: ETS2 1.60 -> 1.61

This document records the static mapping used to carry the earlier 1.60 investigation forward without reusing 1.60 addresses.

## Corpus

The same Ghidra harvester format was generated for both builds.

| Build | Harvested functions |
|---|---:|
| 1.60 corpus | 68,834 |
| 1.61.1.1 | 70,694 |

A normalized pseudocode fingerprint pass found only 118 unique exact matches, all at the same addresses. That is not enough by itself to drive a port.

Useful mapping came from a combination of:

- normalized pseudocode similarity;
- function size;
- call degree;
- external-call similarity;
- direct caller/callee structure;
- instruction-level validation in the 1.61 Ghidra project.

## High-confidence lower-region mapping

| 1.60 role | 1.60 VA | 1.61 VA | Auto score | Notes |
|---|---:|---:|---:|---|
| nested winner | `1413BB140` | `141473E60` | 0.9693 | same size, strong structure |
| RQ_PREP | `14154C370` | `14160C990` | 0.9622 | same size |
| RQ_ONE | `14154C9F0` | `14160D010` | 0.9737 | same size and call structure |
| HEAD_DISPATCH | `14154CF60` | `14160D580` | 0.9297 | same size |
| downstream dispatch | `1402D8D20` | `1402E5FF0` | 0.9485 | same size |
| BUNDLE_BUILD | `1402D7D70` | `1402E5040` | 0.9510 | same size |
| DX12 descriptor builder | `1402942D0` | `14029F9B0` | 0.8428 | same size |
| descriptor heap allocator | `14028F070` | `14029A330` | 0.8612 | same size |
| semantic/resource resolver | `1402E25A0` | `1402EF660` | 0.8823 | same size |
| root-table submission | `14029E1F0` | `1402AAA60` | 0.8942 | same size |
| descriptor heap setup | `14028EBE0` | `140299EA0` | 0.9456 | same size |
| uniform merge helper | `14144C160` | `141508B30` | 0.9490 | same size |
| uniform/resource context setup | `14144C770` | `141509140` | 0.9557 | same size |

Preserved direct lower edges:

```text
141473E60
    -> 14160D010
        -> 14160D580
            -> 1402E5FF0
```

That is substantially stronger evidence than text similarity alone.

## Main loop / coordinator mapping

| 1.60 role | 1.60 VA | 1.61 VA | Auto score |
|---|---:|---:|---:|
| outer main-loop owner | `1401C5280` | `1401C99A0` | 0.9691 |
| LOOP | `1401C77C0` | `1401CBEE0` | 0.9260 |
| PACE | `1401C6CB0` | `1401CB3D0` | 0.9505 |
| render/present coordinator | `1401D72F0` | `1401DBCE0` | 0.6947 |
| WAIT helper | `14011F730` | `140123E50` | 0.9123 |

Verified local edges include:

```text
1401CBEE0 -> 1401DBCE0
1401DBCE0 -> 140123E50
```

The coordinator match is weaker than the LOOP/WAIT matches, so its semantic label should remain evidence-backed but cautious.

## RG_CORE / T1 reconstruction

The global fuzzy matcher initially proposed:

```text
old RG_CORE 14021FE20 -> 14134F3D0   score 0.5657, margin 0.0167
old T1      14021F560 -> 1415C5B90   score 0.6022, margin 0.0306
```

Those candidates were rejected as too weak.

The branch was then reconstructed locally from the mapped coordinator.

### Old 1.60 shape

```text
coordinator
  -> RG_CORE 14021FE20 (2279 bytes)
       -> T1 14021F560 (538 bytes)
```

Old T1 had five ordinary children sized approximately:

```text
87, 157, 305, 214, 300 bytes
```

### 1.61 local topology

The mapped 1.61 coordinator directly calls:

```text
140227140 (4259 bytes)
```

This function contains the characteristic synchronization behavior involving:

- `AcquireSRWLockExclusive`
- `ReleaseSRWLockExclusive`
- `SleepConditionVariableSRW`
- `_alloca_probe`

It directly calls:

```text
140226960 (728 bytes)
```

That function has five ordinary children sized:

```text
157, 217, 214, 305, 300 bytes
```

Four child sizes line up closely with the old T1 subtree.

The direct harvested topology is:

```text
1401DBCE0 -> 140227140 -> 140226960
```

Current working semantic labels:

```text
140227140 = RG-owner candidate
140226960 = T1-like candidate
```

These labels are still hypotheses. The direct relationships are facts.

## Direct-call gap explained by indirect dispatch

The initial public write-up was right to retract the unexplained `...`.

A direct-call BFS still returns:

```text
PATH_FOUND=False
```

for `140226960 -> 141473E60` through depth 12.

The follow-up static pass recovered the missing architecture.

### T1-like callsite

`140226960` loads the callback from owner field `+0x1C68` and calls vtable slot `+0x8`.

### Adapter

`1414752E0` installs an adapter with vtable:

`1421FD1B0`

into render-queue data `+0x1C68`.

Adapter slot `+0x8` points to `14022EAA0`, which forwards:

```text
MOV RCX,[RCX+0x110]
MOV RAX,[RCX]
JMP [RAX+0x8]
```

### Contained callback

`141473A00` builds the source callback with vtable:

`1423F5530`

Raw callsite analysis shows that callback wrapper is passed into `1414752E0`.

Source vtable `+0x10` points to `141476150`, which clones the callback while writing the same vtable `1423F5530`.

The clone is stored at adapter `+0x110`.

### Winner

Source/clone vtable slot `+0x8` points to:

`141476140`

which is a thunk:

```text
JMP 141473E60
```

### Correct current chain

```text
1401CBEE0  LOOP
  -> 1401DBCE0  coordinator
      -> 140227140  RG-owner candidate
          -> 140226960  T1-like
              -> [owner+0x1C68]
              -> adapter 1421FD1B0 +8
              -> 14022EAA0
              -> contained callback 1423F5530 +8
              -> 141476140
              -> 141473E60  substantive winner
                  -> 14160D010  RQ_ONE
                      -> 14160D580  HEAD_DISPATCH
                          -> 1402E5FF0  downstream
                              -> lower render/descriptor work
```

The earlier negative direct-call result remains useful: it explains why the automatic call graph could not recover this middle section.

## Implication for runtime work

The static chain is now recovered. Future tracing should answer which part of that chain, if any, actually coincides with the visible frame spike, and whether elapsed time represents CPU work, synchronization/waiting, GPU/present blocking or an external stall.

That is why the project is moving toward broader ETW/Present/GPU evidence before another long sequence of narrow hook versions.
