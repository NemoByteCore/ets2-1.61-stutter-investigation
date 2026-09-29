# Runtime capture pipeline

Status: exact plugin-only correlation ready.

## Current experiment

```text
NemoFrameLogger v4 exact-frame
           ↕ QPC
NemoChainProbe161 v0.3 exact-RG
```

No external trace consumer is required.

## Why PresentMon is not used

PresentMon 2.6.0 was explicitly tested without elevation on the current account.

Session start failed with access denied and stated that administrative privilege or Performance Log Users membership is required.

No Windows privilege/group modification was made.

## Outputs

ChainProbe exact RG:
`NemoChainProbe161_v03_rg.csv`

```text
event_seq,rg_call_seq,qpc_start,qpc_end,duration_ticks,duration_us,thread_id
```

FrameLogger exact frames:
`NemoFrameLogger_v4_frames.csv`

```text
event_seq,frame_seq,segment_id,qpc_start,qpc_end,duration_ticks,duration_us,thread_id
```

Both use ring-buffer publication and reporter-thread file I/O.

## Launcher behavior

The no-UAC launcher:
- verifies exact ETS/ChainProbe/FrameLogger hashes;
- launches ETS directly;
- waits for fresh telemetry start;
- starts no WPR and no PresentMon;
- waits for normal ETS exit;
- verifies fresh exact CSVs and clean shutdown markers;
- rejects captures with lost ring events;
- archives directly to the PrismRE workspace.

No runtime TEMP capture is required.

## Correlation

For every long frame:
1. take exact `frame.qpc_start..frame.qpc_end`;
2. find RG intervals that intersect it;
3. calculate overlap and RG/frame duration ratio;
4. compare thread IDs.

This is the measurement that v0.2's five-second buckets could not provide.

## ETW

ETW is deferred.

Use it only if exact correlation leaves a scheduler/wait question that plugin timing cannot answer.
