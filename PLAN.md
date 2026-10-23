# PLAN — Q1.4: Can information-theoretic measures detect collusion in multi-agent games?

Umbrella project: *Beyond Words: Detecting AI-Agent Collusion Through Information Theory and
Behavioral Evidence*. This repo owns the **action-only, statistical** half. The sibling repo
(collusion-22-say-vs-do) owns text+action auditing and will reuse our trajectories.

## Core question
Do colluding agents' actions carry more shared information than explained by public market state
and the other participants — and can MI / CMI / pairwise net influence identify the colluding pair
while NOT accusing independent agents that merely respond to common information?
Builds on Bonjour et al. (2022, PMLR) information-theoretic collusion detection in repeated games.

## Environment (build first, simple, deterministic)
Repeated pricing game, 4 sellers (A–D), prices ∈ {8,10,12,14,16}, differentiated-product
(logit or linear) demand so pricing above rivals ≠ zero sales. Public state: demand shock / cost
shock. Validate: compute competitive (Nash) and collusive (joint-profit) benchmarks before agents.

Conditions (randomise the colluding pair across runs):
| | private coordination | common shocks |
|---|---|---|
| A independent baseline | no | no |
| B common-information control | no | yes |
| C collusion-enabled | designated pair | no |
| D collusion + common info | designated pair | yes |

Scripted agents first (zero API cost): best-response / noisy best-response / myopic / rule-based
independents; colluding pairs via e.g. grim-trigger, tit-for-tat price matching, signalled
alternation, partial collusion (collude with prob p) — vary collusion strength to get a
detection-vs-strength curve.

**Hard negatives (essential):** common shocks; *shared policy* (two agents running the same
policy/model with no channel — they correlate and CMI on market state will NOT remove that;
report it as a finding); legit leader-follower price matching; independent agents that happen
to be high-priced.

## Detectors (all consume trajectories.jsonl only)
Pearson/Spearman correlation of prices and of price changes; MI(a_i; a_j); CMI(a_i; a_j | public
state, lagged own/others' actions); lagged/transfer-entropy variants (a_i,t ; a_j,t+1 | ...);
pairwise net influence (Bonjour et al.) — excess dependence of a pair relative to the other pairs.
Estimators: plug-in with small alphabets + bias correction (Miller–Madow) and/or KSG for continuous;
compare.

**Nulls:** rounds are NOT iid. Use within-game nulls: circular shift / block permutation of one
agent's series, or surrogate games from the independent condition. Report p-values and calibrated
scores. Report how detection power scales with number of rounds T (5, 10, 20, 50, 100, 200).

## Must-pass gate (before any LLM spend)
On scripted data, the CMI/net-influence detector ranks the planted pair #1 of 6 in clearly > chance
(e.g. top-1 ≥ 0.8 at T=100 with strong collusion) AND false-positive rate at α=0.05 stays ≈ 5% on
conditions A/B. If not, fix the simulator/estimator first.

## Then: LLM agents
LLM sellers via `llm.py` (codex / Go): 20–40 games × 15–25 rounds, conditions A–D; collusion-enabled
pairs get a private chat channel. Verify separately whether an agreement formed (read private chat)
and whether actions realised it — keep label levels separate. Optional realism test on the starter's
double auction (`~/collusion/collusion_hackathon/llm-agent-collusion`) — reuse, don't rebuild.

## Metrics
AUROC (run-level: collusive vs control), pair identification top-1 accuracy, FPR at fixed α,
detection delay (rounds needed), all with bootstrap CIs over runs. Held-out seeds for final numbers.

## Deliverables
Datasets (`data/scripted_v*/`, `data/llm_v*/`) in SCHEMA.md format — publish early so the sibling
repo can use them; detectors in `detectors/`; REPORT.md with figures: power vs T, power vs collusion
strength, FPR under hard negatives, MI vs CMI vs net-influence comparison, LLM pilot results.
