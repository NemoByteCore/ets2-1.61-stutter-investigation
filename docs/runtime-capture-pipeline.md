# Runtime capture pipeline

Status: PresentMon/ChainProbe runtime evidence acquired. One final ETW capture remains.

## Goal

The final broad run combines:
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

Purpose:
- SampledProfile
- ReadyThread / CSwitch
- DPC / ISR
- DiskIO
- DXGI / DxgKrnl / GPU scheduling

## Tool location / temporary elevation staging

Canonical tooling lives on the PrismRE workspace drive.

The launcher stages only itself and PresentMon into a unique `%TEMP%` directory before UAC elevation. The parent process watches marker files rather than waiting on the elevated PID, archives the result back to the workspace, then removes temporary staging.

No persistent Clevo trace-tool directory is required.

## One-click launcher

Current direct launch target:
`D:\Games\Euro Truck Simulator 2\bin\win_x64\eurotrucks2.exe`

Expected SHA-256:
`EB17944139BE4DE3D70D0CD57CDAA7C52C9E326ECF2D0DD3EA2F806545C74A53`

Steam is not part of the launch path.

The launcher:
- self-elevates through UAC;
- verifies exact ETS/tool/plugin hashes;
- refuses to interfere with an existing WPR session;
- launches ETS directly;
- waits for fresh NemoFrame gameplay telemetry;
- starts WPR + PresentMon;
- waits for ETS exit;
- stops/finalizes WPR **before** any PresentMon cleanup;
- verifies ETL creation;
- archives capture data back to the workspace.

Latest launcher SHA-256:
`8FF71233E9DB96774D34D10397B700524E3988779BCF1EDD94DE8A1197F4B4DA`

## Why the previous ETL was lost

The previous order attempted a PresentMon termination helper before `wpr -stop`.

PresentMon emitted a warning on stderr. PowerShell Stop behavior sent execution into `catch`, which canceled WPR instead of saving the ETL.

Current order guarantees ETL finalization first.

## Existing runtime evidence

The previous PresentMon capture is already useful and should not be repeated merely for frame classification.

It captured 14,670 rows and spikes up to ~72 ms.

The remaining purpose of the final run is specifically ETW classification:
- CPU execution vs scheduler wait;
- worker wakeup / synchronization;
- submit / present dependency;
- driver/DPC activity;
- disk activity.

## Final run protocol

1. launch the one-click tool;
2. approve UAC;
3. drive normally until several characteristic hitches occur;
4. exit ETS normally;
5. wait for capture archive confirmation.

No manual START/STOP is required.

## Interpretation rule

ChainProbe measures sampled elapsed wall time, not guaranteed CPU execution time.

PresentMon provides frame/GPU timing, but ETW scheduler state is required before calling a long chain sample a CPU hotspot or synchronization stall.
