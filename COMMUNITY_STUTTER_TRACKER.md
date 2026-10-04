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

Reddit:
https://www.reddit.com/r/trucksim/comments/1utiq3r/constant_stuttering_every_couple_of_seconds_in/

Official SCS forum version of the same case:
https://forum.scssoft.com/viewtopic.php?p=2148906

Why it is relevant:
- reports a strong version-to-version difference;
- the official forum post identifies an i7-14700K, RTX 4080 SUPER, 32 GB DDR5 system;
- the author reports that 1.58 works smoothly while 1.59 and 1.60 stutter badly;
- the author describes extensive troubleshooting: clean reinstall, no mods, new profile, Windows reinstall, BIOS changes, DDU / different GPU drivers, offline mode, FPS limiting and configuration changes;
- a later post says the 1.61 beta showed the same stuttering;
- another participant with an i7-14700K and RTX 4070 Ti Super reports stutter in both ETS2 and ATS;
- aligns with the existence of measurable 1.58 -> 1.60 render-side regressions documented in the historical archive.

Status:
- the Reddit and SCS forum links appear to describe the same primary report and are therefore treated as one case, not two independent reports;
- public report only;
- the exact 1.61 cold-PSO mechanism must not be retroactively assigned to this 1.59/1.60 case.

### ATS and ETS 2 stutters problem

https://www.reddit.com/r/trucksim/comments/1vfx4ds/ats_and_ets_2_stutters_problem/

Why it is relevant:
- reports stutter in both SCS truck simulators;
- indicates that users may experience hitching despite clean installs / troubleshooting.

Status:
- public report only;
- the accepted cold-PSO result in this repository was proven on ETS2 1.61.1.1 DX12, not ATS.

### Micro-stuttering in ETS 2, starting from versions 1.59–1.61, regardless of PC performance

https://forum.scssoft.com/viewtopic.php?p=2159985

Why it is relevant:
- official SCS forum report dated 17 September 2026;
- author reports i9-13900KS, RTX 3060 Ti, 32 GB RAM and SSD;
- version 1.58 is reported as smooth at Ultra settings;
- versions 1.59, 1.60 and 1.61 are all reported to show micro-stuttering;
- lowering graphics settings to minimum did not remove the symptom;
- the author later reports that suggested refresh-rate / averaging changes, HAGS changes and disabling overlays did not solve it;
- the author explicitly states that the current client is being used without modifications;
- another participant in the same thread reports a separate 1.58-smooth / 1.61-stuttering experience on an i5-14600K / RX 9070 XT system.

Status:
- public report only;
- the thread contains multiple user experiences and later troubleshooting developments, so individual outcomes should not be collapsed into one root-cause claim;
- not proven to be the same 1.61 DX12 cold-PSO mechanism.

### Stuttering since 1.59-60

https://forum.scssoft.com/viewtopic.php?t=352303

Why it is relevant:
- official SCS forum report dated 29 June 2026;
- author reports stuttering beginning with version 1.59 in both ETS2 and ATS while 1.58 and earlier were fine;
- symptom is reported during driving and camera changes;
- the author tested V-Sync, FPS limiting and modded versus vanilla profiles without changing the behavior;
- the author checked the game log and did not identify an obvious explanation there.

Status:
- public report only;
- because the report covers both ETS2 and ATS, it is useful evidence of a recurring symptom pattern but not proof of a shared engine mechanism;
- the exact 1.61 DX12 cold-PSO result in this repository was not proven on ATS.

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
