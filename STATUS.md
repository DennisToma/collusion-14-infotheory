# STATUS (top = current state; updated 2026-10-24 00:45 UTC, iteration 8)

**Scripted half DONE (director: stop touching it).** `scripts/tables.py` reprints §4.1/§4.2 from results JSON.
**llm_v1 FINAL (E18, 74 games, all luna/codex), in REPORT §4.3 + abstract:** channel raises markup +1.76 [1.21,2.31] (C−A),
+1.77 [1.02,2.52] (D−B), mostly market-wide (pair−rivals +0.45). Run AUROC C/D vs A/B: pCMI 0.45 [.32,.59], MI 0.50,
markup 0.87 [.78,.94], pair_level 0.74; pCMI−markup −0.42 [−.56,−.27]. Raw MI flips by family (C vs A 0.20, D vs B 0.82 =
common-trend artefact). top-1 pCMI 9/32 vs level 27/32. Shift null over-rejects on LLM A controls (0.19) → surrogate null only.
**External llm_v3 FINAL n=125 (E13):** pCMI 0.52 [.39,.64], pair_level 0.98; top-1 pCMI 18/70 vs 63/70. In REPORT.
**Running:** queue2 → llm_long (A,C T=50, 16 games, ETA ≈01:40) → llm_mixed (≈02:10) → label/eval llm_long + mixed eval
(queue.log 'queue finished'). codex review of llm_v1 text DONE (/var/tmp/c14/review_llm_v1.md, 3 P0 wording/inference, all applied);
E19 diag: LOO logistic markup+pCMI −0.025 [−.079,+.006] (no incremental value); D-vs-B MI flip = drift (diff-MI 0.51), C-vs-A partly.
**Next:** (2) when queue finished: `llm_report --name llm_long`, mixed eval → §4.3 (iv),(v);
(3) directive 4: extra T=50 batch only if llm_long pCMI grows with T, launch before 04:00, else skip; (4) 04:00+: full-REPORT
claims review (codex + Opus), abstract rewrite ONCE, umbrella paragraph with sibling test numbers (pending in their repo).
**Risks:** no pCMI positive control at T=12; llm_long may not finish before 04:00 decision if codex slows.

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
