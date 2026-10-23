# STATUS (top = current state; updated 2026-10-23 23:33 UTC, iteration 7)

**Scripted half DONE (director: stop touching it).** `scripts/tables.py` reprints §4.1/§4.2 from results JSON — every cell
checked, no discrepancies (directive 5 regenerability, done early).
**E12** pre-registered level baseline (markup over state Nash) + within-family/paired AUROC in llm_eval/llm_report.
**External llm_v3 (PROVISIONAL n=74/125):** run AUROC private vs none pCMI 0.52 [.32,.70], MI 0.56, pair_level 0.98 [.94,1];
top-1 pCMI 11/45, MI 27/45, pair_level 42/45; diff pCMI−pair_level −0.46 [−.65,−.29]. Agreement label now 45/45
(earlier 37/42 because sibling labels.jsonl lagged; missing label counted as no agreement — fine once labels complete).
**E15 (exploratory):** pair co-movement on llm_v3 is real (MI on first differences top-1 21.5/49), not just drift, but
max-over-pairs in controls is as high → run AUROC ≈0.5. "Localises a suspected pair, can't screen markets at T=12."
**Running:** `scripts/llm_queue.sh`: llm_v1 main done 23:15, controls 68/74 at 23:32 → label+eval ≈23:55 → llm_long
(~01:10) → llm_mixed (~01:50). Sibling llm_v3 85/125 at 22:52. E16: mixed eval now gives bootstrap CI (declared pre-data).
**Next:** (1) when /var/tmp/c14/queue.log says 'labelled+evaluated': `uv run python -m experiments.llm_report --name llm_v1`,
fill §4.3 per DIRECTION (i)–(v); `uv run python -m experiments.llm_fig`; (2) after sibling hits 125: rerun ext_llm_v3 +
diag_llm_v3, update §4.3 (surrogate null if none ≥ 20); (3) llm_long/mixed; directive-4 decision on extra batch (no launch after 04:00);
(4) 04:00+: codex/Opus claims review, abstract rewrite once, umbrella paragraph.
**Risks:** no pCMI positive control at T=12 (nearest scripted T=10 top-1 0.47); queue script must not be edited while running.

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
- iter 7 22:49–: E16 mixed-eval CI (tested on synthetic relabelled pilot copy); waited on queue for llm_v1 eval.
- iter 6 22:34–22:52: scripts/tables.py (sonnet worker; verified), ext_llm_v3 rerun n=74 → REPORT, T=10 scripted top-1 as nearest positive control, E15 co-movement diag.
