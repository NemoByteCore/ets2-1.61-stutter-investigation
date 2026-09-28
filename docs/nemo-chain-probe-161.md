# NemoChainProbe161

`NemoChainProbe161` is an exact-build runtime profiler for the current ETS2 1.61 candidate chain.

It exists to answer one question in a single driving session:

> At what level of the mapped render path does the frame-time spike become expensive?

## Hooks

| Label | VA | Sampling |
|---|---:|---:|
| RG owner candidate | `140227140` | 1 / 1 |
| T1-like helper | `140226960` | 1 / 8 |
| nested winner | `141473E60` | 1 / 16 |
| RQ_ONE | `14160D010` | 1 / 16 |
| HEAD_DISPATCH | `14160D580` | 1 / 16 |
| downstream dispatch | `1402E5FF0` | 1 / 16 |
| BUNDLE_BUILD | `1402E5040` | 1 / 64 |
| DX12 descriptor builder | `14029F9B0` | 1 / 64 |

The increasingly aggressive sampling is intentional. The lower functions can be hot enough that timing every invocation would risk making the profiler part of the problem being measured.

## Output

The plugin writes:

```text
bin/win_x64/plugins/NemoChainProbe161.csv
```

Rows are cumulative and emitted approximately every five seconds.

For each target the CSV records:

- total calls,
- sampled calls,
- cumulative sampled microseconds,
- maximum sampled call duration.

The sampled total is **not** automatically multiplied by the sampling divisor. Analysis should use deltas and the sample count rather than treating it as exact whole-program CPU time.

## Runtime safety model

This is an inline-hook profiler, so it is inherently more invasive than the public SCS telemetry logger.

It is therefore fail-closed.

Before installing any hook, the plugin verifies the exact target executable using:

- PE timestamp: `0x6AB3C451`
- SizeOfImage: `0x0398A000`
- exact prologue bytes for all eight target functions

If any check fails, no hooks are installed.

On partial installation failure, already installed hooks are restored.

On normal telemetry shutdown, all original prologue bytes are restored before the DLL closes its log.

## What it does not do

The profiler does not intentionally change:

- rendering settings,
- traffic,
- physics,
- map state,
- resource selection,
- descriptor contents,
- pacing cvars.

The hook wrappers timestamp the original call and then return its original result path.

## Remaining risk

Exact signatures greatly reduce the risk of applying a hook to the wrong build, but they do not prove the recovered ABI is perfect.

A bad ABI interpretation can still crash the game.

For this reason the first runtime session is treated as a validation run. The plugin does not modify game files beyond creating its CSV, and uninstalling it is simply removing the DLL while the game is closed.

## Build artifact used for the first run

Local first build:

- size: `54,272` bytes
- SHA-256: `A8FFB4254F77BDF1ADEAC9BBCA9021B0253AD866235D373AC856809B7F9A3A17`

A `LoadLibrary` self-check confirmed that the DLL loads and exports:

- `scs_telemetry_init`
- `scs_telemetry_shutdown`

This does not execute the ETS-specific hook initialization; that requires the actual target executable.

## Correlation plan

The same run also keeps `NemoFrameLogger` active.

For every 5-second interval:

1. identify windows with elevated max frame time / threshold counts,
2. compute deltas from the cumulative chain counters,
3. compare sampled call duration and maxima at each level,
4. find the earliest level whose cost rises with the frame spike.

Possible outcomes:

- **RG already expensive, lower chain normal** — focus on the new 1.61 RG owner/refactor.
- **T1 becomes expensive** — descend into the reconstructed T1 subtree.
- **RQ/BUNDLE/descriptor becomes expensive** — continue from the old 1.60 renderer finding.
- **none correlate** — stop pursuing this chain and move to present/driver/scheduler or another engine subsystem.

The last outcome is useful: it prevents another long sequence of increasingly narrow hooks on the wrong hypothesis.
