# ETS2 1.61 runtime evidence archive

This directory collects the accepted historical measurements behind the final DX12 PSO finding.

The main README gives the short conclusion. These files preserve the evidence ladder, controlled experiments and negative results that led to it without publishing private handoffs, machine-specific workflow or local filesystem paths.

## Evidence

- [Exact frame/RG correlation — v82](v82-exact-rg/SUMMARY.md)
- [Localization ladder: RG -> post-T1 -> DX12 +0x108 -> AAA60](localization-ladder.md)
- [Controlled wait=1 -> wait=0 A/B](wait-flag-ab.md)
- [Cold-key and prewarm negative results](pso-prewarm-negative-results.md)
- [Built-in async preparation coverage — v0.14](async-coverage-v014.md)

The deterministic v82 analyzer is already public at [tools/analysis_161/analyze_exact_v82.py](../../../tools/analysis_161/analyze_exact_v82.py).

For the earlier investigation that established the measurement discipline and ruled down many attractive hypotheses, see the [historical ETS2 1.60 archive](../../../legacy/1.60/README.md).

## Scope

The exact cold-PSO / missing-async-coverage mechanism is proven for the investigated ETS2 1.61.1.1 DX12 build.

The evidence here must not be read as proof that the identical mechanism was established on DX11 or on the historical 1.60 build.
