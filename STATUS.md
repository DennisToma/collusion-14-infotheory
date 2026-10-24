# STATUS (top = current state; updated 2026-10-24 02:15 UTC, iteration 9)

**Scripted half DONE.** In REPORT: llm_v1 (E18/E19), llm_v3 ext (E13), llm_long (E20).
Level stats run AUROC 0.87/0.98/0.95; pCMI 0.45/0.52/0.45. pCMI adds nothing to markup.
**llm_long (E20) final:** T=50 does NOT rescue pCMI (0.45 [.16,.75] vs T=20 0.39; markup 0.95). Rule not met → no extra batch.
Collusion here is a stable level (markup C−A +2.28; the pair gap shrinks as rivals follow). Shift null over-rejects on A (3/8).
**E21 bug:** llm.chat(tier=big, backend=codex) silently used luna, so llm_mixed was all-luna (invalid, discarded). Fixed
llm.py and added a mixed_eval guard. **llm_mixed2 running** (scripts/llm_queue3.sh, verified sol+luna; ETA gen ≈02:35, then eval
→ queue.log 'llm_mixed2 evaluated').
**Next:** (1) mixed2 → §4.3 (iv) with CI (TE same−cross is the one to watch; treat as one of 5 detectors, unadjusted);
(2) codex claims review of full REPORT after mixed2 (codex free); (3) abstract rewrite ONCE; (4) fill ledger hashes
(E20, E20-final, E21); (5) tables.py: add llm tables? optional. Opus review already applied.
**Risks:** the per-seller `model` field is the last call's model (a sol→luna fallback mid-game would be invisible); low n.

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
