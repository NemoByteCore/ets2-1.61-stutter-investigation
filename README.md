# ETS2 1.61 Stutter Investigation

Public investigation into recurring frame-time spikes and visible stutter in **Euro Truck Simulator 2 1.61**.

## Status

**Active investigation. Root cause is not yet claimed.**

Current exact-correlation instrumentation:
- NemoChainProbe161 v0.7 active-DX12 tail probe
- NemoFrameLogger v4 exact-frame

Current localization:
- the post-T1 RG-linked stall class is dominated by DX12 slot +0x108 / its command-stream interpreter;
- T1-heavy and low-RG long-frame classes remain separate.

The next experiment stays narrow: split only the +0x108 target into compact internal subphases.

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

## Current result

The accepted v0.7 capture recorded 15,551 RG events with zero loss and active DX12 tail counters in every RG row.

Worst RG in that run:
- 27.086 ms total RG
- 26.497 ms post-T1
- 26.346 ms in the DX12 +0x108 phase

That phase also accounts for most post-T1 time in multiple slow-frame correlations.

## Next experiment

Split only the +0x108 DX12 command-stream target into a few internal subphases. Do not broaden back to ETW unless the narrowed result becomes ambiguous.

See:
- `docs/nemo-chain-probe-161.md`
- `docs/nemo-frame-logger-v4.md`
- `docs/runtime-capture-pipeline.md`
- `docs/runtime-results-2026-09-29.md`

## Scope

This repository does not redistribute the ETS2 executable, DLC/map assets, ProMods files or full proprietary decompiler dumps.
