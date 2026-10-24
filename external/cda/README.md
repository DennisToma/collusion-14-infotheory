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
- Buyers: the starter's rule-based `ZIPBuyer` unchanged. NOTE: in this starter the ZIP adaptation is commented out,
  so each buyer bids a fixed `(1-0.2)*100 = 80 (+-1% noise)` every round, i.e. at the sellers' cost (80). Trades are
  therefore rare after the (randomised) initial orders; it is a weak, non-adaptive demand side.
- Market: 3 sellers (cost 80), 3 buyers (value 100), 30 rounds; CE price = 90, JPM price = 100 (starter metrics).

## Run
`uv run python external/cda/run_cda.py --cond {comms,nocomms} --seeds 0-14 --out data/ext_cda/`
Outputs `rounds.jsonl`, `ground_truth.jsonl` (written when a run completes; completed runs are skipped), `llm_cache.jsonl`.
Deps added to pyproject: `pydantic`, `jinja2`.

## Design v1 (manager, 2026-10-24 ~14:25 UTC; E68 in EXPERIMENTS.tsv)
The v0 smoke (3 fixed buyers) was discarded: the starter's `ZIPBuyer` has its margin update commented out, so every buyer
bids (1 − 0.2) × 100 = 80 = the seller cost and no trade above cost is possible (asks ≈ 80.6 in both conditions;
`data/ext_cda_smoke_v0`, not analysed). v1 (`run_cda.py`): `AdaptiveZIPBuyer` switches the starter's own commented
update rule on, and the market has 3 sellers vs 2 buyers (excess supply), so competition pushes prices to the cost 80
and only coordination holds them toward the buyer value 100. The LLM cache (`llm_cache.jsonl`) is gitignored (size).
