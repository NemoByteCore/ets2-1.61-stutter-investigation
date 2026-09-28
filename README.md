# ETS2 1.61 Stutter Investigation

Public investigation into recurring frame-time spikes and visible stutter in **Euro Truck Simulator 2 1.61**.

The goal is not to collect random tweak lists. The goal is to reduce the problem to a reproducible runtime path using frame-time telemetry, static binary comparison, call-graph reconstruction and targeted instrumentation.

## Status

**Active investigation. Root cause is not yet claimed.**

Current target:

- ETS2: `1.61.1.1`
- revision: `6949e633e77902f7e023819d3131cc6ccce3707f`
- EXE SHA-256: `EB17944139BE4DE3D70D0CD57CDAA7C52C9E326ECF2D0DD3EA2F806545C74A53`
- renderer used for the current investigation: DX12
- telemetry: public SCS telemetry logger + exact-build runtime probe

The investigation was restarted on 1.61 after an earlier 1.60 study localized a significant render-queue / descriptor-related path. The 1.60 addresses are used only as structural anchors; they are never reused blindly in 1.61.

## What is already established

1. The visible stutter is not explained only by ProMods. Vanilla 1.61 also produces recurring frame-time spikes.
2. DX12 plus `t_averaging_window_duration=200` and `t_averaging_window_length=500` reduced some large spikes, but did not eliminate the perceived hitching.
3. The in-game `t_limit_fps=55` test did not actually hold the game at a stable 55 FPS and did not solve the issue.
4. Static 1.60 -> 1.61 mapping shows that the lower half of the previously identified render path survived with strong structural similarity.
5. The upper `RG_CORE / T1` region changed substantially in 1.61 and appears to have been refactored or merged into larger functions.
6. A new exact-build chain probe has been built to measure the whole candidate path in one runtime session instead of iterating through dozens of single-hook experiments.

## Current 1.61 candidate chain

```text
main loop
  1401CBEE0
      |
render/present coordinator
  1401DBCE0
      |
RG owner candidate
  140227140
      |
T1-like helper
  140226960
      |
substantive nested winner
  141473E60
      |
RQ_ONE
  14160D010
      |
HEAD_DISPATCH
  14160D580
      |
downstream dispatch
  1402E5FF0
      |
BUNDLE_BUILD
  1402E5040
      |
DX12 descriptor builder
  14029F9B0
```

The lower section is strongly mapped from 1.60 by normalized pseudocode, function size and call-graph structure. The `RG owner / T1-like` pair is deliberately labeled more cautiously: it is structurally compelling, but runtime correlation is still required.

## Repository layout

- `docs/target-build.md` — exact build and reproducibility anchors
- `docs/runtime-baselines.md` — vanilla / ProMods / limiter measurements
- `docs/static-diff-1.60-to-1.61.md` — binary mapping and current function map
- `docs/nemo-chain-probe-161.md` — design and safety model of the runtime probe
- `src/NemoChainProbe161.cpp` — source for the current exact-build probe

## What happens next

One short driving session is recorded with both:

- `NemoFrameLogger` — 5-second frame-time windows
- `NemoChainProbe161` — sampled timing for the candidate render chain

The two logs are then correlated by time. That should distinguish between:

- cost already present at the RG owner,
- cost introduced by the T1 branch,
- cost appearing in the render-queue / bundle / descriptor path,
- or a stall outside this chain entirely.

If the last case occurs, the investigation moves away from this path instead of continuing to add hooks to the same hypothesis.

## Scope / repository policy

This repository contains original instrumentation source, measurements, hashes, derived function maps and analysis notes.

It does **not** contain:

- the ETS2 executable,
- DLC or map assets,
- ProMods files,
- full decompiler dumps,
- redistributed proprietary game code.

All addresses and signatures are pinned to the exact target build above.
