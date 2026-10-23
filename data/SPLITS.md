# Data splits (frozen 2026-10-23 21:25 UTC, iteration 3)

## Scripted market (`experiments/scripted.py --seed S`, `sim/market.py`)
- **Dev (tuning allowed):** seed0 ∈ 1–99. Used so far: 0 (gate v1), 7 (`gate_v2`, seen during iteration 2 —
  it is therefore DEV, not held-out, despite being called "held-out" in the iteration-2 log), 11 (pCMI design
  tuning, `experiments/dev_pcmi.py`), 100 (`experiments/sweep.py` default: power sweeps are descriptive curves,
  not tuned on).
- **Locked test:** seed0 = **1001** (`gate_test`, hard-negative battery, T=100, s=0.6, n=50/group) and
  seed0 = 1002 (power sweep re-run). Run ONCE with the frozen detector configuration; never used for tuning.

## LLM market (`sim/llm_market.py --name llm_v1 --seed 10`)
- Run ids `llm_v1_<cond>_<k>`. **Dev:** k ∈ 0–5 (6 per condition, 24 games). **Locked test:** k ∈ 6–15
  (10 per condition, 40 games). Detector/label choices for LLM data (event-based detector, tacit threshold,
  judge prompt) may be tuned on dev only; headline LLM numbers are computed on test (and also reported on all
  64 games for transparency, labelled as such).
