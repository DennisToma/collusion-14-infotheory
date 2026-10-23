# Opus subagent adversarial review, iteration 3 (2026-10-23 ~21:55 UTC) — condensed, with actions

1. Surrogate null: LOO makes control FPR ≤ α by construction → don't present A/B surrogate rates as calibration
   evidence (abstract + E08 wording). Under the scripted surrogate null, hard-negative rows test "looks like a
   QBR market after residualisation", not a same-policy null → call them false-accusation rate vs QBR reference.
   Reference family is picked from ground-truth condition; legitimate only because shocks are public (could pick from S).
   No tuning leakage; pool is transductive within dataset. → ACTION: reworded abstract/§3/§4.1, ledger note.
2. BUG llm_eval surrogate: 16 controls/family → min p = 1/17 > 0.05 → surrogate flags identically 0 on llm_v1.
   → ACTION: report run-level AUROC with bootstrap CI (≡ mean surrogate rank) instead; flags only if pool ≥ 20.
   mixed_eval treats 6 pairs/run as independent and compares raw scores across tiers with different variance
   → ACTION: per-run (mean same − mean cross) + sign test across runs; count near-constant sellers.
   Shift null at T=20 is coarse (~14 distinct offsets). Minor: offsets mod T−1 applied to length-T prices;
   _strat_roll can give 0 relative offset in small strata (conservative); Nash markup ignores private cost noise.
3. LLM headline: label rates w/ Wilson CIs; price-level effect of channel (Mann-Whitney + bootstrap); run-level
   AUROC [CI] of pCMI / market_level / pair_level; pCMI top-1 vs 1/6 (exact binomial). Don't claim surrogate
   FPR/power on LLM, "no same-model dependence" from null, "pCMI fails on LLMs" in general.
   Split: nothing tuned on LLM data → declare all-64 confirmatory (frozen from scripted), test-only as robustness.
   → ACTION: SPLITS.md updated before any detector output on llm_v1 was viewed.
4. Experiments: (a) long-horizon LLM run (A and C, T=50, ~8 each) + more A games (pool > 20);
   (b) scripted twin of observed LLM behaviour: pair holds a level, rivals follow pair's lagged price.
