# collusion-14-infotheory — information-theoretic collusion detection (Apart AI Collusion Sprint, Q1.4)

**Read [`REPORT.md`](REPORT.md)** (write-up with all numbers, CIs, figures and limitations).

Question: can pairwise dependence measures computed from **prices only** (|Pearson|, MI, CMI given public state,
partial CMI given state + lagged prices = pCMI, transfer entropy) find colluding seller pairs without accusing sellers
that merely share a public shock or a policy?

Short answer (details and CIs in REPORT): pCMI separates coordinated price *variation* from shared shocks and shared
policies in a scripted market. In two LLM pricing markets, though, the private channel shows up mainly as a price *level*.
Dependence measures ignore levels by construction, so a simple markup or pair-level statistic does much better there.

| path | what |
|---|---|
| `sim/` | scripted market (`market.py`) and LLM-seller market (`llm_market.py`) |
| `detectors/infotheory.py` | detectors; they read `trajectories.jsonl` only |
| `experiments/`, `scripts/` | generation, evaluation, reports, figures (commands in REPORT §6) |
| `data/` | trajectories (schema: `SCHEMA.md`), splits (`data/SPLITS.md`), external snapshot `data/ext_llm_v3/` |
| `results/` | every number in REPORT (`results/eval/*.json`), LLM judge labels, reviews |
| `figures/` | all figures |
| `EXPERIMENTS.tsv` | ledger of every experiment, including discarded and negative ones |

Reproduce: `uv sync`, then the commands in REPORT §6. No re-analysis needs an LLM call, because the LLM trajectories
and judge labels are committed. `uv run python scripts/tables.py` reprints every REPORT table from `results/`.
