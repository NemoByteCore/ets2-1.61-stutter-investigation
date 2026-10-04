# What We Want From SCS

## Fix the game engine, not the player's settings

This is the actual request:

> **Fix the engine-level performance problems in ETS2 and ATS. Modernize Prism3D where it can be modernized. Substantially rewrite or replace the parts that cannot deliver stable frametimes anymore.**

That request does **not** depend on DX12 being officially supported.

If SCS considers DX12 experimental, unsupported or unfinished, fine. Then the responsibility is even clearer: the supported renderer and the engine underneath it still need to provide stable gameplay, and SCS should explain what concrete work is being done to achieve that.

The point is not "please support my preferred API."

The point is:

> **Stop shipping a game that repeatedly produces stutter and frametime complaints, then treating those complaints as something players are expected to solve locally.**

## Stop using support-script answers as substitutes for engine work

When players report recurring stutter, microstutter or bad frametimes, the default answer cannot forever be:

- send `game.log.txt`;
- disable mods;
- change settings;
- try another FPS cap;
- disable overlays;
- use another renderer;
- "other users can play without stutters."

Those checks can be useful for ordinary troubleshooting.

They are not a substitute for investigating the engine when:
- the problem survives clean profiles and reinstallations;
- multiple users report similar symptoms on different hardware;
- older versions are reported as smoother than newer ones;
- average FPS looks normal while frametime behavior is poor;
- instrumented evidence points directly into the renderer.

If a player has supplied profiler traces, controlled A/B tests, timings and call-path instrumentation, answer that evidence on its merits.

## The DX12 investigation is evidence, not the whole case

One specific engine-side stutter mechanism was proven on ETS2 1.61.1.1 DX12.

Cold graphics PSOs reached the draw path synchronously:

```text
FUN_1402A06D0
-> FUN_1402AAA60
-> FUN_14029DD00(..., wait=1)
```

The same build contains an async preparation path:

```text
FUN_14029E0F0
-> FUN_14029DD00(..., wait=0)
```

Final measured coverage:

```text
async_total = 0
slow_total  = 27
slow_seen   = 0
slow_unseen = 27
```

All 27 measured slow PSOs reached synchronous first use without prior observed coverage from that async path.

Forcing `wait=0` removed the large synchronous stalls but caused skipped draws / black flashes while compilation was still pending. That makes it diagnostic evidence, not a user fix.

This exact mechanism is **not** being claimed for every stutter report, for DX11, or for ATS.

It matters because it proves a broader point: at least one visible stutter class was demonstrably engine-side and required engine-side work.

So "DX12 is not ready" does not end the discussion.

If SCS rejects DX12 evidence as out of scope, then show the plan for stable frametimes on the renderer that *is* in scope.

## Fix, modernize or replace the parts of Prism3D that are holding the games back

Players should not care whether the final answer is:
- a targeted renderer fix;
- a major Prism3D modernization;
- a substantial graphics-layer rewrite;
- replacement of individual legacy subsystems;
- or a larger engine transition.

That is SCS's engineering decision.

What matters is the result:

- stable frametimes;
- no recurring engine-side hitching during normal gameplay;
- proper shader / pipeline preparation;
- no avoidable render-thread stalls;
- renderer behavior that does not regress badly between updates;
- a technical foundation that can support future content without degrading the base experience.

If Prism3D can meet that standard after modernization, modernize it.

If parts of it cannot, replace those parts.

If the architecture itself has become the blocker, change the architecture.

## Stop treating paid DLC as more important than the foundation every DLC depends on

ETS2 and ATS continue to receive paid content.

That makes maintaining the underlying game more important, not less.

We want SCS to give engine, renderer and frametime work higher priority than continuously expanding the paid-DLC pipeline while core performance complaints remain unresolved.

If the company does not have enough engineering capacity to do both properly, then slow or pause new paid DLC releases until the technical foundation is under control.

This is not saying map artists should become renderer engineers.

It is saying SCS as a company should allocate enough time, staffing and money to the part of the product every map, truck and DLC depends on.

More content running on a struggling foundation does not solve the foundation.

## Stop using renderer status as an escape hatch

If DX12 is experimental, say so.

But then answer the obvious follow-up:

> What is SCS doing to guarantee stable frametimes on the renderer players are actually expected to use?

"DX12 is not ready" cannot be the end of the conversation when the wider complaint is "the game stutters."

Likewise, "works for other users" does not disprove a reproducible problem affecting a subset of machines, workloads or code paths.

Support status and technical reality are separate questions.

## Give players a real engine roadmap

We want a public plan for the technical foundation of ETS2 and ATS.

It should cover, at minimum:

- frametime consistency;
- render-thread stalls;
- shader / pipeline-state preparation and caching;
- DX11 / DX12 direction;
- regression testing between game versions;
- what parts of Prism3D are being modernized;
- what parts are being substantially rewritten or replaced;
- how engine work is being prioritized relative to continued DLC production.

It does not need to promise that every hitch disappears overnight.

It does need to show that SCS recognizes the engine itself as something that requires active investment rather than treating recurring stutter reports as endless local troubleshooting exercises.

## What would count as an actual response

A serious response could be any of the following:

- acknowledge that engine-side frametime problems are being investigated;
- publish a renderer / engine improvement roadmap;
- explain what is being done on the supported renderer to reduce recurring stutter;
- fix the proven cold first-use PSO path in DX12;
- show that the technical conclusion is wrong and provide evidence;
- demonstrate measurable frametime improvements in future builds;
- explain what architectural work is being done to prevent repeat regressions.

What does **not** answer the wider issue:

- another generic settings checklist;
- `works for me`;
- `send game.log` as a substitute for profiler evidence;
- `DX12 is experimental` as if that ends every discussion about engine performance;
- continuing to ship paid content without a credible plan for the technical foundation.

## The point

This is not a campaign for one DX12 bug.

It is a demand for SCS to take responsibility for the technical foundation of the games it continues to sell and expand.

**Fix the engine-level problems. Modernize Prism3D. Replace the parts that cannot be brought up to standard. Stop hiding recurring performance complaints behind local troubleshooting and renderer-status arguments. And give core engine work at least the priority currently given to producing more paid content.**

## Evidence

Full investigation:
https://github.com/NemoByteCore/ets2-1.61-stutter-investigation

Community stutter tracker:
[COMMUNITY_STUTTER_TRACKER.md](COMMUNITY_STUTTER_TRACKER.md)

Accepted 1.61 DX12 runtime evidence:
[evidence/runtime/1.61/README.md](evidence/runtime/1.61/README.md)

Historical 1.60 investigation:
[legacy/1.60/README.md](legacy/1.60/README.md)

Official SCS forum thread:
https://forum.scssoft.com/viewtopic.php?t=354183

Locked-thread permalink:
https://forum.scssoft.com/viewtopic.php?p=2163160#p2163160

Wayback snapshot:
https://web.archive.org/web/20261002223936/https://forum.scssoft.com/viewtopic.php?t=354183
