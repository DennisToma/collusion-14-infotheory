a shock or a policy. Detectors: |Pearson|, mutual information (MI), CMI given public state, Gaussian CMI given state
**and all lagged prices** (pCMI), and lagged CMI (TE), each compared with two baselines: the same game with seller price series circularly shifted out of alignment
(shift null) and comparable no-channel markets (control-surrogate null). **Scripted agents, locked test seeds (T=100, 50 runs/group):**
every contemporaneous detector flags and localises a planted shared-signal pair in 100% of runs. Raw MI also flags 100% of
markets whose independent sellers share a public shock. pCMI flags 14% of them under the shift null. The
surrogate null (which uses those markets as its reference pool, so ≈5% there by construction) flags only 4% [1, 13] of held-out markets with a shared policy plus common shock, and 4% with a public leader-follower pair. Two confounds remain:
policy copies that share their random seed (48–100% flagged by each contemporaneous detector in Table 4.1; 44% for differenced |Pearson|, §4.1), and lagged matching, where TE
flags legitimate leader-follower pricing in 100% of runs. Dependence detects coordinated *variation*, not agreement. A
constant high price (the tested stay-high setting) was not reliably localised by any of these estimators.
**LLM sellers** (gpt-6-luna; our market `llm_v1`, 74 games, T=20; sibling market `llm_v3`, 125 runs, T=12): a private channel
produces judge-verified agreements and raises markup over the competitive (Nash) price in `llm_v1` by +1.8 versus matched no-channel markets (C − A [1.2, 2.3], D − B [1.0, 2.5]),
but the effect is mainly a **price level**. Level statistics separate channel from control runs (run AUROC: `llm_v1` markup
0.87 [0.78, 0.94]; `llm_v3` pair_level 0.98 [0.95, 1.00]). pCMI is not distinguishable from chance (`llm_v1` 0.45 [0.32, 0.59]; `llm_v3` 0.52 [0.39, 0.64]),
and in an exploratory leave-one-run-out logistic model, adding it to markup gave no detectable improvement (−0.02 [−0.08, +0.01]). Longer games (T=50, 8 vs 8) did not meet the pre-declared
rescue criterion (pCMI 0.45 [0.16, 0.75] vs markup 0.95; the CI cannot exclude moderate effects). In mixed gpt-6.1-sol/gpt-6-luna markets, no pCMI same-model excess over
cross-model pairs was detected (+0.003 [−0.025, +0.032], 12 games; only large effects excluded). Supported claim: in these two markets
at T=12–50, the private channel shows up mainly as a price level, which conditioned dependence measures are built to ignore; level statistics discriminate channel assignment far better than pCMI. Some coordinated variation is present (pair localisation on first differences in `llm_v3`; part of it also appears in placebo runs, §4.3.9), and whether pCMI fails because the effect is mostly a level or because of low power at short T is not fully settled. An exploratory injection check (§4.3.8) plants per-round shared ±1 price shocks (in 20% of rounds) into one pair of real LLM control games: pCMI detects them at T=50 (AUROC 0.93 [0.87, 0.98]) but only weakly at T=20 (0.63–0.66), and the real channel pairs show no statistically detected excess co-movement relative to rivals. That fits the level reading but does not settle it. Level screens separate channel *assignment* but are not
collusion-specific (they rank legitimate public partnerships above controls, AUROC 0.75; in the sibling market an offered-but-undelivered placebo channel gave a similar premium, and pair_level named the pair about equally often, 13.5/15 vs 14/15, §4.3.9). In exploratory sibling monitor/firm-framing strata with no judge-labelled agreements, pair_level yielded 3.3/30 tie-averaged hits (chance expectation 5.0; §4.3.10); framing and agreement are confounded. In our own market, the first pair member to write pre-play already sets a provisional price above its rivals while writing its own first private message, before receiving any partner message (+0.94 [0.38, 1.59] vs whole-game premium +0.45; exploratory, descriptive, not a causal offer effect, §4.3.11).

## 1. Question and operational definition
**Question.** Do colluding agents' actions share more information than is explained by public market
state and the rest of the market — and can a detector that sees only prices name the colluding pair
while not accusing agents that respond to common information or share a policy?

**What we call collusion (explicit collusion).** A pair of sellers that has a *private agreement channel*
and uses it to coordinate supra-competitive pricing. This follows the communication-plus-action family of

codex
- **P1 — Wrong dataset for 14%.** Replace the sentence beginning “pCMI flags 14%” with: “pCMI flags 14% of common-shock markets under the shift null and 4% [1, 13] of held-out shared-policy-plus-shock markets under the surrogate null.”

- **P1 — +1.8 applies only to `llm_v1`.** Replace “a private channel raises markup over Nash by +1.8 (C − A [1.2, 2.3])” with: “in our market (`llm_v1`), a private channel raises markup over Nash by +1.8 versus matched no-channel markets (C − A [1.2, 2.3])”.

- **P1 — “At chance” overstates the evidence; the mechanism remains uncertain.** Replace the sentence beginning “pCMI is at chance” with: “pCMI is not distinguishable from chance (0.45–0.52), and neither longer games (T=50, 8 vs 8) nor same-model pairs revealed pCMI signal (both underpowered). Whether pCMI’s weak discrimination reflects mainly level effects or low power at short T remains unresolved.”
tokens used
6,726
- **P1 — Wrong dataset for 14%.** Replace the sentence beginning “pCMI flags 14%” with: “pCMI flags 14% of common-shock markets under the shift null and 4% [1, 13] of held-out shared-policy-plus-shock markets under the surrogate null.”

- **P1 — +1.8 applies only to `llm_v1`.** Replace “a private channel raises markup over Nash by +1.8 (C − A [1.2, 2.3])” with: “in our market (`llm_v1`), a private channel raises markup over Nash by +1.8 versus matched no-channel markets (C − A [1.2, 2.3])”.

- **P1 — “At chance” overstates the evidence; the mechanism remains uncertain.** Replace the sentence beginning “pCMI is at chance” with: “pCMI is not distinguishable from chance (0.45–0.52), and neither longer games (T=50, 8 vs 8) nor same-model pairs revealed pCMI signal (both underpowered). Whether pCMI’s weak discrimination reflects mainly level effects or low power at short T remains unresolved.”
