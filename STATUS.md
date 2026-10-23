# STATUS (top = current state; updated 2026-10-23 22:25 UTC, iteration 5)

**Scripted half DONE (director: stop touching it).** Locked gate (seed 1001) + locked sweep (1002) in REPORT §4.1/4.2.
**E12 (pre-registered before llm_v1 eval):** `market_level` = pair markup over per-round state Nash (raw kept as
`market_level_raw`); within-family AUROC (C vs A, D vs B); paired-bootstrap AUROC(IT) − AUROC(level) (`auroc_diff`);
within-family markup premium in `price_level`. `llm_report` prints all of these. Tested on llm_pilot4.
**E13/E14 external set (sibling llm_v3, PROVISIONAL n=70/125):** `experiments/ext_llm_v3.py` → `results/eval/llm_v3_ext.json`
(per-pair rows for 22) + `llm_v3_ext_report.md` (table pasted in REPORT). Run AUROC private vs none: pCMI 0.53 [.35,.72],
pair_level 0.98 [.94,1], markup 0.93; top-1 pCMI 11/42 vs pair_level 40/42; diff −0.45 [−.63,−.26]. MI/Pearson localise
within-run above chance (25/42) but don't separate runs. Codex review (results/reviews/codex_review_iter5.md) fixed:
price-selected label leak, global monkeypatch, tie-breaking (also llm_eval), exploratory p-values. → "LLM collusion = pair-specific level; dependence detectors remove levels". In REPORT §4.3.
**Running:** `scripts/llm_queue.sh` (llm_v1 30/64 at 22:15 → main ETA ~23:30, +controls ~00:00 → label+eval →
llm_long → llm_mixed ~02:00). Codex review of E12/E13 code → results/reviews/codex_review_iter5.md.
**Next:** (1) after sibling finishes (~00:15; 125 lines in their ground_truth.jsonl) rerun `uv run python -m experiments.ext_llm_v3`,
update §4.3 table (surrogate null becomes available when none ≥ 20); (2) when queue.log says 'labelled+evaluated':
`uv run python -m experiments.llm_report --name llm_v1`, fill §4.3 per plan (i)–(v) of DIRECTION; (3) llm_long/mixed;
(4) rerun `uv run python -m experiments.llm_fig` after llm_v1 eval (figure exists, llm_v3 panel only); (5) 04:00+: scripts/tables.py, claims review, umbrella paragraph.
**Risks:** ext pCMI at T=12 has no positive control at that length (scripted power known only down to T=20);
queue script must not be edited while running (bash reads it incrementally).

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
