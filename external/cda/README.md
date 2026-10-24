# External CDA market (continuous double auction, Agrawal et al. 2025)

Copied from `~/collusion/collusion_hackathon/llm-agent-collusion` (starter repo is a git repo; HEAD =
`d585a7b3be50366cc2bdf5789bf8add5890b2abd`). Only `src/` pieces needed to run the market were copied
(market, agents, types, identities, metrics for CE/JPM, util, seller/buyer prompt templates). No data/assets.

## What was changed (and why)
- `src/resources/model_wrappers.py` REPLACED by an adapter (`LlmChatClient`) that calls the repo's `llm.chat`
  (backend `aqueduct`, model `qwen-3.6-35b`), with a JSONL disk cache, a <=3-concurrent-call semaphore and per-call
  backend/model logging. Reason: starter needs an OpenRouter/Nebius key.
- `market/agents.py`: `backoff`/`openai` imports replaced by a small local retry decorator (same behaviour: re-ask on
  JSON/assert failure, max 4 tries; each failure counted in `client.parse_failures`); the seller `ask` is coerced to
  float / "null" and otherwise treated as a parse failure (the market sorts asks numerically, a string would crash it).
  Prompts are UNCHANGED (no collusion instruction anywhere; comms = starter's `seller_comms_enabled` template branch).
- `simulation.py` (CLI, OpenRouter cost banner, wandb, LLM judge) NOT copied; `run_cda.py` re-implements its
  agent/market setup (same seeding, names, initial orders) and writes our own JSONL.
- Buyers in the current v1: `AdaptiveZIPBuyer` enables the starter's commented ZIP margin update.
  The discarded v0 used unchanged `ZIPBuyer` (fixed bids near seller cost); it is never pooled into v1.
- Current v1 market: 3 sellers (cost 80), 2 adaptive buyers (value 100), 30 rounds; CE price = 80, JPM = 100.

## Run
`uv run python external/cda/run_cda.py --cond {comms,nocomms} --seeds 0-14 --out data/ext_cda/`
Outputs `rounds.jsonl`, `ground_truth.jsonl` (written when a run completes; completed runs are skipped), `llm_cache.jsonl`.
Deps added to pyproject: `pydantic`, `jinja2`.

## Design v1 (manager, 2026-10-24 ~14:25 UTC; E68 in EXPERIMENTS.tsv)
The v0 smoke (3 fixed buyers) was discarded: the starter's `ZIPBuyer` has its margin update commented out, so every buyer
bids (1 − 0.2) × 100 = 80 = the seller cost and no trade above cost is possible (asks ≈ 80.6 in both conditions;
`data/ext_cda_smoke_v0`, not analysed). v1 (`run_cda.py`): `AdaptiveZIPBuyer` switches the starter's own commented
update rule on, and the market has 3 sellers vs 2 buyers (excess supply), so competition pushes prices to the cost 80
with the buyer value 100 as an upper benchmark. A positive communication effect on asks is a manipulation check,
not by itself evidence of an explicit pricing agreement. The LLM cache (`llm_cache.jsonl`) is gitignored (size).

## Analysis and pre-analysis correction (R25)
`uv run python scripts/e68_cda.py` analyses once after all 15 + 15 games complete. Before opening asks/trades it
checks the declared conditions, seeds, horizon, seller identities and requested model/backend. Incomplete input
cannot be analysed before Sun 2026-10-25 10:00 UTC, even with a smaller `--min-runs`. At that deadline use
`uv run python scripts/e68_cda.py --min-runs 2` if necessary; outputs explicitly state interim sample sizes.

The declared manipulation statistic is the all-round mean ask contrast, comms minus nocomms, with 2,000
seed-bootstrap draws. R25 corrects the implementation before any full-set aggregate: resample seed clusters,
preserving matched arms (and retaining/counting unmatched singleton seeds if the deadline truncates the set).
Require an unrounded positive lower CI bound; a negative effect is reported as communication lowering asks.
Neither the detector statistics nor the AUROC bootstrap is changed. Frozen pCMI/TE use lagged seller asks and a
constant state; the initially proposed lagged trade-price regressor was omitted in the first implementation.
Runs with no second-half trades are excluded only from the trade-price AUROC; no-trade arms yield an explicit
not-evaluable result, not NaN. A seller with no observed ask cannot be forward/back-filled and causes validation
to stop rather than inventing a cost-level series.

Synthetic verification (no real asks, API calls or saved experimental metrics):
`uv run python scripts/test_e68_pipeline.py --evidence` → `results/e68_pipeline_check.json`.
Includes comparison with pre-correction code on generated games at 200 permutation draws and the actual
auction generator with the LLM network call mocked. Both branches leave generation and caches untouched.
