# ETS2 1.61 Stutter Investigation

Public investigation into recurring frame-time spikes and visible stutter in **Euro Truck Simulator 2 1.61**.

The goal is to reduce the problem to reproducible engine behavior using frame-time telemetry, static binary comparison, call-graph reconstruction and targeted instrumentation.

## Status

**Active investigation. Root cause is not yet claimed.**

Current target:

- ETS2: `1.61.1.1`
- revision: `6949e633e77902f7e023819d3131cc6ccce3707f`
- EXE SHA-256: `EB17944139BE4DE3D70D0CD57CDAA7C52C9E326ECF2D0DD3EA2F806545C74A53`
- renderer: DX12

## What is established

1. Visible stutter occurs in vanilla 1.61 as well as with ProMods.
2. DX12 plus `t_averaging_window_duration=200` and `t_averaging_window_length=500` reduced some large spikes but did not eliminate the hitching.
3. The tested in-game `t_limit_fps=55` configuration did not actually hold a stable 55 FPS and did not solve the symptom.
4. Static 1.60 -> 1.61 mapping strongly preserves a lower render-queue / descriptor-related region.
5. The upper synchronization/render-owner region is structurally recovered.
6. The upper and lower regions are connected through an indirect adapter/vtable dispatch.

## Current 1.61 chain

```text
1401CBEE0
 -> 1401DBCE0
 -> 140227140
 -> 140226960
 -> callback at owner +0x1C68
 -> adapter vtable 1421FD1B0 +0x8
 -> 14022EAA0
 -> contained callback +0x110
 -> callback vtable 1423F5530 +0x8
 -> 141476140
 -> JMP 141473E60
 -> 14160D010
 -> 14160D580
 -> 1402E5FF0
 -> lower render/descriptor work
```

The earlier direct-call BFS failure remains valid because the middle is an indirect dispatch.

## Instrumentation status

### NemoChainProbe161 v0.2 threaded

Current runtime build:

- size: `58,880` bytes
- SHA-256: `474C9C6925E7B5C486E267CBA03332F5801A3845247E3D188C5707C2020054E2`

It adds:

- QPC interval start/end;
- per-window call/sample deltas;
- per-window max;
- duration buckets >=1/2/4/8/16/33 ms;
- cache-line isolated stat blocks;
- dedicated low-frequency reporting thread;
- no CSV/report I/O in the RG hot path.

### NemoFrameLogger v3

Current runtime build:

- size: `50,688` bytes
- SHA-256: `FF4A11470ED9E8FDCB221EDF25EC17E5F73D400CDD725996AB27C70DE8D5DEB6`

Frame windows now include:
- `qpc_start`;
- `qpc_end`;
- `qpc_freq`.

## Broad runtime capture

Prepared:

- PresentMon 2.6.0 x64
- WPR `GeneralProfile.Light`
- WPR `GPU.Light`

The runtime capture has **not** been performed yet.

On the current Windows setup, WPR requires elevated privileges to enable the selected system-performance profiles. A non-elevated start test failed with `0xc5585011` and left WPR stopped.

The real capture will therefore be started normally from an elevated session when the machine is attended.

See:
`docs/runtime-capture-pipeline.md`

## Current next step

One short controlled driving session with the existing instrumentation and broad trace.

No further static remapping or graphics/config changes are required before that run.

## Repository layout

- `docs/target-build.md`
- `docs/runtime-baselines.md`
- `docs/static-diff-1.60-to-1.61.md`
- `docs/nemo-chain-probe-161.md`
- `docs/runtime-capture-pipeline.md`
- `src/NemoChainProbe161.cpp` — historical experimental v0.1 source

## Scope / repository policy

This repository does not redistribute the ETS2 executable, DLC/map assets, ProMods files or full proprietary decompiler dumps.
