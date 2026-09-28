# Runtime baselines

These measurements are from ETS2 1.61.1.1 using `NemoFrameLogger`.

They are not presented as benchmark-grade FPS comparisons. Their purpose is to characterize the recurring frame-time spikes that match the visible hitching.

## Vanilla — DX12 + averaging 200 / 500

26 complete 5-second windows:

| Metric | Result |
|---|---:|
| Frames | 7,688 |
| Maximum frame | 51.608 ms |
| Frames >20 ms | 229 |
| Frames >25 ms | 222 |
| Frames >33 ms | 166 |
| Frames >50 ms | 1 |
| Frames >100 ms | 0 |

Typical window averages were approximately 16.7–17.2 ms.

A 280.408 ms partial UI/garage transition window was excluded from the driving baseline.

### Interpretation

The game can sit near a nominal 60 FPS average while still producing recurring ~33–35 ms frame events and occasional larger spikes. The average therefore understates the perceived hitching.

## ProMods — DX12 + averaging 200 / 500

55 complete windows:

| Metric | Result |
|---|---:|
| Frames | 16,268 |
| Maximum frame | 64.489 ms |
| Frames >50 ms | 2 |
| Frames >100 ms | 0 |

Notable maxima included:

- 64.489 ms
- 59.8 ms
- 44.260 ms
- repeated ~33–35 ms events

The subjective result was still clearly poor despite the absence of >100 ms events.

### Interpretation

ProMods increases workload and can amplify the symptom, but it is not sufficient as a root-cause explanation because the same class of recurring spikes exists in vanilla.

## Internal 55 FPS limiter test

Configuration:

```text
r_vsync "0"
t_limit_fps "55"
r_device "dx12"
t_averaging_window_duration "200"
t_averaging_window_length "500"
```

20 complete windows:

| Metric | Result |
|---|---:|
| Frames | 6,038 |
| Maximum frame | 73.088 ms |
| Frames >20 ms | 66 |
| Frames >25 ms | 5 |
| Frames >33 ms | 3 |
| Frames >50 ms | 1 |
| Frames >100 ms | 0 |

Top events included 73.088 ms, 40.263 ms and 36.076 ms.

Most 5-second windows still contained roughly 300 frames, so the internal limiter did not appear to hold the game at 55 FPS.

### Conclusion

This test was rejected as a practical fix. No further tuning loop is being built around that cvar.

## Current runtime objective

The next run is not another graphics-setting comparison.

It records the normal frame-time stream and the internal candidate-chain timings simultaneously so the spike windows can be correlated against specific engine work.
