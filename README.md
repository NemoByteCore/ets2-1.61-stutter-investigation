# ETS2 1.61 Stutter Investigation

Public investigation into recurring frame-time spikes and visible stutter in **Euro Truck Simulator 2 1.61**.

## Status

**Active investigation. Root cause is not yet claimed.**

Current exact-correlation instrumentation:
- NemoChainProbe161 v0.3 exact-RG
- NemoFrameLogger v4 exact-frame

The next experiment requires neither WPR nor PresentMon.

## Why

Earlier runtime captures proved real long-frame events, but ChainProbe v0.2 summarized RG timing in approximately five-second windows.

That resolution cannot prove that a specific RG maximum occurred during a specific slow frame.

v0.3 and FrameLogger v4 solve the timing problem directly:
both emit exact QPC intervals.

## NemoChainProbe161 v0.3

- size `61,952`
- SHA-256 `DAD26A46EE67FBA81039C3994E8205C739548A14262BEBCC75977442B4B29A3E`

Every RG call:
```text
event_seq,rg_call_seq,qpc_start,qpc_end,duration_ticks,duration_us,thread_id
```

## NemoFrameLogger v4

- size `55,296`
- SHA-256 `B1D6D9E93FC466D5F31E650E2567B4EA4D5541B0675D4CED37AF1A7D6782F413`

Every valid frame interval:
```text
event_seq,frame_seq,segment_id,qpc_start,qpc_end,duration_ticks,duration_us,thread_id
```

## No-UAC path

A non-elevated PresentMon session was tested and failed with access denied on the current Windows account.

Rather than changing Windows privileges/groups, the next experiment is plugin-only.

No WPR.
No PresentMon.
No elevation.

## Next experiment

Capture exact frames and exact RG calls during the same short drive, then intersect the QPC intervals directly.

Only if the exact result remains ambiguous will targeted ETW become the next step.

See:
- `docs/nemo-chain-probe-161.md`
- `docs/nemo-frame-logger-v4.md`
- `docs/runtime-capture-pipeline.md`
- `docs/runtime-results-2026-09-29.md`

## Scope

This repository does not redistribute the ETS2 executable, DLC/map assets, ProMods files or full proprietary decompiler dumps.
