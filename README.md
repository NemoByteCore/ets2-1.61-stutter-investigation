# ETS2 1.61 Stutter Investigation

Public investigation into recurring frame-time spikes and visible stutter in **Euro Truck Simulator 2 1.61**.

## Status

**Active investigation. Root cause is not yet claimed.**

Target:
- ETS2 `1.61.1.1`
- revision `6949e633e77902f7e023819d3131cc6ccce3707f`
- EXE SHA-256 `EB17944139BE4DE3D70D0CD57CDAA7C52C9E326ECF2D0DD3EA2F806545C74A53`
- renderer DX12

## Established

- visible stutter occurs in vanilla 1.61 and with ProMods;
- PresentMon captured real frame intervals up to ~72 ms;
- lower-chain sampled functions are generally much shorter than the full stutters;
- the recovered upper/lower relationship includes an indirect adapter/vtable bridge;
- v0.2's five-second aggregation is too coarse to prove exact RG/frame coincidence.

## Current instrumentation

Current runtime build is **NemoChainProbe161 v0.3 exact-RG**.

DLL:
- size `61,952`
- SHA-256 `DAD26A46EE67FBA81039C3994E8205C739548A14262BEBCC75977442B4B29A3E`

v0.3 records every RG call:
- QPC start
- QPC end
- duration
- thread ID

The hook does not perform file I/O; events are published to a ring and drained by the reporter thread.

The existing v0.2 aggregate telemetry is retained for context.

## Why this experiment comes before ETW

Previous runtime results only matched PresentMon frames to five-second ChainProbe buckets.

That can show that events occur in the same broad interval, but cannot establish that a particular RG call belongs to a particular long frame.

The next run therefore measures exact RG events first.

ETW is deferred until this direct timeline establishes whether the long stall is:
- substantially inside RG;
- outside/above RG;
- or still ambiguous enough to require scheduler/system evidence.

## Next experiment

PresentMon + FrameLogger + v0.3 exact-RG.

No WPR is required for this experiment.

See:
- `docs/nemo-chain-probe-161.md`
- `docs/runtime-capture-pipeline.md`
- `docs/runtime-results-2026-09-29.md`

## Scope

This repository does not redistribute the ETS2 executable, DLC/map assets, ProMods files or full proprietary decompiler dumps.
