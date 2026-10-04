# Community creator resources

These files are **community-made communication resources** based on NemoByteCore's original ETS2 1.61 DX12 stutter investigation.

They are intended for journalists, YouTubers, streamers, translators and community moderators who want to explain the investigation accurately without reading the full reverse-engineering archive first.

> **Canonical source:** the repository's technical evidence and live Markdown documents remain authoritative. If any community briefing, translation, video script or PDF differs from the current repository, use the repository.

## Provenance

The English PDF and the GitHub-native Markdown resource pack were supplied on 2026-10-04 by Reddit user **GonzA321N** as a community contribution.

The resources were reviewed before publication. They preserve the important scope limits: the exact demonstrated mechanism concerns ETS2 1.61.1.1 DX12 and is not automatically generalized to DX11, ATS or every stutter report.

The live [WHAT_WE_WANT_FROM_SCS.md](../../WHAT_WE_WANT_FROM_SCS.md) is broader and may evolve after these outreach resources were written. Use that file for the current campaign position.

## Credit

The underlying technical investigation — reverse engineering, instrumentation, profiler correlation, A/B testing, measurements, evidence collection and publication of the investigation — is credited to **NemoByteCore**.

These community resources summarize and translate that work; they do not claim authorship of the investigation.

## Creator briefings

- [English creator briefing](CREATOR_BRIEFING_EN.md)
- [Guía para creadores en español](CREATOR_BRIEFING_ES.md)

## Video scripts

- [English YouTube script](YOUTUBE_SCRIPT_EN.md)
- [Guion de YouTube en español](YOUTUBE_SCRIPT_ES.md)

## Downloadable PDF

- [English creator dossier](ETS2_1.61_Stutter_Dossier_EN.pdf)

A Spanish PDF also exists as part of the contributor's outreach work, but it is not mirrored here until the actual file is archived and reviewed.

## Original investigation

Start here if you want the primary evidence rather than the outreach summary:

- [Main investigation README](../../README.md)
- [Accepted ETS2 1.61 runtime evidence](../../evidence/runtime/1.61/README.md)
- [Manifesto](../../MANIFESTO.md)
- [What we want from SCS](../../WHAT_WE_WANT_FROM_SCS.md)
- [Community stutter tracker](../../COMMUNITY_STUTTER_TRACKER.md)
- [SCS forum evidence archive](../../evidence/forum/README.md)

## Scope reminder

The documented finding concerns **Euro Truck Simulator 2 1.61.1.1 under DX12**. It demonstrates a specific engine-side stutter class involving cold graphics PSO creation on the draw path. It does **not** establish that every ETS2/ATS stutter, every renderer or every game version shares the same root cause.
