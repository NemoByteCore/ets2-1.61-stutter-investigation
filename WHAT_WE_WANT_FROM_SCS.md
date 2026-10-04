# What We Want From SCS

## Fix the foundation of the game

This is not a request for another `config.cfg` tweak, another generic troubleshooting checklist, or another argument about whether one renderer is officially ready.

The request is simpler:

> **Fix the engine-level performance problems that are damaging normal gameplay. Modernize Prism3D where it can be modernized. Replace or substantially rewrite the parts that cannot be made reliable.**

Players should not have to reverse-engineer a commercial game's renderer to prove that a visible stutter is happening inside the engine.

## Stop treating engine problems as player-side problems by default

When a report includes profiler traces, controlled A/B tests, call-path instrumentation and reproducible timings, answers such as:

- `send game.log`;
- `DX12 is not ready`;
- `other users can play without stutters`;
- `try different settings`;

are not technical answers to that evidence.

A `game.log.txt` can be useful for configuration, hardware, scripts and mods. It cannot contain the render-thread timing or PSO instrumentation used in this investigation.

If SCS disagrees with the evidence, challenge the evidence. If the mechanism is understood, fix it. Do not substitute a support-script response for an engineering response.

## Fix, modernize or replace the renderer components that cannot deliver stable frametimes

The investigation in this repository proved one specific engine-side stutter mechanism in ETS2 1.61.1.1 DX12:

```text
FUN_1402A06D0
-> FUN_1402AAA60
-> FUN_14029DD00(..., wait=1)
```

Cold graphics PSOs reached first use synchronously and produced large gameplay stalls.

The same build already contains an async preparation path:

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

Forcing `wait=0` removed the large synchronous stalls but caused skipped draws / black flashes while compilation was still pending. That shows why a player-side flag flip is not the solution: the engine has to prepare the required work before first use.

This exact mechanism was proven for the investigated 1.61.1.1 DX12 build. It is not being claimed as the explanation for every ETS2 or ATS stutter report.

The broader demand is straightforward: **stable frametimes have to become an engine responsibility, not something players are expected to patch around.**

If the existing Prism3D architecture can be brought up to that standard, modernize it.

If parts of it cannot, replace or substantially rewrite those parts.

## Stop prioritizing an endless DLC pipeline over the condition of the base game

ETS2 and ATS are long-running commercial products with a continuing stream of paid content.

That makes the condition of the underlying game more important, not less.

We want SCS to stop treating new paid DLC as a higher priority than long-standing engine, renderer and frametime problems.

If engineering capacity is insufficient to do both properly, then the sensible priority is the foundation that every existing and future DLC depends on.

That can mean slowing or pausing new paid DLC releases while core performance work is brought under control.

This is not an argument that map artists or asset creators should suddenly become renderer engineers. It is a request for SCS as a company to allocate enough time, staffing and budget to the engine instead of allowing the content pipeline to continue indefinitely while fundamental performance complaints remain unresolved.

## Stop hiding behind renderer-status arguments

Saying that DX12 is experimental or not the primary supported renderer may explain support policy.

It does not make a measured engine defect disappear.

Likewise, saying that some other users do not stutter does not disprove a reproducible bug affecting a particular path, workload or subset of machines.

Support status and technical reality are different questions.

## Give players a real engine roadmap

We want a public plan for the technical foundation of ETS2 and ATS, including:

- frametime consistency;
- render-thread stalls;
- shader / PSO preparation and caching;
- DX11 / DX12 renderer direction;
- regression testing between game versions;
- what parts of Prism3D are being modernized;
- what parts, if any, are being replaced.

It does not need to promise that every hitch will vanish overnight.

It does need to be more concrete than telling players to keep changing local settings while the same class of complaints continues to appear.

## What would count as an actual response

Any of the following would move this forward:

- acknowledge the measured 1.61.1.1 DX12 issue and explain what is happening;
- show that the technical conclusion is wrong and provide evidence;
- fix the cold first-use path in a future build;
- demonstrate improved async PSO coverage;
- publish a broader renderer / engine performance roadmap;
- explain what architectural work is being done to prevent recurring frametime regressions.

What does **not** answer the issue:

- another generic troubleshooting list;
- `works for me`;
- `send game.log` as a substitute for profiler evidence;
- `DX12 is experimental` as if that invalidates the measurement;
- continuing to ship paid content while never addressing the underlying engineering question.

## The point

Players are not asking SCS to adopt an external hack.

They are asking SCS to maintain the foundation of the games they continue to sell content for.

**Fix it. Modernize it. Replace the parts that need replacing. Give engine work the priority it needs. And stop treating recurring stutter reports as something the player must keep solving locally.**

## Evidence

Full investigation:
https://github.com/NemoByteCore/ets2-1.61-stutter-investigation

Community stutter tracker:
[COMMUNITY_STUTTER_TRACKER.md](COMMUNITY_STUTTER_TRACKER.md)

Accepted 1.61 runtime evidence:
[evidence/runtime/1.61/README.md](evidence/runtime/1.61/README.md)

Official SCS forum thread:
https://forum.scssoft.com/viewtopic.php?t=354183

Locked-thread permalink:
https://forum.scssoft.com/viewtopic.php?p=2163160#p2163160

Wayback snapshot:
https://web.archive.org/web/20261002223936/https://forum.scssoft.com/viewtopic.php?t=354183
