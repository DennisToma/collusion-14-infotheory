# Data splits (frozen 2026-10-23 21:25 UTC, iteration 3)

## Scripted market (`experiments/scripted.py --seed S`, `sim/market.py`)
- **Dev (tuning allowed):** seed0 ∈ 1–99. Used so far: 0 (gate v1), 7 (`gate_v2`, seen during iteration 2 —
  it is therefore DEV, not held-out, despite being called "held-out" in the iteration-2 log), 11 (pCMI design
  tuning, `experiments/dev_pcmi.py`), 100 (`experiments/sweep.py` default: power sweeps are descriptive curves,
  not tuned on).
- **Locked test:** seed0 = **1001** (`gate_test`, hard-negative battery, T=100, s=0.6, n=50/group) and
  seed0 = 1002 (power sweep re-run). Run ONCE with the frozen detector configuration; never used for tuning.

## LLM market (`sim/llm_market.py --name llm_v1 --seed 10`)
**Revised 2026-10-23 22:00 UTC, before any detector output on llm_v1 was computed** (after Opus review): no
detector setting is tuned on LLM data — all settings are frozen from the scripted work — so **all 74 games (64 planned + 10 extra A/B controls added 23:53 before any detector output, E17)
are the confirmatory set**; the k ≥ 6 subset is reported as a robustness check. The original plan was:
- Run ids `llm_v1_<cond>_<k>`. **Dev:** k ∈ 0–5 (6 per condition, 24 games). **Locked test:** k ∈ 6–15
  (10 per condition, 40 games). Detector/label choices for LLM data (event-based detector, tacit threshold,
  judge prompt) may be tuned on dev only; headline LLM numbers are computed on test (and also reported on all
  64 games for transparency, labelled as such).

## Phase 2 LLM datasets (declared 2026-10-24 06:33 UTC, before generation; E43–E45; amended 06:35 before any result)
No detector setting is tuned on these datasets: all detectors use the frozen v1 configuration, so **every game is
confirmatory** (no dev split needed). `llm_p2_<variant>` (seed 43, A/C, n=6, T=20 — amended from 8 before any result; variants v0/para/template/order/noreason),
`llm_long_p2` (seed 50, A/C, n=20, T=60 — amended from 80 before any result), `llm_ds_p2` (deepseek-v4.1-flash via Go, thinking disabled, seed 10, A/C, n=15, T=20).
If a later analysis needs tuning, it must use a new seed range declared here first.
