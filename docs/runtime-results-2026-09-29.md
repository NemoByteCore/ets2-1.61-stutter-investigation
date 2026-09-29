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
