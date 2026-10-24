# Reimplementation brief (independent check)
You are given ONLY a method description (excerpted verbatim from a research report) and data. Do NOT read any
code outside this directory (in particular nothing under /home/factory/collusion/). Implement the statistics from
the description yourself in Python (use /home/factory/collusion/collusion-14-infotheory/.venv/bin/python, which has numpy/scipy/scikit-learn;
write your code in /var/tmp/c14/reimpl/reimpl.py) and write results to /var/tmp/c14/reimpl/results.json and a short
/var/tmp/c14/reimpl/NOTES.md listing every interpretation choice you had to make where the description was ambiguous.

## Data
data/<name>/trajectories.jsonl: one row per (run_id, round): market = {demand_shock: low|high, cost: 6|8} (public state),
agents = list of 4 sellers A,B,C,D with price. Ignore messages/profit. data/<name>/labels.jsonl: run_id, condition (A,B,C,D),
assigned_pair (colluding pair in C/D, null in A/B). Market facts: the per-round competitive (Nash) price is 10 when cost=6 and 12 when cost=8.
Datasets: llm_v1 (74 runs, T=20, conditions A,B,C,D) and llm_long (16 runs, T=50, conditions A,C).

## Method description (verbatim excerpt)
## 3. Detectors (`detectors/infotheory.py`, read `trajectories.jsonl` only)
Per run and pair: |Pearson| of prices and of price changes; plug-in MI with Miller–Madow correction;
CMI given the discrete public state; **pCMI** = −½ log(1−ρ²) of residuals after regressing each agent's
price on state dummies and *all four lagged prices*; lagged CMI/TE (max over directions); and Bonjour-style
net influence (pair score minus mean of the other pairs). **Null:** B=200 draws, each circularly shifting
every agent's series by its own random offset (all pairwise relative offsets ≥ 3 rounds); raw-price
statistics use plain shifts, CMI|state shifts within each state stratum (keeps each seller's price–state
relation), pCMI/TE re-residualise the shifted residuals on the design. Run-level p-value = max-over-pairs
statistic against its null. Rounds are not iid, so we never use iid permutation. With fewer than 20
valid shifts (T ≲ 13) no test is performed (p = 1). Calibration is checked empirically on control runs
(below), not assumed.


*Pre-registered baseline fix (E12, before any llm_v1 detector output was viewed):* `market_level` is the pair's
mean **markup over the per-round state Nash** (raw mean price is confounded by B/D cost shocks; the raw version is
kept as `market_level_raw`). AUROCs are reported pooled (C/D vs A/B) and within family (C vs A, D vs B); "do
dependence detectors add anything beyond level?" = AUROC(IT) − AUROC(level), paired bootstrap over runs.

## What to compute
For every run and each of the 6 seller pairs: (1) pCMI score; (2) plug-in MI with Miller–Madow correction on the
raw integer prices; (3) market_level = pair's mean markup over per-round Nash (mean over both members and rounds);
(4) pair_level = pair mean price minus mean price of the other two sellers. Run-level score = max over pairs.
Then: run AUROC (C/D vs A/B pooled; C vs A; D vs B) for each statistic on llm_v1 using all 20 rounds, and C vs A on
llm_long using all 50 rounds and using the first 20 rounds. Also the pCMI shift-null run-level p-value (B=200) for
every llm_v1 run, and the fraction of A runs and of C runs with p < 0.05. Save per-run scores in results.json
(keys: dataset -> statistic -> run_id -> run score; plus the AUROCs and flag rates).
