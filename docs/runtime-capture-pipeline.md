# Runtime capture pipeline

Status: prepared and offline-validated. Runtime capture pending.

## Goal

The next experiment is designed to distinguish several mechanisms in one short drive instead of creating another sequence of single-hook versions.

Signals:

- frame-time windows from NemoFrameLogger v3;
- chain intervals from NemoChainProbe161 v0.2 threaded;
- PresentMon CPU/GPU/present metrics;
- Windows ETW scheduler, GPU, driver and disk activity.

## Timing basis

All project telemetry now exposes QPC-compatible timing.

NemoFrameLogger v3:
- `qpc_start`
- `qpc_end`
- `qpc_freq`

NemoChainProbe v0.2:
- QPC interval start/end
- QPC frequency

PresentMon:
- `--qpc_time`

This removes the earlier ambiguity caused by independently started approximately five-second windows.

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

Memory mode is used during the driving segment.

GeneralProfile.Light provides useful evidence including:

- CSwitch;
- ReadyThread;
- SampledProfile;
- DPC;
- Interrupt/ISR;
- DiskIO.

GPU.Light adds:

- DXGI;
- DxgKrnl;
- GPU activity.

FileIO.Light is deliberately omitted from the first broad run to reduce overhead. If DiskIO correlates with hitches, a later targeted FileIO trace can identify exact files.

## Run protocol

1. Start ETS normally.
2. Reach a representative on-road state.
3. Start the trace.
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

## Analysis questions

For each hitch window:

1. Did ChainProbe elapsed time rise?
2. If yes, was the thread executing or waiting/preempted?
3. Did GPU work/present latency rise at the same QPC interval?
4. Was there a ReadyThread/CSwitch stall?
5. Did DPC/ISR activity spike?
6. Did DiskIO spike?

This should separate:
- renderer CPU workload;
- worker synchronization;
- GPU/present blocking;
- driver/OS scheduling;
- storage/streaming.

## Interpretation rule

No long function-duration sample is treated as proof of CPU work by itself.

ChainProbe measures elapsed time. ETW scheduling state and PresentMon/GPU data decide what that elapsed time represents.
