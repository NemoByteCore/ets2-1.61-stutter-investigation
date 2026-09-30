# Runtime results — 2026-09-29

## Historical v0.2 runs

Two earlier runs established real stutter events.

Run A:
FrameLogger max interval 33.470 ms with RG max 18.718 ms somewhere in the same five-second ChainProbe bucket.

Run B:
PresentMon captured frame intervals including:
71.7929 / 63.3167 / 53.3464 / 47.2012 / 47.0668 ms.

## Measurement correction

The old wording over-associated frame spikes with RG maxima.

v0.2 only provides approximately five-second aggregate windows.

Therefore:
- a slow frame and an RG maximum in the same bucket may be separated by seconds;
- exact per-frame RG attribution is not established by those runs;
- no root cause is claimed from that bucket-level relationship.

## Current instrumentation

NemoChainProbe161 v0.3 exact-RG:
- every RG call has exact QPC start/end and thread ID.

NemoFrameLogger v4 exact-frame:
- every valid frame interval has exact QPC start/end, segment ID and thread ID.

## Next result

For each long v4 frame interval:
- enumerate every RG interval that overlaps it;
- measure overlap;
- compare total RG time with frame duration;
- compare callback/hook thread IDs.

Decision:
- long frame dominated by RG -> inspect inside RG;
- long frame with short/non-overlapping RG -> move profiling elsewhere;
- timing points to wait/preemption but cannot classify it -> targeted ETW.

This exact-event test precedes any further broad tracing.


## Exact v0.3/v4 run

Accepted capture:
`capture_exact_v03_v04_2026-09-29_201302`

Integrity checks passed:
- RG events: 34,534, lost 0
- frame intervals: 33,214, lost 0
- both event sequences contiguous
- row counts match shutdown counters
- both streams used QPC frequency 10,000,000

Long frame-start intervals:
- >=25 ms: 12
- >=33 ms: 3
- >=50 ms: 1

The 75.689 ms maximum is the first measured interval of segment 1 and is treated as a startup/segment-transition artifact candidate.

For the remaining >=25 ms intervals:
- 9/11 overlap an RG call >=10 ms;
- 6/11 are at least 50% covered by RG elapsed time.

Strongest RG-linked example:
- frame interval 46.626 ms
- RG elapsed 32.161 ms
- exact overlap 32.161 ms (68.98%)
- frame and RG thread IDs match

Several other 28–33 ms frame intervals contain 15–22 ms RG calls, leaving roughly 11–13 ms outside RG.

However, a second class exists:
- 35.478 ms frame with only 4.599 ms RG overlap;
- 29.156 ms frame with only 3.850 ms RG overlap.

Therefore the exact run supports two statements:
1. anomalously long RG elapsed time is a major same-thread contributor to a subset of stutters;
2. RG does not explain all long frames.

This is not a sole-root-cause claim. RG elapsed time may still contain execution, preemption, synchronization, or waiting.

Next step: instrument inside RG for the RG-linked class, while preserving a separate outside-RG branch for long residual stalls.


## v0.5 compact T1-gap result

Accepted capture:
- RG events: 51,283
- frame intervals: 53,061
- `rg_lost=0`
- `frame_lost=0`
- QPC frequency: 10,000,000
- clean capture completion

Public deterministic artifacts:
- `tools/analysis_161/analyze_exact_v85_t1_gaps.py`
- `analysis/v85/SUMMARY_T1_GAPS.md`
- `analysis/v85/RESULTS_T1_GAPS.csv`

The compact probe records one row per RG call and breaks RG time into:
- T1 total/max;
- time before the first T1;
- total gaps between T1 calls;
- largest individual T1 gap;
- time after the final T1;
- total elapsed RG time outside T1.

The strongest RG-linked stall in this capture was:

- frame 44142: 61.196 ms
- RG call 41712: 49.720 ms
- RG overlap: 81.25%
- T1 total: 3.652 ms
- pre-T1: 0.002 ms
- inter-T1 gaps total: 0.037 ms
- post-T1: 46.028 ms

This localizes that stall class to the post-T1 renderer-finalization tail rather than setup before T1 or gaps between T1 calls.

A separate T1-heavy class also remains:

- frame 25571: 32.921 ms
- RG call 24692: 18.232 ms
- T1 total: 16.517 ms
- maximum single T1: 15.168 ms

There are also long frames with low RG contribution, so RG is not the sole stutter source.

The next runtime experiment should stay narrow: split only the post-T1 renderer-finalization tail into a few compact per-RG phases. Do not reintroduce per-subevent logging or a broad trace.


## v0.6 DX11 post-T1 tail experiment

The accepted v0.5 result localized a major RG-linked stall class to work after the final T1 call.

Strongest observed example:
- frame: 61.196 ms
- RG: 49.720 ms
- T1 total: 3.652 ms
- pre-T1: 0.002 ms
- inter-T1 gaps total: 0.037 ms
- post-T1: 46.028 ms

Static analysis identifies the active DX11 device vtable at `0x1422127A8`.

The next compact probe measures six validated post-T1 DX11 vtable phases:
- `+0x160 -> 0x1402B62B0`
- `+0x120 -> 0x1402E8FE0`
- `+0x0D0 -> 0x1402AE700`
- `+0x108 -> 0x1402B1A30`
- `+0x110 -> 0x1402B3A80`
- `+0x118 -> 0x1402F03B0`

The `+0x2D8` slot resolves to a CFG indirect-call guard and is not treated as a renderer phase.

The probe keeps one compact row per RG call. It records each phase count/time plus a nested-safe union of instrumented tail time. The deterministic analyzer computes residual post-T1 time not covered by the six phases.

Analyzer:
- `tools/analysis_161/analyze_exact_v87_dx11_tail.py`
- SHA-256 `D636312CEF7770E64EA00812E117077BFC0CE2637E99B6EDB03CA9D722D83384`

No valid v0.6 tail-phase performance result is claimed. The accepted run used DX12 while this probe patched a DX11 vtable, so its zero tail counters were a backend mismatch.

The active backend was remapped before any further drive.


## v0.7 active-DX12 tail result — 2026-09-30

The v0.6 tail experiment was invalid for tail-phase conclusions because the game was running DX12 while v0.6 patched a DX11 vtable. The zero v0.6 phase counters therefore indicated a backend mismatch, not that the phases were fast.

The active DX12 backend was then mapped statically and a compact v0.7 probe instrumented the corresponding post-T1 virtual calls.

Accepted v0.7 capture:
- RG events: 15,551
- RG events lost: 0
- instrumented DX12 tail active in 100% of RG rows

The strongest RG event in the capture:
- RG: 27.086 ms
- T1: 0.510 ms
- post-T1: 26.497 ms
- DX12 slot +0x108 target: 26.346 ms

Across the capture, the +0x108 phase was the only measured tail phase to produce >=8 ms events, including one >=16 ms event.

Frame correlation also shows the same phase accounting for most of post-T1 time in multiple slow frames. Example:
- frame interval: 24.924 ms
- overlapping RG: 9.061 ms
- T1: 4.102 ms
- post-T1: 4.900 ms
- +0x108 phase: 4.464 ms

The +0x108 target is a large DX12 command-stream interpreter. The next experiment will split only that function into a small set of internal subphases.

This remains a class-specific result, not a sole-root-cause claim:
- a separate T1-heavy class remains;
- some long frames still have low RG contribution.
