# Runtime capture pipeline

Status: one-click launcher prepared, elevation path validated, pre-runtime review cross-checked. Runtime capture ready.

## Goal

The next experiment combines:
- NemoFrameLogger v3 frame windows;
- NemoChainProbe161 v0.2 threaded intervals;
- PresentMon CPU/GPU/present metrics;
- Windows ETW scheduler/GPU/driver/disk activity.

All project telemetry exposes QPC-compatible timing.

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

## One-click launcher

The current launcher:
- self-elevates through normal Windows UAC;
- verifies exact runtime-tool hashes;
- refuses to interfere with an existing WPR session;
- launches ETS2 through Steam;
- waits for the game process;
- waits for fresh NemoFrame gameplay-start telemetry in the current game.log;
- starts WPR + PresentMon only after gameplay telemetry begins;
- waits for ETS exit;
- finalizes WPR/PresentMon automatically;
- collects project logs into a timestamped trace directory.

The launcher has a `-SelfTestOnly` mode.

That self-test was executed successfully:
- UAC elevation succeeded;
- WPR GeneralProfile.Light + GPU.Light started;
- WPR cancellation succeeded;
- final WPR status was idle;
- ETS2 was not launched.

## Pre-runtime review status

The adversarial review was cross-checked against the compiled wrapper assembly.

One real issue was reproduced and fixed: the RQ wrapper truncated a 64-bit RCX argument because it was declared as `uint32_t`.

Other claimed issues were verified individually rather than accepted automatically. The corrected runtime build is ready for the first controlled capture.

## Run protocol after review

1. launch the one-click tool;
2. approve normal UAC;
3. drive until several characteristic hitches occur;
4. exit ETS normally;
5. launcher finalizes the capture automatically.

No manual START/STOP should be required in the normal path.

## Interpretation rule

ChainProbe measures sampled elapsed wall time, not guaranteed CPU execution time.

ETW scheduling state and PresentMon/GPU data are required before calling a long chain sample a CPU hotspot.
