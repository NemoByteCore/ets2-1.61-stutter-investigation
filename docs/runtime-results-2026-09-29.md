# Runtime results — 2026-09-29

## Existing v0.2 evidence

Two controlled runs were completed before v0.3.

### Run A — plugin-only

Largest FrameLogger spike:
33.470 ms.

Same five-second ChainProbe window:
- RG max 18.718 ms
- T1 max 0.541 ms
- winner max 0.444 ms
- RQ max 0.418 ms
- HEAD max 0.468 ms
- downstream max 0.516 ms

### Run B — PresentMon + plugins

PresentMon rows:
14,670.

Representative frame intervals:
- 71.7929 ms
- 63.3167 ms
- 53.3464 ms
- 47.2012 ms
- 47.0668 ms

The old v0.2 correlation placed these frames inside five-second ChainProbe windows whose RG maxima were roughly 6–12 ms in several cases.

## Important correction

That does **not** establish that the RG maximum occurred during the specific slow frame.

v0.2's five-second aggregation is too coarse.

Therefore:
- exact RG/frame coincidence is currently unproven;
- "RG participates in this specific 71 ms frame" is not yet a fact;
- lower-chain interval maxima remain useful context but not exact event attribution.

## Current instrumentation

NemoChainProbe161 v0.3 exact-RG is now deployed.

It records every RG call with:
- QPC start/end;
- duration;
- thread ID.

## Next result to obtain

For each slow PresentMon frame:
1. derive the exact QPC frame interval;
2. find RG calls that truly overlap that interval;
3. compare RG duration with frame duration.

This single measurement determines the next branch:

- **RG explains most of frame:** instrument/sample inside RG.
- **RG is short:** move profiling above/outside RG.
- **exact timing still suggests scheduling/wait ambiguity:** use targeted ETW.

No root cause is claimed before this exact-event correlation.
