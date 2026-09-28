# ETS2 1.61 Stutter Investigation

Public investigation into recurring frame-time spikes and visible stutter in **Euro Truck Simulator 2 1.61**.

The goal is not to collect random tweak lists. The goal is to reduce the problem to reproducible engine behavior using frame-time telemetry, static binary comparison, call-graph reconstruction and targeted instrumentation.

## Status

**Active investigation. Root cause is not yet claimed.**

Current target:

- ETS2: `1.61.1.1`
- revision: `6949e633e77902f7e023819d3131cc6ccce3707f`
- EXE SHA-256: `EB17944139BE4DE3D70D0CD57CDAA7C52C9E326ECF2D0DD3EA2F806545C74A53`
- renderer: DX12
- baseline telemetry: `NemoFrameLogger`

The 1.60 investigation is used only as historical structural evidence. No 1.60 address is assumed valid in 1.61.

## What is already established

1. Visible stutter occurs in vanilla 1.61 as well as with ProMods.
2. DX12 plus `t_averaging_window_duration=200` and `t_averaging_window_length=500` reduced some large spikes but did not eliminate the hitching.
3. The tested in-game `t_limit_fps=55` configuration did not actually hold a stable 55 FPS and did not solve the symptom.
4. Static 1.60 -> 1.61 mapping strongly preserves a lower render-queue / descriptor-related region.
5. A separate upper synchronization/render-owner region is also structurally credible.
6. The upper and lower regions are now statically connected through an indirect adapter/vtable dispatch.

That sixth point is an important correction to the initial public write-up.

## Current 1.61 evidence map

### Upper region — verified direct edges

```text
main loop
1401CBEE0
    |
    v
render/present coordinator
1401DBCE0
    |
    v
RG-owner candidate
140227140
    |
    v
T1-like candidate
140226960
```

The local topology is real:

```text
1401DBCE0 -> 140227140
140227140 -> 140226960
```

The semantic labels `RG-owner candidate` and `T1-like candidate` remain hypotheses.

### Lower region — strong remap from 1.60

```text
substantive nested winner
141473E60
    |
    v
RQ_ONE
14160D010
    |
    v
HEAD_DISPATCH
14160D580
    |
    v
downstream dispatch
1402E5FF0
    |
    v
BUNDLE_BUILD
1402E5040

DX12 descriptor builder
14029F9B0
```

The strongest direct lower edges include:

```text
141473E60 -> 14160D010 -> 14160D580 -> 1402E5FF0
```

## Recovered indirect middle

A normal direct-call search still finds no path from `140226960` to `141473E60`.

The missing relationship is indirect:

```text
140226960
  -> callback at owner +0x1C68
  -> adapter vtable 1421FD1B0 +0x8
  -> 14022EAA0 forwarding thunk
  -> contained callback at adapter +0x110
  -> callback vtable 1423F5530 +0x8
  -> 141476140
  -> JMP 141473E60
```

Construction analysis shows `141473A00` creates the source callback, `1414752E0` clones it through source-vtable `+0x10`, stores the clone at adapter `+0x110`, and stores the adapter at render-queue data `+0x1C68`.

This explains why the harvested direct-call graph could not connect the regions.

## Instrumentation status

`NemoFrameLogger` remains the low-risk baseline logger through the public SCS telemetry API.

`NemoChainProbe161 v0.1` was built as an exact-build inline-hook profiler, but it is currently **experimental / HOLD** rather than the recommended decisive next run.

Why:

- the static chain is now recovered, but the current probe format is still not clean enough for decisive correlation;
- its current output uses cumulative max values;
- probe and frame windows are not explicitly QPC-aligned;
- every-N sampling may miss a rare long call;
- shared atomics can contribute observer effect.

See:
`docs/nemo-chain-probe-161.md`

## Current next step

The next high-information stage is:

1. revise probe telemetry to interval/QPC-aligned semantics;
2. reduce probe observer effect where practical;
3. collect one broad ETW/WPA + PresentMon/GPU trace to distinguish:
   - CPU render work;
   - worker-thread synchronization/waits;
   - GPU/present blocking;
   - file I/O / asset streaming;
   - driver/OS scheduling.

Only if broad evidence points back into the mapped render region should narrower hook instrumentation continue.

## Repository layout

- `docs/target-build.md` — exact build and reproducibility anchors
- `docs/runtime-baselines.md` — vanilla / ProMods / limiter measurements
- `docs/static-diff-1.60-to-1.61.md` — binary mapping and corrected evidence map
- `docs/nemo-chain-probe-161.md` — v0.1 probe design, limitations and current HOLD status
- `src/NemoChainProbe161.cpp` — experimental v0.1 probe source

## Scope / repository policy

This repository contains original instrumentation source, measurements, hashes, derived function maps and analysis notes.

It does **not** contain:

- the ETS2 executable;
- DLC or map assets;
- ProMods files;
- full decompiler dumps;
- redistributed proprietary game code.

All addresses and signatures are pinned to the exact target build above.
