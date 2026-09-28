# Runtime capture pipeline

Status: prepared and offline-validated. Runtime capture pending.

## Goal

The next experiment combines:

- NemoFrameLogger v3 frame windows;
- NemoChainProbe161 v0.2 threaded intervals;
- PresentMon CPU/GPU/present metrics;
- Windows ETW scheduler/GPU/driver/disk activity.

All project telemetry now exposes QPC-compatible timing.

## PresentMon

Version:
`2.6.0 x64`

SHA-256:
`B2A706BC6AD475749E3B7E3409263AA1E6906D45BDCF993F6DBC0F660188F1AF`

Target:
`eurotrucks2.exe`

Output:
v2 metrics + QPC time.

## WPR / ETW

Profiles:

```text
GeneralProfile.Light
GPU.Light
```

These provide scheduler/ReadyThread/CSwitch/SampledProfile/DPC/ISR/DiskIO plus DXGI/DxgKrnl/GPU evidence.

FileIO.Light is deliberately omitted from the first broad run to reduce overhead.

## Elevation requirement

On the current Windows setup, these WPR system-performance profiles require elevation.

A non-elevated test start returned:

```text
0xc5585011
Failed to enable the policy to profile system performance.
```

The test was performed while ETS was closed.

After the failed test:
- WPR was not recording;
- PresentMon was not running;
- no managed trace was active.

The real capture should therefore be started from a normally elevated session with the machine attended. The project does not attempt to bypass UAC or weaken Windows policy.

## Run protocol

1. Start ETS normally.
2. Reach a representative on-road state.
3. Start the trace from an elevated session.
4. Drive until several characteristic hitches are observed.
5. Exit ETS normally.
6. Finalize the trace.

Do not alter graphics/config during the capture.

## Expected capture bundle

- PresentMon CSV;
- WPR ETL;
- NemoChainProbe v0.2 CSV;
- `game.log.txt` containing NemoFrame v3 records;
- metadata with tool/build hashes.

## Interpretation rule

ChainProbe measures sampled elapsed wall time, not guaranteed CPU execution time.

ETW scheduling state and PresentMon/GPU data are required before calling a long chain sample a CPU hotspot.
