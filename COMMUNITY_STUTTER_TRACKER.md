# Community Stutter Tracker

This file collects public reports of ETS2 / ATS stutter, hitching, frametime spikes and version-to-version smoothness regressions.

Its purpose is **not** to claim that every report below has the same root cause as the cold-PSO / async-coverage issue proven in ETS2 1.61.1.1 DX12.

The exact mechanism documented in this repository is build- and renderer-specific evidence. Community reports are listed here to show that stutter complaints recur across users, hardware and game versions, and to make future comparison easier.

## Confirmed technical reference point

The accepted 1.61 investigation in this repository proved one specific stutter class on:

- ETS2 1.61.1.1
- revision `6949e633e77902f7e023819d3131cc6ccce3707f`
- DX12
- EXE SHA-256 `EB17944139BE4DE3D70D0CD57CDAA7C52C9E326ECF2D0DD3EA2F806545C74A53`

Relevant path:

```text
FUN_1402A06D0
-> FUN_1402AAA60
-> FUN_14029DD00(..., wait=1)
```

Built-in async preparation path:

```text
FUN_14029E0F0
-> FUN_14029DD00(..., wait=0)
```

Final coverage result:

```text
async_total = 0
slow_total  = 27
slow_seen   = 0
slow_unseen = 27
```

That is the technical baseline. Entries below are **community reports**, not automatic confirmations of the same mechanism.

## Public community reports

### Best ETS2 version for smoothness and no stuttering?

https://www.reddit.com/r/trucksim/comments/1waz3lt/best_ets2_version_for_smoothness_and_no_stuttering/

Why it is relevant:
- asks directly whether newer ETS2 versions introduced microstutter;
- compares the smoothness of older and newer builds;
- useful for version-regression discussion.

Status:
- public report only;
- not proven to be the same 1.61 DX12 cold-PSO mechanism.

### I may have found a temporary fix for the traversal stuttering

https://www.reddit.com/r/trucksim/comments/1t04eya/i_may_have_found_a_temporary_fix_for_the/

Why it is relevant:
- reports traversal-style stutter;
- discusses DX12 behaving better than DX11;
- useful context for comparing renderer behavior.

Status:
- public report only;
- not proven to be the same root cause.

### ETS2 microstutter / sliding frametime — maybe shader cache?

https://www.reddit.com/r/trucksim/comments/1svhh93/ets2_microstutter_sliding_frametime_maybe_shader/

Why it is relevant:
- specifically suspects shader/cache behavior;
- describes frametime instability rather than only low average FPS;
- useful context for the later confirmed 1.61 PSO investigation.

Status:
- public report only;
- shader/cache suspicion does not by itself prove the mechanism documented here.

### Constant stuttering every couple of seconds in ETS2 1.60 / 1.58 works fine

https://www.reddit.com/r/trucksim/comments/1utiq3r/constant_stuttering_every_couple_of_seconds_in/

Why it is relevant:
- reports a strong version-to-version difference;
- aligns with the existence of measurable 1.58 -> 1.60 render-side regressions documented in the historical archive.

Status:
- public report only;
- the exact 1.61 cold-PSO mechanism must not be retroactively assigned to this 1.60 case.

### ATS and ETS 2 stutters problem

https://www.reddit.com/r/trucksim/comments/1vfx4ds/ats_and_ets_2_stutters_problem/

Why it is relevant:
- reports stutter in both SCS truck simulators;
- indicates that users may experience hitching despite clean installs / troubleshooting.

Status:
- public report only;
- the accepted cold-PSO result in this repository was proven on ETS2 1.61.1.1 DX12, not ATS.

### HELP HOW DO I FIX THESE MICRO STUTTERS

https://www.reddit.com/r/trucksim/comments/1skujs7/help_how_do_i_fix_these_micro_stutters/

Why it is relevant:
- direct player report of recurring microstutter;
- useful as another public example of the symptom players are trying to solve through local tweaks.

Status:
- public report only;
- no root-cause equivalence is claimed.

## How to add a report

A useful entry should include as much of the following as the original author actually supplied:

- public URL;
- ETS2 or ATS;
- game version;
- DX11 / DX12 if known;
- hardware if known;
- vanilla / modded if known;
- symptom description;
- whether an older/newer version behaves differently;
- troubleshooting already attempted.

Do not invent missing fields.

Do not classify a report as the confirmed 1.61 cold-PSO issue unless it has evidence sufficient to support that conclusion.

## What this tracker can and cannot establish

This tracker can establish that public reports of stutter and frametime problems recur and can help identify patterns worth reproducing.

It cannot, by itself, establish:
- that every report has one common root cause;
- that the exact 1.61 DX12 mechanism is present on DX11;
- that ATS uses the identical failing path;
- that every historical ETS2 version has the same bug.

For the accepted technical evidence, use:

- [1.61 runtime evidence](evidence/runtime/1.61/README.md)
- [historical 1.60 archive](legacy/1.60/README.md)
