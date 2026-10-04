# ETS2 1.61 DX12 stutter — creator briefing

**Community-made outreach resource based on NemoByteCore's original investigation.**

The technical investigation summarized here was performed and published by **NemoByteCore**. The reverse engineering, instrumentation, profiler correlation, A/B testing, measurements and evidence archive are his work. This document exists only to make that work easier to communicate accurately to a wider audience.

> **Important:** this is not the canonical technical record. For verification, use the [main investigation](../../README.md) and the [accepted 1.61 runtime evidence](../../evidence/runtime/1.61/README.md).

## The short version

NemoByteCore investigated recurring frame-time spikes in **Euro Truck Simulator 2 1.61.1.1 using DX12** and localized a reproducible stutter class to **cold graphics Pipeline State Object (PSO) creation happening synchronously on the draw path**.

On a cold cache miss, the documented path reaches:

```text
FUN_1402A06D0
  -> FUN_1402AAA60
      -> FUN_14029DD00(..., wait=1)
```

With `wait=1`, the draw path waits for PSO creation to finish before continuing. The investigation repeatedly measured cold-PSO stalls in the **~10–40+ ms** range.

At 60 FPS, the nominal frame budget is about **16.67 ms**. A 20, 30 or 40 ms operation on the latency-critical draw path can therefore create a visible hitch even when the average FPS counter still looks acceptable.

## Why the 27/27 result matters

The same ETS2 build contains an asynchronous PSO preparation path:

```text
FUN_14029E0F0
  -> FUN_14029DD00(..., wait=0)
```

NemoByteCore instrumented that path and compared it with the PSOs that later produced slow synchronous stalls.

The accepted final coverage run recorded:

```text
async_total = 0
slow_total  = 27
slow_seen   = 0
slow_unseen = 27
```

In that run, **27 out of 27 measured slow PSOs had not been observed going through the built-in async preparation path before first use**.

That does not mean “every PSO in the game is broken.” It means that, for the measured stutter class in that run, the PSOs that later blocked the draw path were arriving cold instead of being prepared in advance by the existing async machinery.

## The A/B test

NemoByteCore also changed the relevant lookup from:

```text
FUN_14029DD00(..., wait=1)
```

to:

```text
FUN_14029DD00(..., wait=0)
```

The large synchronous stalls disappeared.

But this was **not a usable fix**. A cold PSO can return as not ready while compilation is still pending, which caused skipped drawing and visible black flashes / incomplete rendering.

That experiment matters because it narrows the engineering problem:

- the expensive work can be moved off the critical draw path;
- simply refusing to wait is not enough;
- the required PSOs need to be discovered and prepared **before first use**.

That is an engine-side problem, not a user configuration tweak.

## What the investigation proves

It is fair to say that:

- NemoByteCore demonstrated a reproducible **engine-side stutter class** in ETS2 1.61.1.1 under DX12;
- cold graphics PSO creation was observed synchronously blocking the draw path;
- the affected PSOs produced measurable stalls large enough to disrupt frame pacing;
- the game build already contains an asynchronous PSO preparation mechanism;
- in the accepted final coverage run, all 27 measured slow PSOs arrived at the later synchronous path without prior observed coverage from that async preparation path;
- forcing the final draw lookup asynchronous removed the large synchronous stalls but broke rendering, proving that preparation must happen earlier rather than simply skipping the wait;
- the underlying stutter class was reproduced in both vanilla and modded ETS2, so mods were not required to produce it.

## What the investigation does **not** prove

Do **not** turn the result into any of these claims:

- “NemoByteCore found the cause of all ETS2 stutter.”
- “Every stutter in ATS has the same cause.”
- “DX11 has been proven to have this exact PSO bug.”
- “27/27 means every PSO in ETS2 is affected.”
- “Changing `wait=1` to `wait=0` is a player fix.”
- “The investigation proves every community performance complaint is caused by this code path.”

The demonstrated scope is narrower and stronger: **one specific, measurable and reproducible stutter class was localized inside the ETS2 1.61.1.1 DX12 rendering path.**

## What happened on the SCS forum

NemoByteCore posted the findings on the official SCS forum. The thread ultimately received a moderator note centered on the absence of a `game.log.txt`, was locked, and its title was marked **[NOT A BUG]**. The repository preserves screenshots and an external archive of the exchange.

A `game.log.txt` is useful for many forms of support: hardware identification, settings, mods, script errors and general environment information. But it does not contain the internal render-thread timing, function-level correlation or async-coverage measurements used in this investigation.

The important outreach point is therefore not “logs are useless.” It is:

> When a report includes profiler evidence, controlled A/B testing and instrumentation of the rendering path, that evidence deserves a technical response at the same level.

See the [forum evidence archive](../../evidence/forum/README.md).

## The wider Prism3D question

The investigation is about a specific DX12 stall class, but it also raises a broader question about renderer architecture and technical debt.

SCS has publicly discussed the age and accumulated technical debt of its engine. That does **not** by itself prove that every performance problem has the same architectural cause. It does, however, make it reasonable for the community to ask how SCS plans to keep latency-critical rendering work off the frame path as ETS2 and ATS continue to evolve.

The engineering question identified by the project is now very specific:

> Why are graphics PSOs reaching the synchronous draw path cold while the existing asynchronous preparation path is not covering them before first use?

Possible engine-side directions listed by the investigation include better PSO discovery / warm-up coverage, using the existing async path earlier, appropriate persistent caching where the architecture allows it, and avoiding render-thread waits on cold PSO creation during normal driving.

## What the community can reasonably ask SCS for

A technically serious response does not require SCS to accept every conclusion automatically. Useful responses could include:

- reproducing or disproving the measured path;
- explaining why the async-coverage interpretation is wrong, if it is wrong;
- correcting the preparation path;
- showing measurable frame-time improvements;
- documenting the intended future of the DX11/DX12 renderers;
- describing how renderer regressions and frame-time spikes are being tested;
- explaining how Prism3D's graphics architecture is being modernized where necessary.

The request is not “agree with the community.” The request is **answer technical evidence with technical evidence**.

## Guidance for creators

### Good framing

Use language such as:

- “NemoByteCore demonstrated a specific engine-side source of stutter in ETS2 1.61.1.1 under DX12.”
- “The investigation measured cold PSO creation blocking the draw path.”
- “In the accepted coverage run, 27/27 measured slow PSOs had not been seen through the built-in async preparation path before first use.”
- “The test that removed the wait also broke rendering, so this is not a simple user-side patch.”
- “The finding does not explain every ETS2 or ATS stutter.”

### Avoid

Avoid headlines or narration such as:

- “The cause of ETS2 stutter has finally been solved.”
- “SCS intentionally makes the game stutter.”
- “This proves every performance problem is Prism3D.”
- “Here is the one-line fix SCS refuses to apply.”

The evidence is already strong. Overstating it only gives critics an easy way to dismiss the real result.

## Suggested titles

- **A player traced an ETS2 1.61 stutter into the DX12 renderer**
- **NemoByteCore found a measurable engine-side stutter in ETS2 1.61**
- **27/27: what the ETS2 DX12 stutter investigation actually found**
- **ETS2 can show 60 FPS and still hitch — here is one proven reason why**

## Primary sources

For the complete evidence and current wording, use:

- [Main investigation README](../../README.md)
- [Accepted 1.61 runtime evidence](../../evidence/runtime/1.61/README.md)
- [Manifesto](../../MANIFESTO.md)
- [What we want from SCS](../../WHAT_WE_WANT_FROM_SCS.md)
- [Community stutter tracker](../../COMMUNITY_STUTTER_TRACKER.md)
- [Forum evidence archive](../../evidence/forum/README.md)

## Attribution

If you cover or reuse this briefing, please make the original source clear:

> **Original technical investigation: NemoByteCore — `ets2-1.61-stutter-investigation`**

Linking directly to the repository allows viewers and readers to inspect the evidence themselves.
