# STATUS (top = current state; updated 2026-10-24 01:10 UTC, iteration 9)

**Scripted half DONE.** llm_v1 FINAL (E18/E19) and llm_v3 ext FINAL (E13) are in REPORT §4.3. Channel raises markup by +1.8.
Level stats run AUROC 0.87/0.98; pCMI 0.45/0.52 (not distinguishable from chance); pCMI adds nothing to markup.
**iter 9:** E20 declared before eval: llm_long T-prefix analysis + directive-4 rule (extra T=50 batch iff AUROC(pCMI,50) ≥ .65
and ≥ AUROC(T=20)+.15). REPORT §4.4 umbrella synthesis with Q2.2 (premium_llm_v3.py: private +1.65 [1.38,1.93] vs +0.45 here).
Opus full-REPORT claims review (/var/tmp/c14_review_opus/review.md) applied: shared-seed 48–100%, stay-high TE flags market
but not pair, 74 games/E17 note, overlapping market ranges, legit pair_level top-1 only 6/20 (wrong pair), expanded Limitations.
**Running:** queue2 llm_long (ETA ≈01:20) → llm_mixed (≈02:00) → labels/eval.
**Next:** label+eval llm_long as soon as it lands → apply E20 rule → §4.3 (v); mixed eval → (iv); codex claims review once
codex is free (after mixed); abstract rewrite ONCE after (iv)/(v); fill E20 commit hash.
**Risks:** llm_long/mixed n=8/12 → only large effects testable.

## Log
- 20:24 smoke test ok.
- iter 1 (~20:25): built sim/market.py, detectors, experiments/scripted.py, gate dataset (no STATUS update).
- iter 2 20:28–21:16: fixed null calibration (old Bonferroni with B=100 could never reject); gate passes; sweeps
  + figures; codex built sim/llm_market.py; pilots showed gpt-6-luna stuck at 12 → wide grid, private costs,
  reasoning, hybrid mode, explore hint (none helped) → found JSON-example anchor, removed → collusion appears.
  Codex methods review (/var/tmp/c14/review_methods.md, key points in STATUS next-steps) → revised null,
  realistic shared policy, Wilson CIs, held-out gate v2. Launched llm_v1.
- iter 3 21:15–21:50: SPLITS + ledger; dev pCMI design test (inter discarded); control-surrogate null added to
  scripted + llm eval; locked test gate run; hard-negatives figure with both nulls; llm_eval: msg-timing fix,
  CD_ambiguous, dev/test groups, pair_level/market_level baselines, mixed-model analysis; sim --mixed-tier.
- iter 3 21:50–22:00: locked test sweep, Opus review + fixes, LLM analysis plan declared in REPORT §4.3, queue script.
- iter 4 21:54–22:15: queue healthy (20/64). Wrote experiments/llm_report.py (tables+figures for §4.3), verified on llm_pilot4; no llm_v1 detector peeking. Codex REPORT-claims review deferred until LLM results land.
- iter 5 21:57–22:30: E12 baseline fix + within-family/paired AUROC in llm_eval/llm_report (before llm_v1 eval); E13 ext_llm_v3 provisional; ledger hashes; §5 n fix; codex review → E14 fixes; ext rerun at n=70; experiments/llm_fig.py (figures/llm_auroc_both.png).
- iter 7 22:49–00:00: E16 mixed-eval CI; found backend drift (E17) → killed queue, queue2 with codex pinned; llm_v3 final n=125 → REPORT §4.3, figure.
- iter 6 22:34–22:52: scripts/tables.py (sonnet worker; verified), ext_llm_v3 rerun n=74 → REPORT, T=10 scripted top-1 as nearest positive control, E15 co-movement diag.
- iter 8 00:04–00:45: waited for queue2; llm_v1 label+eval done 00:26 → llm_report, llm_fig, REPORT §4.3 llm_v1 results + abstract LLM sentence (E18); ledger hashes filled; codex review of the new text started.
- iter 8 00:45–01:15: codex review of llm_v1 text (numbers all OK; P0s on inference: incremental-value untested, surrogate pool per family not pooled, 'flat vs T' false) → E19 diag_llm_v1 (incremental logistic + detrend/diff) → §4.3 + abstract rewritten accordingly.
- iter 9 01:02–01:10: E20 declared; §4.4 umbrella; Opus claims review applied (P0s + limitations).
