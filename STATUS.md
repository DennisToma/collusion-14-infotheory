# STATUS (top = current state; updated 2026-10-23 21:16 UTC, end of iteration 2)

**Works:** scripted market `sim/market.py` (v0.2: + realistic `shared_policy` w/ independent noise, old one = `shared_seed`);
detectors `detectors/infotheory.py` with **revised null** after codex review (pairwise offsets ≥3, CMI|state shifts
within state strata, pCMI/TE re-residualise shifted residuals, no test if <20 valid shifts); Wilson CIs.
**Gate v2 (held-out seed 7, n=50/group, `results/eval/gate_v2.json`) PASSES:** pCMI top-1 1.00 on C/D, FPR A 0.02;
BUT pCMI FPR under common shocks B = 0.16 [.08,.29] (nonlinear state×lag response) — needs fix.
shared_policy (indep. noise): pCMI 0.12–0.18 vs MI 0.30–1.00; shared_seed fools all (0.74–0.94); TE flags leader-follower 0.96.
Sweeps (`results/sweeps/power.json`, OLD null — rerun): signal detectable s≥0.1@T=100, s=0.3 needs T≈50; at T=20 run-test power 0.12
but pair top-1 0.95; tft only via TE; stay-high invisible to all.
**LLM:** gpt-6-luna anchored on the `"price": 12` JSON example → fixed (llm0.3); pilot4 shows real pair collusion (14 vs 12).
**Running:** `llm_v1` (64 games A/B/C/D×16, T=20, 4 workers, started 21:15, ETA ~23:15; log /var/tmp/c14/llm_v1.log,
resumable: rerun same command). 
**Next (priority):** (1) when llm_v1 done: `uv run python -m experiments.llm_eval label --name llm_v1` then `eval`
(check llm_eval fixes from review: agreement timing uses round>first_round+1; separate ambiguous; prefix labels);
(2) fix pCMI under common shocks: add state×lag interactions and/or **control-surrogate null** (reference
distribution from no-channel runs, = "same-model baseline null" of PLAN req. 3); (3) rerun sweeps with new null;
(4) different-model no-channel condition (Go deepseek or claude backend for 2 sellers) — req. 3;
(5) event-based detector for sticky LLM prices (co-occurrence of price changes); (6) REPORT claims review by codex + Opus.
**Risks:** codex quota/throughput; LLM games may still converge to a constant focal price (zero information).

## Log
- 20:24 smoke test ok.
- iter 1 (~20:25): built sim/market.py, detectors, experiments/scripted.py, gate dataset (no STATUS update).
- iter 2 20:28–21:16: fixed null calibration (old Bonferroni with B=100 could never reject); gate passes; sweeps
  + figures; codex built sim/llm_market.py; pilots showed gpt-6-luna stuck at 12 → wide grid, private costs,
  reasoning, hybrid mode, explore hint (none helped) → found JSON-example anchor, removed → collusion appears.
  Codex methods review (/var/tmp/c14/review_methods.md, key points in STATUS next-steps) → revised null,
  realistic shared policy, Wilson CIs, held-out gate v2. Launched llm_v1.
