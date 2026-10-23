# STATUS (top = current state; updated 2026-10-23 ~20:40 UTC, iteration 2)

**Works:** scripted market `sim/market.py`; detectors `detectors/infotheory.py` (Pearson, MI-MM, CMI|state,
pCMI|state+lags, TE, net influence) with a calibrated **max-over-pairs circular-shift null** (iteration-1
Bonferroni with B=100 could never reject — fixed). LLM market `sim/llm_market.py` (codex-built, reviewed;
public board OFF by default — with it on, all 4 sellers publicly coordinate on 12, killing the C-vs-A contrast).
`experiments/llm_eval.py` (judge labels + detectors + power vs T) written, untested on real data.
**Gate PASSES** (`results/eval/gate_s06_T100.json`): pCMI & CMI|state top-1 = 1.00 on C/D; FPR A 0.04/0.00, B 0.08/0.00.
**Key numbers:** raw MI/Pearson flag 100% of common-shock runs; shared policy flagged 72–88% by all
contemporaneous detectors (unsolved); TE flags legit leader-follower 100%, indep-high-price 52%.
Sweep so far: `signal` detected at s≥0.1 (T=100); `tft` and `fixed_high` ≈ undetectable by pCMI (lag-conditioned
/ no shared variation) — expected, explain in REPORT.
**Running:** `experiments.sweep` → results/sweeps/power.json; LLM pilot `llm_pilot` (C,D ×3, T=20).
**Next:** (1) plot sweeps, check TE on tft; (2) read pilot private chats → if coordination happens, launch
`llm_v1` (≥60 games: A10/B20/C10/D20 or similar, T=20) with `--workers 3`; (3) label with judge, eval;
(4) shared-policy fix: same-model surrogate null from no-channel runs; (5) transfer: run detectors on sibling's
LLM data (`~/collusion/collusion-22-say-vs-do/data/llm_v2`, read-only); (6) codex adversarial review of methods.
**Risks:** LLM throughput (codex ~4 s/call, CPU contention with sibling); constant-price LLM play ⇒ zero MI
(info-theory sees coordinated *variation* only) — use common-shock conditions for variation.

## Log
- 20:24 smoke test ok.
- iter 1 (~20:25): built sim/market.py, detectors, experiments/scripted.py, gate dataset (no STATUS update).
- iter 2 20:28–: fixed null calibration (max-stat joint shift, B=200); gate passes; hard-negative figure;
  sweep script; codex implemented sim/llm_market.py (dry-tested), added --public flag; smoke game showed
  pair agreeing privately on 12 and all sellers publicly converging on 12; pilot launched; REPORT draft.
