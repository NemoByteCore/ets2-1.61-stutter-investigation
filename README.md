# ETS2 1.61 DX12 Stutter — Independent Player Investigation

Independent reverse-engineering notes from a player who wanted to find out why **Euro Truck Simulator 2 1.61 (DX12)** keeps stuttering.

**Not affiliated with SCS Software. Not commissioned by SCS. Not made for SCS.**

I investigated this for myself because the game was stuttering badly enough to make me dig into Prism3D. The repository remains public only because the results are useful evidence and because I am not going to keep doing unpaid renderer work for the game's developers.

## Status

> **Investigation closed. I found the engine-side problem I was looking for, and I'm not doing SCS's renderer work for them.**

This repository is no longer an active reverse-engineering project. It is being kept public as a record of what I found. SCS can use the evidence if they want to fix their renderer, but producing a vendor-ready engineering package was never the purpose of this project.

After narrowing the issue from frame-time spikes down to the DX12 draw path, the remaining problem is clear enough that continuing to build external patches no longer makes sense.

## Final finding

The dominant stutter class investigated here is caused by **cold DX12 graphics pipeline state object (PSO) creation happening synchronously on the draw path**.

Relevant path in ETS2 1.61.1.1:

```text
FUN_1402A06D0
  -> FUN_1402AAA60
      -> FUN_14029DD00(..., wait=1)
```

On a cache miss, `FUN_14029DD00` creates a `compile_pipeline_task_t`. With `wait=1`, the draw path waits for pipeline creation to finish before continuing.

Measured cold-PSO stalls repeatedly landed in the **~10–40+ ms** range.

## What was tested

### 1. Exact DX12 localization

The stutter chain was narrowed from broad RG timing to:

```text
RG
-> post-T1
-> DX12 +0x108
-> FUN_1402A06D0
-> FUN_1402AAA60
-> FUN_14029DD00
```

The accepted profiler captures showed the DX12 +0x108 path dominating the post-T1 stall class.

### 2. Forced async at the draw call

Changing the AAA60 PSO lookup from:

```text
FUN_14029DD00(..., wait=1)
```

to:

```text
FUN_14029DD00(..., wait=0)
```

removed the large synchronous AAA60 stalls.

That was not a valid final fix: a cold PSO returns `0xFFFF` while compilation is pending, so the draw can be skipped. In practice this produced visible black flashes / missing rendering.

Conclusion: the expensive work can be moved off the draw path, but it must happen **before first use**, not at first draw.

### 3. Hard-coded prewarm

A later experiment captured slow PSO keys and attempted to prepare them in advance.

This also failed as a general solution:
- PSO keys encountered on the next drive were different;
- cold PSOs are workload/content dependent;
- synchronous prewarming simply moved some stalls earlier;
- individual prewarm calls still reached several milliseconds, including a ~35 ms call.

A per-run static key list is therefore a dead end.

### 4. Built-in async PSO preparation

ETS2 already contains an asynchronous preparation path:

```text
FUN_14029E0F0
  -> FUN_14029DD00(..., wait=0)
```

A targeted coverage probe compared this path with the later synchronous AAA60 stalls.

Final v0.14 result from one normal drive:

```text
async_total = 0
slow_total  = 27
slow_seen   = 0
slow_unseen = 27
```

**27/27 measured slow AAA60 PSOs had never been submitted through the built-in async preparation path.**

Representative measured synchronous stalls in that run included:

```text
9.958 ms
10.331 ms
11.247 ms
11.617 ms
11.990 ms
12.821 ms
13.303 ms
14.674 ms
16.416 ms
19.936 ms
22.351 ms
```

This is why this investigation is being stopped here: the engine already contains the machinery needed to compile PSOs asynchronously, but the affected DX12 draw flow does not use it before first use.

## What SCS should investigate

The useful engineering question is no longer “where is the hitch?”

It is:

> Why are graphics PSOs reaching `FUN_1402AAA60` cold and forcing `FUN_14029DD00(..., wait=1)`, while the existing `FUN_14029E0F0` async preparation path is not covering those PSOs before first use?

A proper engine-side solution could include:
- ensuring required graphics PSOs are submitted to the existing async compilation path before first draw;
- improving PSO discovery / warm-up coverage;
- persisting an appropriate PSO cache between runs if the engine architecture supports it;
- avoiding render-thread waits on cold PSO creation during normal driving.

## Why this repository remains public

I am not going to keep reverse-engineering and patching a commercial game's renderer from the outside.

The repo stays public because the measurements, tooling and results may still be useful to:
- SCS developers investigating the DX12 stutter;
- other players trying to establish whether their hitching has the same cause;
- anyone reproducing the findings on the same game build.

The investigation is **closed**, not abandoned due to lack of evidence.

## Build investigated

- ETS2: **1.61.1.1**
- revision: `6949e633e77902f7e023819d3131cc6ccce3707f`
- executable SHA-256: `EB17944139BE4DE3D70D0CD57CDAA7C52C9E326ECF2D0DD3EA2F806545C74A53`
- renderer: DX12

## Scope

This repository does not redistribute the ETS2 executable, DLC/map assets, ProMods files or full proprietary decompiler dumps.

See the repository history and `docs/` for earlier localization work and instrumentation.
