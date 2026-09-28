# NemoChainProbe161

`NemoChainProbe161 v0.1` is an exact-build experimental inline-hook profiler built for ETS2 1.61.1.1.

## Current status

**HOLD / experimental. Do not treat v0.1 as the recommended decisive next run.**

The DLL was built successfully and validated as a loadable plugin artifact.

The static upper-to-lower relationship has since been recovered through an indirect adapter/vtable path. The remaining HOLD status is about measurement quality: v0.1 telemetry is weaker than needed for clean frame-window correlation and may introduce observer effect.

The source remains public because it is useful as an exact-build instrumentation artifact and documents the current hypothesis. Its limitations are part of the investigation.

## Hook set

| Label | VA | Sampling |
|---|---:|---:|
| RG-owner candidate | `140227140` | 1 / 1 |
| T1-like candidate | `140226960` | 1 / 8 |
| nested winner | `141473E60` | 1 / 16 |
| RQ_ONE | `14160D010` | 1 / 16 |
| HEAD_DISPATCH | `14160D580` | 1 / 16 |
| downstream dispatch | `1402E5FF0` | 1 / 16 |
| BUNDLE_BUILD | `1402E5040` | 1 / 64 |
| DX12 descriptor builder | `14029F9B0` | 1 / 64 |

Important: the hook list spans **two evidence regions**. It must not be interpreted as proof that every entry belongs to one direct runtime chain.

## Static chain status

The direct upper and lower regions are now connected through an indirect adapter path:

```text
140226960
 -> [owner+0x1C68]
 -> adapter 1421FD1B0 +8
 -> 14022EAA0
 -> contained callback 1423F5530 +8
 -> 141476140
 -> 141473E60
```

The earlier direct-call BFS failure remains correct; the bridge is not represented by ordinary direct-call edges.

Therefore the hook set now spans one statically recovered relationship, although runtime timing/correlation still needs validation.

## v0.1 output

The plugin writes:

```text
bin/win_x64/plugins/NemoChainProbe161.csv
```

Rows are cumulative and emitted approximately every five seconds.

For each target v0.1 records:

- total calls;
- sampled calls;
- cumulative sampled microseconds;
- cumulative maximum sampled call duration.

## Why v0.1 telemetry is insufficient for a decisive correlation

Cumulative totals can be differenced between rows.

Cumulative maximum cannot identify the interval in which the long call occurred. Once a large max has happened, later rows retain it.

The probe and `NemoFrameLogger` also create their ~5-second rows independently, without an explicit shared QPC interval boundary.

Every-N sampling can additionally miss a rare single long call.

Therefore v0.1 data could be suggestive, but should not be used for a strong statement such as:

> the 33 ms frame spike in window N was caused by target X

without additional alignment evidence.

## Required telemetry direction before decisive use

Preferred next format:

- explicit QPC window start;
- explicit QPC window end;
- per-interval call delta;
- per-interval sampled count;
- per-interval sampled time;
- per-interval max;
- duration buckets/histogram where practical;
- thread ID for exceptional long calls where useful.

The project should also reduce shared-counter contention where practical because global atomics can contribute observer effect/false sharing.

## Runtime safety model

This is an inline-hook profiler and is more invasive than the public SCS telemetry logger.

It is fail-closed against the exact target build.

Before installing any hook v0.1 verifies:

- PE timestamp: `0x6AB3C451`
- SizeOfImage: `0x0398A000`
- exact prologue bytes for all eight targets

If any check fails, no hooks are installed.

On partial installation failure, already installed hooks are restored.

On normal telemetry shutdown, original prologue bytes are restored.

## Trampoline constraints

The simple trampoline is only appropriate when the copied prologue is relocation-safe.

For the selected v0.1 targets the hook lengths were chosen on instruction boundaries and the copied sequences were inspected for problematic early relative/RIP-sensitive instructions.

LOOP/COORD were intentionally not hooked with this mechanism because their early instruction sequences were less suitable.

This does not eliminate all risk:
- recovered ABI can still be wrong;
- stack/XMM arguments can be misunderstood;
- scheduler preemption can make wall-time duration look like function work;
- concurrent patching is not inherently atomic.

## What the probe does not intentionally change

It does not intentionally modify:

- rendering settings;
- traffic;
- physics;
- map state;
- resource selection;
- descriptor contents;
- pacing cvars.

The wrappers time original calls and return through the original execution path.

## Build artifact

First local build:

- size: `54,272` bytes
- SHA-256: `A8FFB4254F77BDF1ADEAC9BBCA9021B0253AD866235D373AC856809B7F9A3A17`

A `LoadLibrary` self-check confirmed the DLL loads and exports:

- `scs_telemetry_init`
- `scs_telemetry_shutdown`

That test validates the artifact/dependencies, not the ETS-specific hook initialization.

## Recommended next stage

Before relying on a revised hook probe:

1. redesign telemetry around explicit QPC-aligned intervals and per-window maxima;
2. reduce shared-counter / sampling observer effect where practical;
3. collect a broad ETW/WPA + PresentMon/GPU trace;
4. use that trace to decide whether the dominant spike is:
   - CPU render work;
   - synchronization/wait;
   - GPU/present;
   - file I/O/asset streaming;
   - driver/OS scheduling.

If broad tracing points back into these regions, a revised QPC-aligned probe becomes the next focused instrument.
