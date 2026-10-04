# What We Want From SCS

This is the narrow request.

The public investigation has already identified one reproducible engine-side stutter mechanism in ETS2 1.61.1.1 DX12. The useful next step is not another round of generic player-side troubleshooting. It is a technical response to the evidence and an engine-side plan.

## 1. Address the 27/27 async-coverage result

The central result is:

```text
async_total = 0
slow_total  = 27
slow_seen   = 0
slow_unseen = 27
```

All 27 measured slow PSOs reached synchronous first use without prior coverage from the existing async preparation path.

The question is simple:

> Why are graphics PSOs reaching `FUN_1402AAA60` cold and forcing `FUN_14029DD00(..., wait=1)`, while the existing `FUN_14029E0F0 -> FUN_14029DD00(..., wait=0)` preparation path is not covering them before first draw?

A technical answer to that question would address the actual finding.

## 2. Keep cold PSO compilation off the latency-critical draw path

The controlled `wait=0` experiment showed that removing the synchronous wait removes the large stall, but a still-pending PSO can cause the draw to be skipped.

That means simply changing one flag is not the solution.

The engine needs to ensure required PSOs are prepared before first use.

Possible engine-side directions include:
- improving async PSO discovery / coverage;
- scheduling preparation after required dependencies are valid but before first draw;
- persisting appropriate pipeline-cache data between runs where the architecture permits it;
- avoiding synchronous cold compilation during normal driving.

The exact implementation is SCS's engineering decision. The requirement is the important part: cold PSO work should not block the draw path during gameplay.

## 3. Treat profiler evidence as profiler evidence

A `game.log.txt` can be useful for configuration, hardware, mod and script information.

It cannot substitute for:
- render-thread timing;
- PSO compilation timing;
- call-path instrumentation;
- async-coverage measurements.

When a report includes instrumented evidence outside the scope of `game.log.txt`, the response process should be able to engage with that evidence directly rather than treating the absence of a game log as proof that there is no bug.

## 4. Clarify renderer status without using status as a technical answer

SCS can say that a renderer is experimental or unsupported.

That is a product-support statement.

It does not answer whether a reproducible defect exists inside that renderer.

For the investigated 1.61.1.1 DX12 build, the cold-PSO synchronous stall and missing async coverage were measured directly. A support-status label does not change that technical result.

## 5. Publish a concrete stutter / renderer improvement plan

Players do not need a promise that every hitch will disappear immediately.

A useful response would be a concrete plan covering areas such as:
- shader / PSO preparation;
- render-thread stall reduction;
- pipeline-cache behavior;
- frametime consistency;
- regression testing across renderer and game updates.

Even a staged plan is more useful than repeatedly pushing every report back toward local settings.

## What this document is not asking for

This document is not claiming:
- that every ETS2 or ATS stutter report has the same root cause;
- that the exact 1.61 DX12 mechanism has been proven on DX11;
- that the exact mechanism has been proven on ATS;
- that one external patch should be adopted as-is;
- that SCS must rewrite the entire renderer immediately.

It is asking for a technical response to a specific measured result, followed by an engine-side fix or a credible engineering plan.

## Evidence

Full investigation:
https://github.com/NemoByteCore/ets2-1.61-stutter-investigation

Accepted 1.61 runtime evidence:
[evidence/runtime/1.61/README.md](evidence/runtime/1.61/README.md)

Official SCS forum thread:
https://forum.scssoft.com/viewtopic.php?t=354183

Locked-thread permalink:
https://forum.scssoft.com/viewtopic.php?p=2163160#p2163160

Wayback snapshot:
https://web.archive.org/web/20261002223936/https://forum.scssoft.com/viewtopic.php?t=354183
