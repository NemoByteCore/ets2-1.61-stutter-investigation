# ETS2 1.61 Stutter Investigation

Public investigation into recurring frame-time spikes and visible stutter in **Euro Truck Simulator 2 1.61**.

The goal is to reduce the problem to reproducible engine behavior using frame-time telemetry, static binary comparison, call-graph reconstruction and targeted instrumentation.

## Status

**Active investigation. Root cause is not yet claimed.**

Current target:
- ETS2 `1.61.1.1`
- revision `6949e633e77902f7e023819d3131cc6ccce3707f`
- EXE SHA-256 `EB17944139BE4DE3D70D0CD57CDAA7C52C9E326ECF2D0DD3EA2F806545C74A53`
- renderer DX12

## What is established

1. Visible stutter occurs in vanilla 1.61 as well as with ProMods.
2. DX12 plus averaging 200/500 reduces some spikes but does not eliminate hitching.
3. The tested in-game 55 FPS limiter did not hold a stable 55 FPS and did not solve the symptom.
4. Static 1.60 -> 1.61 mapping strongly preserves a lower render-queue / descriptor-related region.
5. The upper synchronization/render-owner region is structurally recovered.
6. The upper and lower regions are connected through an indirect adapter/vtable dispatch.
7. Runtime PresentMon capture now confirms real single-frame spikes up to ~72 ms.
8. The largest spikes do not resemble simple GPU saturation.
9. RG-owner timing correlates with some hitches but is not sufficient to explain the largest stalls by itself.

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

## Instrumentation

### NemoChainProbe161 v0.2 threaded

Current runtime build:
- size `58,880`
- SHA-256 `C71C659DDD1A6A1C852C692C945C5E5CD1BEE9259E80C8DF86D7104290B41CB4`

The RQ wrapper ABI-width bug found during pre-runtime review was fixed before the captured runs.

### NemoFrameLogger v3

Current runtime build:
- size `50,688`
- SHA-256 `FF4A11470ED9E8FDCB221EDF25EC17E5F73D400CDD725996AB27C70DE8D5DEB6`

## Runtime evidence — 2026-09-29

A PresentMon + ChainProbe + FrameLogger run captured:
- 14,670 PresentMon rows;
- frame spikes up to 71.7929 ms;
- corresponding ChainProbe QPC windows.

Examples:
- 71.7929 ms frame: CPUBusy 71.1136 / CPUWait 0.6793 / GPUBusy 1.7433 / GPUWait 70.1669
- 63.3167 ms frame: CPUBusy 62.6699 / CPUWait 0.6468 / GPUBusy 2.1356 / GPUWait 61.0582
- 53.3464 ms frame: CPUBusy 52.6511 / CPUWait 0.6953 / GPUBusy 1.7690 / GPUWait 51.4071

The largest frames do not align with equally large RG-owner samples:
- 71/63 ms frame region: RG max ~10.356 ms
- 53 ms frame region: RG max ~7.556 ms

Current interpretation:
the RG-owner path is involved, but a higher or parallel scheduling/work-queue/submit dependency is likely.

See:
`docs/runtime-results-2026-09-29.md`

## Broad ETW capture

WPR profiles:
- `GeneralProfile.Light`
- `GPU.Light`

The first broad run lost its ETL because a PresentMon cleanup warning interrupted finalization before `wpr -stop`.

The launcher has been corrected so ETL finalization happens first.

## Current next step

One final controlled runtime run to obtain ETW scheduler/GPU/system evidence.

No additional static remapping or generic graphics/config changes are justified before that trace.

## Repository layout

- `docs/target-build.md`
- `docs/runtime-baselines.md`
- `docs/static-diff-1.60-to-1.61.md`
- `docs/nemo-chain-probe-161.md`
- `docs/runtime-capture-pipeline.md`
- `docs/runtime-results-2026-09-29.md`
- `src/NemoChainProbe161.cpp` — historical experimental v0.1 source

## Scope

This repository does not redistribute the ETS2 executable, DLC/map assets, ProMods files or full proprietary decompiler dumps.
