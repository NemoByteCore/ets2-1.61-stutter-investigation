# NemoChainProbe161

`NemoChainProbe161` is an exact-build inline-hook profiler for the current ETS2 1.61 candidate render chain.

## Current runtime build

**v0.3 exact-RG**

- size: `61,952` bytes
- SHA-256: `DAD26A46EE67FBA81039C3994E8205C739548A14262BEBCC75977442B4B29A3E`

v0.2 remains important historical evidence but is no longer the deployed build.

## Static chain

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

## Hook set

| Label | VA | Aggregate sampling |
|---|---:|---:|
| RG-owner candidate | `140227140` | 1 / 1 |
| T1-like candidate | `140226960` | 1 / 8 |
| nested winner | `141473E60` | 1 / 16 |
| RQ_ONE | `14160D010` | 1 / 16 |
| HEAD_DISPATCH | `14160D580` | 1 / 16 |
| downstream dispatch | `1402E5FF0` | 1 / 16 |
| BUNDLE_BUILD | `1402E5040` | 1 / 64 |
| DX12 descriptor builder | `14029F9B0` | 1 / 64 |

RG additionally receives an exact event for **every call** in v0.3.

## Why v0.3 exists

v0.2 fixed cumulative-max/report-thread problems but still summarized data in roughly five-second windows.

That is inadequate for statements such as:
"a 71 ms PresentMon frame contained the 10 ms RG maximum from the same five-second bucket."

Those two events might be separated by several seconds.

v0.3 removes this ambiguity.

## Exact RG stream

Columns:

```text
event_seq,rg_call_seq,qpc_start,qpc_end,duration_ticks,duration_us,thread_id
```

Properties:
- every RG call is recorded;
- QPC end is taken immediately after the trampoline returns;
- duration therefore excludes later ring publication and thread-ID retrieval;
- 65,536 event slots;
- producer path contains no CSV/file write;
- reporter thread drains events;
- clean shutdown reports total event count and lost-event count.

Expected RG rate from earlier runs is around 55 calls/s, leaving large capacity margin for normal short captures.

## Existing aggregate stream

v0.3 retains the v0.2 summary statistics:
- call/sample counts;
- sampled elapsed duration;
- interval max;
- >=1/2/4/8/16/33 ms buckets;
- QPC interval bounds.

## ABI validation

The earlier RQ declaration bug was fixed before runtime investigation:
the first RQ argument is 64-bit.

The v0.3 compiled DLL was re-checked and still forwards the full RCX value with 64-bit moves before the trampoline call.

Validation:
- LoadLibrary: OK
- telemetry init export: OK
- telemetry shutdown export: OK

## Interpretation caveat

RG duration remains **elapsed wall time**.

A long exact event can contain:
- CPU execution;
- preemption;
- synchronization/wait time;
- combinations of these.

v0.3 solves **when** the RG event occurred relative to a frame. It does not by itself prove **why** the call took that long.

## Next experiment

Run PresentMon + FrameLogger + v0.3 exact-RG without WPR.

Then directly intersect individual PresentMon frame QPC intervals with RG event QPC intervals.

Decision:
- long frame and comparably long RG -> inspect inside RG;
- long frame and short RG -> move profiling outside/above RG;
- unresolved scheduling semantics -> targeted ETW.
