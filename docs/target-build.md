# Target build: ETS2 1.61.1.1

This investigation is pinned to one exact executable.

## Executable identity

| Field | Value |
|---|---|
| Version | `1.61.1.1` |
| Revision | `6949e633e77902f7e023819d3131cc6ccce3707f` |
| SHA-256 | `EB17944139BE4DE3D70D0CD57CDAA7C52C9E326ECF2D0DD3EA2F806545C74A53` |
| File size | `53,300,040` bytes |
| PE timestamp | `0x6AB3C451` |
| SizeOfImage | `0x0398A000` |

Addresses, signatures and runtime hooks in this repository are valid only for this build unless explicitly remapped and revalidated.

## Runtime renderer / pacing state used for the current baseline

Current primary renderer:

```text
r_device "dx12"
t_averaging_window_duration "200"
t_averaging_window_length "500"
```

A later limiter test also used:

```text
r_vsync "0"
t_limit_fps "55"
```

That limiter test did not hold a stable 55 FPS and was not accepted as a solution.

## Instrumentation

Two independent data streams are used.

### NemoFrameLogger

Uses the public SCS telemetry API and records 5-second windows:

- average frame time,
- maximum frame time,
- counts above 20 / 25 / 33 / 50 / 100 ms.

It does not depend on internal 1.60 addresses.

### NemoChainProbe161

Exact-build internal timing probe for the current candidate chain.

Before installing any hooks it validates:

- PE timestamp,
- SizeOfImage,
- exact prologue bytes for all eight hooked functions.

A mismatch causes fail-closed initialization: no hooks are installed.

## Reproducibility rule

Do not transfer raw addresses from another ETS2 build.

The 1.60 archive is used only as a source of semantic and structural anchors. 1.61 targets are recovered through static matching, call-graph reconstruction and build-specific instruction validation.
