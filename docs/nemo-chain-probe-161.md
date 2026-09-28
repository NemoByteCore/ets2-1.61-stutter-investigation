# NemoChainProbe161

`NemoChainProbe161` is an exact-build inline-hook profiler for the current ETS2 1.61 candidate render chain.

## Current status

The original public source in `src/NemoChainProbe161.cpp` is the historical v0.1 design.

The current runtime build is **v0.2 threaded**.

v0.1 should not be used as the decisive correlation build.

## Static chain

The recovered 1.61 relationship is:

```text
1401CBEE0
 -> 1401DBCE0
 -> 140227140
 -> 140226960
 -> [owner+0x1C68]
 -> adapter 1421FD1B0 +0x8
 -> 14022EAA0
 -> contained callback 1423F5530 +0x8
 -> 141476140
 -> 141473E60
 -> 14160D010
 -> 14160D580
 -> 1402E5FF0
```

The middle is an indirect vtable/adapter dispatch. That is why a normal direct-call BFS could not connect `140226960` to `141473E60`.

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

## v0.1 problems

v0.1 emitted cumulative values every approximately five seconds.

Useful totals could be differenced, but cumulative maximum made it impossible to identify the interval in which a long call actually happened.

Its report path also ran from the RG wrapper, creating avoidable observer-effect risk.

## v0.2 threaded changes

Current build:

- size: `58,880` bytes
- SHA-256: `474C9C6925E7B5C486E267CBA03332F5801A3845247E3D188C5707C2020054E2`

Changes:

- QPC interval start/end;
- interval call deltas;
- interval sampled-call deltas;
- interval sampled duration;
- interval maximum;
- sampled-duration buckets >=1/2/4/8/16/33 ms;
- stat structures isolated to separate cache lines;
- reporting moved to a dedicated low-frequency reporter thread;
- RG hot path no longer performs report/CSV I/O;
- exact-build PE/signature validation retained.

Offline validation:

- `LoadLibrary`: OK
- `scs_telemetry_init`: exported
- `scs_telemetry_shutdown`: exported

## Safety model

Before installing any hook the build validates:

- PE timestamp `0x6AB3C451`;
- SizeOfImage `0x0398A000`;
- exact prologue bytes for all eight targets.

A mismatch fails closed.

Partial hook installation failure restores already patched entries.

Normal shutdown restores original prologue bytes.

## Remaining interpretation caveat

The probe records sampled **elapsed wall time**.

A long sample can mean:

- CPU execution;
- lock/wait time;
- scheduler preemption;
- a combination of those.

Therefore a long ChainProbe sample should not automatically be called a CPU hotspot.

The planned WPR/PresentMon capture exists specifically to distinguish those cases.

## Runtime correlation

The matching FrameLogger v3 emits QPC start/end/frequency for its frame windows.

PresentMon is also configured to emit QPC time.

That allows direct overlap against ChainProbe intervals rather than matching independent five-second windows by sequence number.

## Next experiment

Use one combined run with:

- ChainProbe v0.2 threaded;
- NemoFrameLogger v3;
- PresentMon 2.6.0;
- WPR GeneralProfile.Light + GPU.Light.

Then correlate chain timing against:

- frame-time spikes;
- ReadyThread/CSwitch scheduling;
- GPU/present behavior;
- DPC/ISR;
- DiskIO.
