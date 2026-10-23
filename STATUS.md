# STATUS (top = current state; updated 2026-10-24 00:00 UTC, iteration 7)

**Scripted half DONE (director: stop touching it).** `scripts/tables.py` reprints §4.1/§4.2 from results JSON — every cell
checked, no discrepancies (directive 5 regenerability, done early).
**E12** pre-registered level baseline (markup over state Nash) + within-family/paired AUROC in llm_eval/llm_report.
**External llm_v3 FINAL n=125 (E13):** run AUROC private vs none pCMI 0.52 [.39,.64], MI 0.59, pair_level 0.98 [.95,1];
top-1 pCMI 18/70, MI 42/70, pair_level 63/70; diff pCMI−pair_level −0.46 [−.58,−.33]; surrogate null pCMI 0/70, pair_level 45/70. In REPORT.
**E15 (exploratory):** pair co-movement on llm_v3 is real (MI on first differences top-1 31.5/70, final n), not just drift, but
max-over-pairs in controls is as high → run AUROC ≈0.5. "Localises a suspected pair, can't screen markets at T=12."
**Running:** `scripts/llm_queue2.sh` (E17: queue v1 KILLED 23:55 — backend=auto drifted to Go/deepseek for in-flight controls;
68 completed llm_v1 runs verified gpt-6-luna; queue2 pins --backend codex). llm_v1 controls → label+eval ≈00:25 → llm_long ≈01:45 → llm_mixed ≈02:15.
Before using any LLM dataset: check ground_truth model field is single-model.
**Next:** (1) when /var/tmp/c14/queue.log says 'labelled+evaluated': `uv run python -m experiments.llm_report --name llm_v1`,
fill §4.3 per DIRECTION (i)–(v); `uv run python -m experiments.llm_fig`; (2) DONE; (3) llm_long/mixed; directive-4 decision on extra batch (no launch after 04:00);
(4) 04:00+: codex/Opus claims review, abstract rewrite once, umbrella paragraph.
**Risks:** (for director/sibling) llm.py tier=cheap auto-order silently uses Go/deepseek whenever the Go cooldown lapses — sibling llm_v3fp may be affected; no pCMI positive control at T=12 (nearest scripted T=10 top-1 0.47); queue script must not be edited while running.

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
