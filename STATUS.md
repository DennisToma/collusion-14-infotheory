# STATUS (top = current state; updated 2026-10-24 03:12 UTC, iteration 11)

**All declared analyses DONE** (§4.3 (i)–(v) filled). Scripted half done; LLM: llm_v1 (E18/E19), llm_v3 ext (E13), llm_long (E20), llm_mixed2 (E22).
Level stats run AUROC 0.87/0.98/0.95; pCMI 0.45/0.52/0.45. pCMI adds nothing to markup. T=50 does not rescue pCMI (declared rule not met; CI wide).
**llm_mixed2 (E22):** 12 games, 2 sol + 2 luna each, all pass model check. Same − cross per run: pCMI +0.003 [−0.025, +0.032];
TE +0.047 [+0.002, +0.104] (1 of 5 detectors, unadjusted, sign p=.15 → weak at most). No detectable same-model excess; n=12 excludes only large effects.
**E23:** codex claims review applied (no table-number errors; fixed shared-seed 44–100%, legit top-1 5/20, CMI|state 0.64 on llm_v3 disclosed,
softened "invisible/never/rescue/causal" wording, stale m=16). Review text: results/reviews/codex_claims_review_iter10.md. **E24:** Opus coherence review applied (order (iv)→(v), §6 repro fixed, abstract attributions).
**E25 (iter 11):** full number audit (sonnet worker): 0 mismatches; dropped 1 untraceable claim, added scripts/market_mean_ranges.py; mixed2 forest figure added; table lint OK.
**Next:** abstract frozen (do not rewrite). No new LLM batch (E20 rule not met). Remaining: optional final codex read of REPORT
for clarity only; re-run tables.py once in finalize (08:15) and push. §4.3.1 pilot descriptives have no results file (ledger E04/E05 only) — acceptable, labelled descriptive.
**Risks:** low n everywhere on LLM; only OpenAI-family sellers (cross-family Claude sellers not run, quota cost).

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
- iter 9 01:10–02:15: llm_long label+eval (I accidentally pkilled the queue's eval and reran it) → E20 final in §4.3 (v); found E21 mixed-tier bug, fixed, llm_mixed2 launched.
- iter 10 02:17–02:26: llm_mixed2 finished + evaluated → §4.3 (iv), abstract sentence; scripts/mixed_price_by_model.py; codex claims review → E23 edits.
- iter 10 02:26–02:29: tables.py mixed(); Opus coherence review → E24 edits.
- iter 10 02:29: §4.3 restructured into subsections (no number changes).
- iter 11 02:58–03:12: figures/llm_mixed2_same_vs_cross.png (scripts/mixed_fig.py) → §4.3.5 + §6; table lint OK; no new LLM batch (directive 4); E25 number audit + fixes.
