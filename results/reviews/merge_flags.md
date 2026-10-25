# Q1.4 → merge flags (for `collusion-beyond-words` SUBMISSION.md)

Machine check: `uv run python scripts/check_merge_sources.py` (read-only, zero calls) → `results/reviews/merge_check.json`.
It checks 35 Q1.4 values in SUBMISSION against saved JSON, checks that pinned `e68_cda.json`/`e70_grid.json` SHA256 are unchanged, and reports each flag's open/applied status.
Last run: 2026-10-25 08:39 UTC on merge `02ebfd2` + working tree: **0 JSON mismatches, 0 quotes missing; F1 open, F3 open.**
Watch-list (overclaims from DIRECTION 08:23): no hits that matter. "one shared market" only occurs as "They are not one shared market" (l.86), which is correct.

| id | sev | SUBMISSION line | current text | exact replacement | REPORT § | JSON key | status |
|---|---|---|---|---|---|---|---|
| F1 | **P1** | §5.2 l.174–175 | "The null is not an estimator artefact (rank-based and discrete estimators are also at chance) and, at T = 60, not a pure power failure: observed co-move excess is …" | "Neither rank-based nor discrete estimators detect co-movement that linear pCMI missed (both at chance). At T = 60 the observed co-move excess is … — this is injection-specific sensitivity, not a general power bound." (keep the numbers that follow, which are correct) | P2.8(b), P2.8(f) | `eval/e73_nonlinear.json` → `E70`, `E44_T60`, `executed_only`; `eval/long_power_llm_long_p2_T60.json` → `mde.60.by_q.0.1`, `mde.60.observed_C_comove_excess` | open (I109) |
| F2 | P2 (optional) | abstract l.17–19 | "We detect no contemporaneous co-movement. … pCMI … is at chance in a 192-game grid …" | optionally add "(pCMI CI ∋ 0.5 in 8/9 main sets; exception base Qwen3.6 0.71 [0.51, 0.88], not replicated in the grid)". §5.2 l.178 already says this | main claim, P2.13 | `eval/claims_denominators.json`; `eval/e74_paired_diff.json` → `main_sets.llm_qb36_p2.pcmi` | open, optional |
| F3 | P2 (optional) | Table 1 l.168 | "executed agreements only (48/149) \| (inflated by construction) \| 0.42 …" | "max-pair markup 0.99 (inflated by construction); pair_level 0.87 [0.80, 0.94] (not inflated)". Appendix l.369 already says this | P2.11(c) | `eval/p2_partc.json` → `E64_pooled.all sets.pair_level.executed` | open, optional |

Rule (DIRECTION 08:23): only P1 issues get re-posted. If the merge manager rejects a flag, its status becomes "rejected" and we drop it.
