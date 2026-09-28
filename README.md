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

## What is established

1. Visible stutter occurs in vanilla 1.61 as well as with ProMods.
2. DX12 plus `t_averaging_window_duration=200` and `t_averaging_window_length=500` reduced some large spikes but did not eliminate the hitching.
3. The tested in-game `t_limit_fps=55` configuration did not actually hold a stable 55 FPS and did not solve the symptom.
4. Static 1.60 -> 1.61 mapping strongly preserves a lower render-queue / descriptor-related region.
5. The upper synchronization/render-owner region is structurally recovered.
6. The upper and lower regions are now connected through an indirect adapter/vtable dispatch.

## Current 1.61 chain

Direct upper region:

```text
1401CBEE0
 -> 1401DBCE0
 -> 140227140
 -> 140226960
```

Recovered indirect middle:

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

Lower region:

```text
141473E60
 -> 14160D010
 -> 14160D580
 -> 1402E5FF0
 -> lower render/descriptor work
```

The earlier direct-call BFS failure remains correct: the missing section is not represented by ordinary direct-call edges.

## Instrumentation status

The initial v0.1 probe exposed two problems:

- cumulative maxima were poor for interval attribution;
- report I/O from a hot path could itself become an observer effect.

Those issues were addressed in the current runtime build.

### NemoChainProbe161 v0.2 threaded

Current local/deployed build:

- size: `58,880` bytes
- SHA-256: `474C9C6925E7B5C486E267CBA03332F5801A3845247E3D188C5707C2020054E2`

Changes from v0.1:

- QPC start/end per reporting interval;
- per-window call/sample deltas;
- per-window max;
- duration buckets >=1/2/4/8/16/33 ms;
- cache-line isolated stat blocks;
- report I/O moved to a dedicated low-frequency thread;
- no reporting path remains inside the RG hook hot path;
- exact-build fail-closed validation retained.

### NemoFrameLogger v3

Current local/deployed build:

- size: `50,688` bytes
- SHA-256: `FF4A11470ED9E8FDCB221EDF25EC17E5F73D400CDD725996AB27C70DE8D5DEB6`

Every approximately five-second frame window now emits:

- `qpc_start`;
- `qpc_end`;
- `qpc_freq`;
- frame count;
- average/max frame time;
- >20/25/33/50/100 ms counts.

This makes direct overlap with ChainProbe and PresentMon possible.

## Broad runtime capture

Prepared tools:

- PresentMon 2.6.0 x64
- WPR `GeneralProfile.Light`
- WPR `GPU.Light`

The first broad capture intentionally avoids always-on FileIO tracing to reduce overhead. GeneralProfile still provides DiskIO, scheduler, ReadyThread, CSwitch, DPC and ISR evidence.

The next run should distinguish:

- real CPU work inside the mapped chain;
- thread waiting / scheduling delay;
- GPU or present blocking;
- DPC/ISR/driver activity;
- storage activity.

See:
`docs/runtime-capture-pipeline.md`

## Current next step

No more static remapping is required before the next experiment.

The next evidence should come from one short controlled driving session:

1. start ETS normally;
2. reach a representative on-road state;
3. start the prepared broad trace;
4. capture several characteristic hitches;
5. exit ETS normally;
6. finalize the trace;
7. correlate QPC across FrameLogger, ChainProbe, PresentMon and ETW.

Do not change graphics/config during that run.

## Repository layout

- `docs/target-build.md` — exact build and reproducibility anchors
- `docs/runtime-baselines.md` — vanilla / ProMods / limiter measurements
- `docs/static-diff-1.60-to-1.61.md` — binary mapping and indirect bridge
- `docs/nemo-chain-probe-161.md` — probe design and evolution
- `docs/runtime-capture-pipeline.md` — next combined runtime experiment
- `src/NemoChainProbe161.cpp` — historical experimental v0.1 source

## Scope / repository policy

This repository contains original instrumentation source, measurements, hashes, derived function maps and analysis notes.

It does **not** contain:

- the ETS2 executable;
- DLC or map assets;
- ProMods files;
- full decompiler dumps;
- redistributed proprietary game code.

All addresses and signatures are pinned to the exact target build above.
