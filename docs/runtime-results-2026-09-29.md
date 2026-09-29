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
