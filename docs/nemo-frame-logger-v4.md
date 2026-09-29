# NemoFrameLogger v4

NemoFrameLogger v4 adds exact per-frame interval telemetry for the ETS2 1.61 investigation.

## Build

- size: `55,296` bytes
- SHA-256: `B1D6D9E93FC466D5F31E650E2567B4EA4D5541B0675D4CED37AF1A7D6782F413`

Offline validation:
- LoadLibrary: OK
- `scs_telemetry_init`: exported
- `scs_telemetry_shutdown`: exported

## Measurement

The plugin registers for:
`SCS_TELEMETRY_EVENT_frame_start`

A frame interval is measured between consecutive frame-start callback QPC timestamps.

The first callback after a started/resumed segment establishes the baseline and is not emitted as an interval.

Intervals above five seconds are treated as discontinuities rather than normal frames.

## Exact output

```text
event_seq,frame_seq,segment_id,qpc_start,qpc_end,duration_ticks,duration_us,thread_id
```

Segment ID increments on each telemetry `started` event.

## Hot-path design

The frame callback:
- reads QPC;
- publishes a compact event to a 65,536-slot ring;
- updates the historical five-second aggregate counters.

It does not write CSV directly.

A reporter thread drains the exact-event ring.

Clean shutdown records:
- total frame events;
- lost-event count;
- number of started segments.

## Purpose

The exact frame stream shares the same QPC clock as NemoChainProbe161 v0.3.

This enables direct frame/RG overlap without PresentMon, WPR or elevation.
