# STATUS (top = current state; updated 2026-10-23 22:00 UTC, end of iteration 3)

**Works:** scripted market + detectors; **two nulls**: within-run shift null and **control-surrogate null**
(rank max-pair score vs no-channel control markets; = "same-model baseline null"). Splits frozen in `data/SPLITS.md`
(scripted dev seeds 1–99 incl. old gate_v2=7; locked test 1001/1002; llm_v1 k≤5 dev, k≥6 test). Ledger `EXPERIMENTS.tsv`.
**Locked test gate (`results/eval/gate_test.json`, seed 1001):** pCMI surrogate FPR 0.04 [.01,.13] on common shock,
shared policy (A & B), leader-follower; shift-null pCMI B 0.14; shared_seed unremovable (0.48–0.94); C/D 1.00, top-1 1.00.
Dev: state×lag interactions don't help (E07, discarded).
**Locked test sweep (`results/sweeps/power_test.json`, seed 1002):** signal pCMI 0.97 at s=0.1/T=100, 0.80 at T=20 (ctrl 0.05);
tft only TE (≥0.97 at s≥0.45); stay-high invisible. REPORT §4.1/§4.2 + figures updated to test numbers.
**Opus review** (`results/reviews/opus_review_iter3.md`) → fixed: LOO-surrogate wording, llm surrogate pool bug (16 → min p
1/17; now flags only if pool ≥ 20, AUROC+bootstrap CI otherwise), mixed_eval per-run sign test, all-64 confirmatory LLM split.
**Running:** `scripts/llm_queue.sh` (pid via `pgrep -f llm_queue`; progress /var/tmp/c14/queue.log): waits for llm_v1
(18/64 at 21:52, ETA ~23:30) → +5 A & +5 B controls → `llm_eval label/eval llm_v1` → llm_long (A,C ×8, T=50)
→ llm_mixed (A ×12, 2 luna + 2 sol) → label/eval/mixed. If killed: rerun the script (all steps resumable/cached).
**Next:** (1) read /var/tmp/c14/llm_v1_eval.log + results/eval/llm_v1.json, fill REPORT §4.3 per declared plan
(label rates, price-level effect, AUROC pCMI vs market_level/pair_level, top-1 binomial, power vs T);
(2) LLM figure (price trajectories C vs A; AUROC bars); (3) llm_long/mixed results; (4) codex review of REPORT claims;
(5) optional: scripted "level + followers" twin (≈ fixed_high already).
**Risks:** LLM C/D pair-specific signal may be weak at T=20; surrogate null needs matched reference markets.

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
