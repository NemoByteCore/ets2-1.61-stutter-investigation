# Static diff: ETS2 1.60 -> 1.61

This document records the static mapping used to carry the earlier 1.60 investigation forward without reusing 1.60 addresses.

## Corpus

The same Ghidra harvester format was generated for both builds.

| Build | Harvested functions |
|---|---:|
| 1.60 corpus | 68,834 |
| 1.61.1.1 | 70,694 |

A normalized pseudocode fingerprint pass found only 118 unique exact matches, all at the same addresses. That is intentionally not enough to drive the port.

The useful mapping came from a combination of:

- normalized pseudocode similarity,
- function size,
- call degree,
- external-call similarity,
- direct caller/callee structure,
- instruction-level validation in the 1.61 Ghidra project.

## High-confidence lower-chain mapping

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

The important lower runtime sequence is also preserved by direct call-graph edges:

```text
141473E60
    -> 14160D010
        -> 14160D580
            -> 1402E5FF0
```

This is substantially stronger evidence than text similarity alone.

## Main loop / coordinator mapping

| 1.60 role | 1.60 VA | 1.61 VA | Auto score |
|---|---:|---:|---:|
| outer main-loop owner | `1401C5280` | `1401C99A0` | 0.9691 |
| LOOP | `1401C77C0` | `1401CBEE0` | 0.9260 |
| PACE | `1401C6CB0` | `1401CB3D0` | 0.9505 |
| render/present coordinator | `1401D72F0` | `1401DBCE0` | 0.6947 |
| WAIT helper | `14011F730` | `140123E50` | 0.9123 |

The 1.61 loop directly calls the mapped coordinator:

```text
1401CBEE0 -> 1401DBCE0
```

The mapped coordinator also calls the mapped WAIT helper:

```text
1401DBCE0 -> 140123E50
```

## Important correction: RG_CORE / T1

The global fuzzy matcher initially proposed:

```text
old RG_CORE 14021FE20 -> 14134F3D0   score 0.5657, margin 0.0167
old T1      14021F560 -> 1415C5B90   score 0.6022, margin 0.0306
```

Those scores and margins are too weak to accept.

Instead, the mapping was reconstructed from the already mapped coordinator and local call structure.

### Old 1.60 shape

```text
coordinator
  -> RG_CORE 14021FE20 (2279 bytes)
       -> T1 14021F560 (538 bytes)
```

Old T1 had five ordinary children, including functions sized:

```text
87, 157, 305, 214, 300 bytes
```

### 1.61 structural candidate

The mapped 1.61 coordinator directly calls:

```text
140227140 (4259 bytes)
```

This function preserves the characteristic synchronization shape:

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

Four child sizes line up almost exactly with the old T1 subtree, while one branch is enlarged.

Current working labels are therefore:

```text
140227140 = RG owner candidate
140226960 = T1-like helper
```

These are stronger than the original global fuzzy candidates, but the labels remain hypotheses until runtime correlation confirms where the spike cost appears.

## Current working chain

```text
1401CBEE0  LOOP
  -> 1401DBCE0  render/present coordinator
      -> 140227140  RG owner candidate
          -> 140226960  T1-like
              -> ...
                  -> 141473E60  substantive winner
                      -> 14160D010  RQ_ONE
                          -> 14160D580  HEAD_DISPATCH
                              -> 1402E5FF0  downstream
                                  -> 1402E5040  BUNDLE_BUILD
                                      -> 14029F9B0  descriptor builder
```

The purpose of the runtime probe is to test this chain as one hypothesis, not to declare it the root cause in advance.
