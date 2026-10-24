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
`llm_long_p2` (seed 50, A/C, n=20, T=60 — amended from 80 before any result), `llm_ds_p2` (deepseek-v4.1-flash via Go, thinking disabled, seed 10, A/C, n=15, T=20). `llm_ds_p2pub` (E59: deepseek, condition A + public board, seed 10 = same seeds as `llm_ds_p2` A, n=15, T=20; confirmatory/exploratory, no tuning).
If a later analysis needs tuning, it must use a new seed range declared here first.

## Phase 2 scripted gaps 5/6/8 (declared 2026-10-24 07:03 UTC, after dev runs, before any test run; E49–E51)
`experiments/p2_scripted.py` (coalition / onset / costasym; T=100, s=0.6 signal, n=30 per group, B=100). **Dev:** seed0 200 / 210 / 220
(results/p2/*_dev.json, written by codex; no setting tuned on them; the CUSUM threshold h=14.5 is set from the 30 dev controls).
**Locked test:** seed0 2001 (coalition), 2002 (onset), 2003 (costasym), run once with `--test` and the frozen configuration
(onset: h frozen from dev, so the test control alarm rate is an out-of-sample FPR).

## Phase 2 gap 7 market robustness (declared 2026-10-24 07:10 UTC, before the dev run; E52)
`experiments/p2_market.py` (N=2/4/6, mu 1.5/3/4.5; T=100, n=30 per group, B=100). **Dev:** seed0 230. **Locked test:** seed0 2004,
run once with `--test` and the configuration frozen after dev (no detector setting is tunable here; dev only checks the script).

## Phase 2 gap 9 bid rotation (declared 07:29 UTC, before the dev run; E53, exploration)
`experiments/p2_rotation.py` (base market; T=100 + T30 prefix; n=30 per group; B=100). **Dev:** seed0 240. **Locked test:** seed0 2005, run once with `--test`.

## Phase 2 part C (declared 2026-10-24T11:01 UTC, before generation; E61–E63)
No detector setting is tuned: all are frozen, so every game in E61/E62 is **confirmatory**. `llm_qa_p2` (qwen-abliterated, Modal) and `llm_qb_p2` (qwen-base),
`llm_g56l_p2` (gpt-5.6-luna, codex), `llm_glm_p2` (glm-5.2, Go): all seed 10 (same pairs/costs as llm_v1 and llm_ds_p2), A/C, T=20.
E63 strong-lever **pilots** `llm_strong_*_pilot` (seed 61, T=40) are dev only — used to choose the lever set; a promoted full arm gets a new seed declared here first.

## Phase 2 part C promoted arm (declared 2026-10-24T13:38 UTC, before generation; E65)
`llm_strong_qa` = qwen-abliterated (Modal), `--memory`, T=40, **seed 65** (new; pilot used 61), A and C n=20 each. Promoted because the E63 pilot
`llm_strong_qa_pilot` executed 5/5 C games (judge labels only; no detector was run on the pilot). All games confirmatory (detectors frozen).

## Phase 2 external CDA (E68; split recorded here in R25, after generation began, before analysis)
Original registration: EXPERIMENTS.tsv E68-declared (2026-10-24 14:23 UTC); E68-manip (17:12).
`data/ext_cda`: seeds **0–14** in each of `comms` / `nocomms`, matched by seed; 30 rounds,
3 qwen-3.6-35b sellers (Aqueduct), 2 adaptive ZIP buyers. All 30 games are confirmatory; no tuning or dev split.
Discarded `ext_cda_smoke_v0` is never pooled. Analyse once after 15 + 15 complete games, or from Sun 10:00 UTC
with completed games (explicit interim counts; `--min-runs 2` allows the deadline-truncated sample only after that cutoff).
R25 pre-analysis implementation correction (19:18 UTC, before any full-set aggregate): manipulation CI resamples
seed clusters, retaining both arms of a matched seed; unmatched completed seeds at the cutoff remain as singletons
and are counted. The all-game point contrast is unchanged. A positive unrounded lower CI bound is required;
a negative ask effect is not collusion elicited. Frozen detector definitions and AUROC bootstraps are unchanged.
