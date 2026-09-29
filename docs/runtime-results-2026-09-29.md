# Runtime results — 2026-09-29

## Scope

This document summarizes the two controlled ETS2 1.61 runtime runs performed on 2026-09-29.

No root cause is claimed yet.

## Run A — plugin-only

FrameLogger and ChainProbe completed cleanly.

Largest noted FrameLogger spike:
- 33.470 ms

Overlapping ChainProbe window:
- RG max: 18.718 ms
- T1 max: 0.541 ms
- winner max: 0.444 ms
- RQ max: 0.418 ms
- head max: 0.468 ms
- downstream max: 0.516 ms

This establishes correlation for at least one hitch, but ChainProbe durations are wall time and can include waits/preemption.

## Run B — PresentMon + plugins

PresentMon rows:
- 14,670

Largest frames include:

| FrameTime | CPUBusy | CPUWait | GPUBusy | GPUWait |
|---:|---:|---:|---:|---:|
| 71.7929 ms | 71.1136 ms | 0.6793 ms | 1.7433 ms | 70.1669 ms |
| 63.3167 ms | 62.6699 ms | 0.6468 ms | 2.1356 ms | 61.0582 ms |
| 53.3464 ms | 52.6511 ms | 0.6953 ms | 1.7690 ms | 51.4071 ms |
| 47.2012 ms | 46.5759 ms | 0.6253 ms | 8.1962 ms | 0.0000 ms |
| 47.0668 ms | 46.4388 ms | 0.6280 ms | 14.7729 ms | 0.0000 ms |

These measurements do not support simple GPU saturation as the general explanation.

## ChainProbe correlation

Representative overlaps:

- 71/63 ms frame region:
  - ChainProbe window 43
  - RG max ~10.356 ms
  - downstream targets remain sub-millisecond to low-millisecond

- 53 ms frame region:
  - ChainProbe window 58
  - RG max ~7.556 ms

- 26 ms frame region:
  - ChainProbe window 47
  - RG max ~11.948 ms

The largest frame spikes are therefore not explained by RG-owner duration alone.

## Current interpretation

Supported:
- real long frame events exist;
- simple GPU saturation is not a sufficient explanation;
- RG-owner is involved in the affected path;
- lower-chain sampled functions are generally much shorter than the full frame stalls.

Still unresolved:
- CPU work above RG;
- worker-thread synchronization / wakeup delay;
- submit/present dependency;
- driver scheduling / DPC;
- disk or streaming activity.

## ETL status

The WPR ETL from Run B was lost because finalization attempted PresentMon cleanup before `wpr -stop`.

That launcher bug is fixed.

## Next experiment

One final controlled runtime run should collect ETW with:
- ReadyThread / CSwitch;
- sampled CPU stacks;
- DPC / ISR;
- DiskIO;
- DXGI / DxgKrnl / GPU scheduling.

After that trace, follow the ETW evidence instead of adding more generic hooks or configuration experiments.
