# ETS2 exact frame/RG analysis

Analyzer version: 1.0.0
Analyzer SHA-256: 4013CD77B74EB8D216416539B020F8DE6EB8109700A2C92D574EADC61DB69600
Capture: accepted exact v0.3/v4 runtime capture from 2026-09-29.

## Integrity

| Check | Result |
| --- | --- |
| RG SHA-256 | F7C06B4BE4881E09FAC2DF55AA2C41EED45A33CE9221A0FB8E62ACD07BF8BF88 |
| Frame SHA-256 | DED05136D3D72AFF6A7AC0028B76A7FC733503CBE28EDD197F714865D67853E0 |
| Shared QPC frequency | 10000000 |
| RG rows / shutdown events | 34534 / 34534 |
| Frame rows / shutdown events | 33214 / 33214 |
| RG lost | 0 |
| Frame lost | 0 |
| Segments | 4 |
| RG qpc_start decreases in event_seq order | 0 |
| RG qpc_end decreases in event_seq order | 0 |
| Frame qpc_start decreases in event_seq order | 0 |
| Frame qpc_end decreases in event_seq order | 0 |

All event_seq values are contiguous 1..N; row counts match clean shutdown counters; duration ticks and stored microseconds were validated against QPC.

## Frame distribution

- total frame intervals: 33214
- >=25 ms: 12
- >=33 ms: 3
- >=50 ms: 1
- p50: 18.044 ms
- p95: 19.202 ms
- p99: 19.808 ms

Percentiles use floor-index selection on the sorted sample: floor((N-1)*p).

## RG timing

- total RG calls: 34534
- RG duration p50: 4.412 ms
- RG duration p95: 6.875 ms
- RG duration p99: 7.951 ms
- RG duration max: 32.161 ms

- frames with >=1 RG overlap: 30441 / 33214
- frames with >1 RG overlap: 0
- matching frame/RG thread IDs when overlap exists: 30441 / 30441
- RG-overlap p50: 4.449 ms
- RG-overlap p95: 6.912 ms
- RG-overlap p99: 7.956 ms
- residual p50: 13.401 ms
- residual p95: 14.974 ms
- Pearson(frame duration, RG overlap): 0.7982
- Pearson(frame duration, residual): 0.9628

## Timing bins

| Bin | N | Avg frame ms | Avg RG overlap ms | Avg residual ms | RG overlap >=50% |
| --- | ---: | ---: | ---: | ---: | ---: |
| <20 ms | 32999 | 16.626 | 4.334 | 12.291 | 12 |
| 20-25 ms | 203 | 20.870 | 6.066 | 14.804 | 4 |
| 25-33 ms | 9 | 28.837 | 14.084 | 14.754 | 5 |
| >=33 ms | 3 | 52.598 | 15.143 | 37.455 | 1 |

## Ordinary vs long-frame RG

- ordinary frames (<20 ms), overlapping RG call duration: p50 4.554 ms, p95 6.957 ms, p99 7.944 ms
- long frames (>=25 ms), overlapping RG call duration: p50 12.953 ms, p95 21.653 ms, p99 21.653 ms

## First measured interval of each segment

| Segment | Frame seq | Duration ms | RG overlap ms | Residual ms |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 75.689 | 8.669 | 67.020 |
| 2 | 1801 | 18.582 | 4.190 | 14.392 |
| 3 | 13480 | 17.891 | 4.254 | 13.637 |
| 4 | 28638 | 17.984 | 5.032 | 12.952 |

First-of-segment is a structural tag only. The analyzer does not automatically discard it.

## All frame intervals >= 25 ms

| Frame | Segment | First? | Frame ms | RG count | RG overlap ms | Overlap % | Residual ms | Max RG call | Max RG ms | Frame TID | RG TID |
| ---: | ---: | :---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | yes | 75.689 | 1 | 8.669 | 11.45 | 67.020 | 1720 | 8.669 | 3384 | 3384 |
| 6762 | 2 | no | 46.626 | 1 | 32.161 | 68.98 | 14.465 | 8523 | 32.161 | 3384 | 3384 |
| 10139 | 2 | no | 35.478 | 1 | 4.599 | 12.96 | 30.879 | 11618 | 4.598 | 3384 | 3384 |
| 29520 | 4 | no | 32.569 | 1 | 21.654 | 66.49 | 10.915 | 29869 | 21.653 | 3384 | 3384 |
| 9615 | 2 | no | 32.285 | 1 | 18.868 | 58.44 | 13.417 | 11137 | 18.868 | 3384 | 3384 |
| 24710 | 3 | no | 29.961 | 1 | 17.193 | 57.38 | 12.768 | 25343 | 17.192 | 3384 | 3384 |
| 4842 | 2 | no | 29.156 | 1 | 3.850 | 13.20 | 25.306 | 6763 | 3.849 | 3384 | 3384 |
| 20108 | 3 | no | 28.942 | 1 | 16.129 | 55.73 | 12.813 | 21125 | 16.128 | 3384 | 3384 |
| 12618 | 2 | no | 28.661 | 1 | 15.389 | 53.69 | 13.272 | 13890 | 15.389 | 3384 | 3384 |
| 27696 | 3 | no | 27.264 | 1 | 12.953 | 47.51 | 14.311 | 28081 | 12.953 | 3384 | 3384 |
| 18659 | 3 | no | 25.442 | 1 | 10.639 | 41.82 | 14.803 | 19797 | 10.639 | 3384 | 3384 |
| 7479 | 2 | no | 25.257 | 1 | 10.080 | 39.91 | 15.177 | 9179 | 10.079 | 3384 | 3384 |

## Threshold-only mechanical observations

- >=25 ms excluding first-of-segment: 11 intervals.
- among those, max overlapping RG >=10 ms: 9 / 11.
- among those, RG overlap >=50% of frame interval: 6 / 11.

These are threshold counts, not causal labels. RG duration is elapsed wall time and may include execution, waiting, synchronization or scheduler preemption.

## Output semantics

RG overlap is the union of all RG intervals intersecting the frame interval. This avoids double-counting if overlapping or nested RG events ever occur.
Residual = frame_start-to-frame_start duration minus RG-overlap union. It is not automatically equivalent to CPU execution outside RG.
RESULTS.csv contains every frame interval at or above the configured threshold, with exact QPC overlap details and all overlapping RG call IDs.
