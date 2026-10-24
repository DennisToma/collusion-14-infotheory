codex
Read-only review; no analysis executed. **No P0 findings.**

- **P1 — AUROC measures an average over ten plantings, not single-game detection.** [Script:73](/home/factory/collusion/collusion-14-infotheory/scripts/injection_mde.py:73) averages max-pair scores before computing AUROC. At T=50, q=0.1/0.2, the reported **0.81/0.95** compare with single-planting pooled AUROCs **0.76/0.93** (`auroc_all_reps`). Top-1 instead uses individual plantings. Fix: report single-planting AUROC with game-cluster uncertainty, or replace the table caption’s opening with:
  > “Cells report AUROC comparing each control game’s mean max-pair pCMI across ten independent plantings with its unplanted score; this is not single-planting run AUROC.”

- **P1 — Bootstrap breaks the shared-game pairing.** [Script:74](/home/factory/collusion/collusion-14-infotheory/scripts/injection_mde.py:74) calls [auroc_ci:143](/home/factory/collusion/collusion-14-infotheory/experiments/llm_eval.py:143), which resamples positives and negatives independently. Both derive from the same control games. Fix: resample game indices jointly, retaining each original score and its plantings. The AUROC point estimate need not change; the current CIs do not preserve the sampling dependence. Until corrected, replace “CI by bootstrap over games” with:
  > “Reported CIs independently bootstrap planted game means and unplanted scores, without preserving their shared-game pairing.”

- **P1 — The causal explanation is overclaimed.** [REPORT:440–444](/home/factory/collusion/collusion-14-infotheory/REPORT.md:440) cannot establish that insufficient T is secondary. AUROC is discrimination, not calibrated detection power; co-movement excess neither determines pCMI nor captures market-wide coordination, which rival subtraction can cancel. Control-background injections also need not represent coordination on channel backgrounds.

  Replace the **entire “Reading” paragraph** with:
  > “Reading: at T=50, these control-background injections yield substantial pCMI discrimination and localisation for the specified shared-offset alternative. The observed channel pairs have no statistically detected mean excess of contemporaneous same-direction price changes relative to rival pairs, and their upper confidence bounds lie below the mean excesses of the q=0.1 plantings. This demonstrates sensitivity to one planted alternative; it does not establish why the real-channel pCMI comparison is null, rule out low power for other alternatives, or distinguish a level effect from other coordinated variation.”

  Replace the **new abstract sentence** with:
  > “An exploratory injection check (§4.3.8) shows pCMI sensitivity to shared price offsets on T=50 control games; channel pairs have no statistically detected mean co-movement excess relative to rivals, but the explanation for the pCMI null remains unresolved.”

  Replace the **line-411 parenthetical** with:
  > “(low power remains possible; §4.3.8 demonstrates sensitivity only to a specific shared-offset alternative)”

- **P2 — “Moves in 20% of rounds” misdescribes the injection.** [Script:62–65](/home/factory/collusion/collusion-14-infotheory/scripts/injection_mde.py:62) adds **price-level offsets**; injected first differences are `Δz_t`, not `z_t`. Replace the planting description with:
  > “For each planting, we choose a random pair and add the same independently drawn price-level offset z_t ∈ {−1,0,+1} to both sellers each round, with probability q/2 for each nonzero value.”

  Replace the co-movement definition with:
  > “Co-movement is the fraction of the T−1 transitions with Δp_iΔp_j>0; unchanged prices count as non-co-movement. Excess subtracts the mean over the other five pairs.”

  **Observed-side alignment is correct:** assigned IDs are mapped to columns and sorted; both sides use the same statistic and T-round prefix.

- **P2 — One numerical transcription error.** [REPORT:432](/home/factory/collusion/collusion-14-infotheory/REPORT.md:432): `llm_v1 A`, q=0.1 excess is **0.104862…**, so **(+0.11) → (+0.10)**. All other reported numbers in the scoped section match the JSON to displayed precision.
tokens used
30,088
Read-only review; no analysis executed. **No P0 findings.**

- **P1 — AUROC measures an average over ten plantings, not single-game detection.** [Script:73](/home/factory/collusion/collusion-14-infotheory/scripts/injection_mde.py:73) averages max-pair scores before computing AUROC. At T=50, q=0.1/0.2, the reported **0.81/0.95** compare with single-planting pooled AUROCs **0.76/0.93** (`auroc_all_reps`). Top-1 instead uses individual plantings. Fix: report single-planting AUROC with game-cluster uncertainty, or replace the table caption’s opening with:
  > “Cells report AUROC comparing each control game’s mean max-pair pCMI across ten independent plantings with its unplanted score; this is not single-planting run AUROC.”

- **P1 — Bootstrap breaks the shared-game pairing.** [Script:74](/home/factory/collusion/collusion-14-infotheory/scripts/injection_mde.py:74) calls [auroc_ci:143](/home/factory/collusion/collusion-14-infotheory/experiments/llm_eval.py:143), which resamples positives and negatives independently. Both derive from the same control games. Fix: resample game indices jointly, retaining each original score and its plantings. The AUROC point estimate need not change; the current CIs do not preserve the sampling dependence. Until corrected, replace “CI by bootstrap over games” with:
  > “Reported CIs independently bootstrap planted game means and unplanted scores, without preserving their shared-game pairing.”

- **P1 — The causal explanation is overclaimed.** [REPORT:440–444](/home/factory/collusion/collusion-14-infotheory/REPORT.md:440) cannot establish that insufficient T is secondary. AUROC is discrimination, not calibrated detection power; co-movement excess neither determines pCMI nor captures market-wide coordination, which rival subtraction can cancel. Control-background injections also need not represent coordination on channel backgrounds.

  Replace the **entire “Reading” paragraph** with:
  > “Reading: at T=50, these control-background injections yield substantial pCMI discrimination and localisation for the specified shared-offset alternative. The observed channel pairs have no statistically detected mean excess of contemporaneous same-direction price changes relative to rival pairs, and their upper confidence bounds lie below the mean excesses of the q=0.1 plantings. This demonstrates sensitivity to one planted alternative; it does not establish why the real-channel pCMI comparison is null, rule out low power for other alternatives, or distinguish a level effect from other coordinated variation.”

  Replace the **new abstract sentence** with:
  > “An exploratory injection check (§4.3.8) shows pCMI sensitivity to shared price offsets on T=50 control games; channel pairs have no statistically detected mean co-movement excess relative to rivals, but the explanation for the pCMI null remains unresolved.”

  Replace the **line-411 parenthetical** with:
  > “(low power remains possible; §4.3.8 demonstrates sensitivity only to a specific shared-offset alternative)”

- **P2 — “Moves in 20% of rounds” misdescribes the injection.** [Script:62–65](/home/factory/collusion/collusion-14-infotheory/scripts/injection_mde.py:62) adds **price-level offsets**; injected first differences are `Δz_t`, not `z_t`. Replace the planting description with:
  > “For each planting, we choose a random pair and add the same independently drawn price-level offset z_t ∈ {−1,0,+1} to both sellers each round, with probability q/2 for each nonzero value.”

  Replace the co-movement definition with:
  > “Co-movement is the fraction of the T−1 transitions with Δp_iΔp_j>0; unchanged prices count as non-co-movement. Excess subtracts the mean over the other five pairs.”

  **Observed-side alignment is correct:** assigned IDs are mapped to columns and sorted; both sides use the same statistic and T-round prefix.

- **P2 — One numerical transcription error.** [REPORT:432](/home/factory/collusion/collusion-14-infotheory/REPORT.md:432): `llm_v1 A`, q=0.1 excess is **0.104862…**, so **(+0.11) → (+0.10)**. All other reported numbers in the scoped section match the JSON to displayed precision.

[exited with code 0]
