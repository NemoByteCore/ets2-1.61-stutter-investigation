# Runtime capture pipeline

Status: v0.3 exact-RG correlation run ready.

## Current experiment

The immediate experiment uses:
- NemoFrameLogger v3;
- NemoChainProbe161 v0.3 exact-RG;
- PresentMon 2.6.0.

It intentionally does **not** use WPR/ETW.

Purpose:
replace five-second bucket correlation with direct event/frame QPC overlap.

## PresentMon

Version:
`2.6.0 x64`

SHA-256:
`B2A706BC6AD475749E3B7E3409263AA1E6906D45BDCF993F6DBC0F660188F1AF`

Target:
`eurotrucks2.exe`

Output:
v2 metrics + QPC time.

## v0.3 exact RG

Exact stream:
```text
event_seq,rg_call_seq,qpc_start,qpc_end,duration_ticks,duration_us,thread_id
```

Every RG call is emitted through a ring buffer.

No RG-hook file I/O.

## Launcher

The no-elevation launcher verifies exact hashes and starts the game directly.

No Steam URI.
No WPR.
No UAC.

Capture during the run uses an isolated `%TEMP%\NemoByteCore\ETS2RGV03_<GUID>` directory.

After ETS exits:
- PresentMon is finalized;
- game.log and both ChainProbe v0.3 CSV files are verified fresh;
- clean ChainProbe shutdown markers are required;
- files are archived to the PrismRE workspace;
- only after successful archive verification is the per-run TEMP directory removed.

## Why ETW is deferred

The previous PresentMon capture is already sufficient to show real long-frame events.

The unresolved problem is that v0.2 only identified RG maxima in five-second buckets.

Before paying the cost/complexity of another ETW run, v0.3 will establish exact timing:

Does the specific long PresentMon frame actually overlap a comparably long RG call?

ETW remains available later for:
- ReadyThread / CSwitch;
- CPU sampling;
- DPC/ISR;
- disk I/O;
- DXGI/DxgKrnl scheduling.

## Run protocol

1. run the v0.3 no-UAC launcher;
2. drive normally until several characteristic hitches occur;
3. exit ETS normally;
4. wait for `CAPTURE_COMPLETE`.

No manual START/STOP and no elevation are required.
