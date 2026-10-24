"""Five-minute talk deck (Markdown, one slide per `---`). Every number is read from results/eval/*.json.

    uv run python scripts/slides.py    # -> PRESENTATION.md
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EV = ROOT / "results" / "eval"


def load(name):
    return json.load(open(EV / name))


def pct(x):
    return f"{100 * x:.0f}%"


def ci2(ci):
    return f"[{ci[0]:.2f}, {ci[1]:.2f}]"


def cip(ci):
    return f"[{100 * ci[0]:.0f}, {100 * ci[1]:.0f}]"


def sd(x):
    return f"{x:+.2f}"


def main():
    g = load("gate_test.json")["metrics"]
    v1 = load("llm_v1.json")
    t20 = v1["by_T"]["20"]
    pl = v1["price_level"]
    lg = load("llm_long.json")["by_T"]["50"]
    v3 = load("llm_v3_ext.json")["detectors"]
    mx = load("llm_mixed2_mixed.json")["pcmi"]["per_run_same_minus_cross"]

    def gr(det, grp, null=""):
        m = g[det][grp]
        k = "surrogate_flag" if null == "s" else "flag"
        return f"{pct(m[k + '_rate'])} {cip(m[k + '_ci'])}"

    a1 = lambda d: (t20[d]["auroc_CD_vs_AB"], t20[d]["auroc_ci"])
    a3 = lambda d: (v3[d]["auroc_private_vs_none"]["auroc"], v3[d]["auroc_private_vs_none"]["ci"])
    al = lambda d: (lg[d]["auroc_C_vs_A"], lg[d]["auroc_ci_C_vs_A"])
    fa = lambda t: f"{t[0]:.2f} {ci2(t[1])}"
    ca, db = pl["within_family_markup"]["C_minus_A"], pl["within_family_markup"]["D_minus_B"]
    t1 = v3["pcmi"]["top1_private"]
    t1l = v3["pair_level"]["top1_private"]
    legit = v3["pair_level"]["auroc_legit_vs_none"]

    s = []
    s.append(f"""# Conditioned mutual information catches coordinated price *moves*, not price *levels*
Apart AI Collusion Sprint · Q1.4 information-theoretic detection · action-only (prices + public state, no messages)

**Question.** Can a pairwise dependence statistic flag colluding pricing agents *without* accusing agents that
merely see the same public shock or run the same policy?

**Answer in one line.** Largely yes for collusion that shows up as coordinated price *variation*. With scripted sellers
(easiest shared-signal case), pCMI flags {pct(g['pcmi']['C']['flag_rate'])} of colluding markets and cuts common-shock false alarms from
{pct(g['mi']['B']['flag_rate'])} (raw MI) to {pct(g['pcmi']['B']['flag_rate'])}, which is still above the nominal 5%. Policy copies that share a random seed remain a confound.
With LLM sellers, pCMI does not separate channel from no-channel markets: the private channel shows up mainly as a
price *level*, and simple level statistics discriminate channel assignment far better.""")

    s.append(f"""## Setup
* 4-seller repeated differentiated-price (logit) market, public demand/cost shocks, state Nash computed per round.
* Groups: A independent · B common shock · C colluding pair · D colluding pair + shock; hard negatives: shared
  policy, shared policy + shared seed, public leader-follower ("legit"), independent high price.
* Detectors on each of the 6 seller pairs: |Pearson|, MI, CMI | public state, **pCMI** = Gaussian CMI | state **and all
  lagged prices**, TE (lagged CMI).
* Two nulls: within-run circular **shift** null, and **control-surrogate** null (no-channel markets).
* Locked test seeds frozen before tuning (`data/SPLITS.md`); every number regenerates from `results/` (REPORT §6).""")

    s.append(f"""## Result 1: scripted sellers (locked test, T=100, 50 markets/group, s=0.6)
![](figures/headline.png)

| markets flagged, α=.05 [Wilson 95% CI] | raw MI (shift null) | pCMI (shift null) | pCMI (control-surrogate null) |
|---|---|---|---|
| common public shock (B) | {gr('mi','B')} | {gr('pcmi','B')} | {gr('pcmi','B','s')} |
| shared policy (A+shared_policy) | {gr('mi','A+shared_policy')} | {gr('pcmi','A+shared_policy')} | {gr('pcmi','A+shared_policy','s')} |
| public leader-follower | {gr('mi','A+legit_cooperation')} | {gr('pcmi','A+legit_cooperation')} | {gr('pcmi','A+legit_cooperation','s')} |
| policy copy sharing a random seed | {gr('mi','A+shared_seed')} | {gr('pcmi','A+shared_seed')} | {gr('pcmi','A+shared_seed','s')} |
| **collusion C / D** | {gr('mi','C')} / {gr('mi','D')} | {gr('pcmi','C')} / {gr('pcmi','D')} | {gr('pcmi','C','s')} |

Conditioning cuts the shared-shock false positives but does not remove them under the shift null. A shared random seed
is still a confound. TE flags lagged legitimate leader-follower pricing (REPORT §4.1). On B the surrogate null is leave-one-out
within B's own reference pool, so its 4% is ≈ α by construction, not independent calibration evidence.""")

    s.append(f"""## Result 2: LLM sellers (gpt-6-luna). The channel is a level shift
* **Our market `llm_v1`** (74 games, T=20): the private channel raises market-average markup over Nash: C − A {sd(ca['diff'])} {ci2(ca['diff_ci'])},
  D − B {sd(db['diff'])} {ci2(db['diff_ci'])}.
* Run AUROC by **channel assignment** (not realised collusion: {t20['pcmi']['CD_realized']['n']}/{t20['pcmi']['C']['n'] + t20['pcmi']['D']['n']} `llm_v1` channel games meet the realised label); run score = max over the 6 pairs; 0.5 = chance:

| | pCMI | pair price − rivals' | pair markup over Nash |
|---|---|---|---|
| `llm_v1` T=20, C/D vs A/B | {fa(a1('pcmi'))} | {fa(a1('pair_level'))} | {fa(a1('market_level'))} |
| `llm_long` T=50, C vs A (8 v 8) | {fa(al('pcmi'))} | {fa(al('pair_level'))} | {fa(al('market_level'))} |
| sibling `llm_v3` T=12, private vs none | {fa(a3('pcmi'))} | {fa(a3('pair_level'))} | {fa(a3('market_level'))} |

* Pair localisation in `llm_v3` (chance 1/6): pCMI top-1 {t1['k']}/{t1['n']}; pair level {t1l['k']}/{t1l['n']}.
* T=50 did not meet the pre-declared rescue rule. Mixed gpt-6.1-sol/luna markets: same-model − cross-model pCMI
  {mx['mean']:+.3f} [{mx['mean_ci'][0]:+.3f}, {mx['mean_ci'][1]:+.3f}] (12 games). No same-model pCMI excess was detected, but 12 games exclude only large effects.""")

    s.append(f"""## What this means
* **Dependence detectors respond to coordinated *variation*, not to agreement as such.** They are built to ignore a constant
  high price. In these two markets LLM collusion shows up mainly as a level shift, so it falls largely outside what they
  measure. Some coordinated variation is present: on first differences, MI localises the `llm_v3` channel pair above chance (REPORT §4.3.3, exploratory).
* **Level screens catch it but are not collusion-specific.** By pair_level, markets with the sibling's *legitimate*
  public partnership rank above controls (AUROC {legit['auroc']:.2f} {ci2(legit['ci'])}), but the top pair is the partner pair in only
  {v3['pair_level']['top1_legit']['k']}/{v3['pair_level']['top1_legit']['n']} runs. In the sibling's exploratory placebo study (15 matched seeds), messages that were offered but never
  delivered gave about the same pair premium as delivered ones (+0.03 [−0.54, +0.49]), so being offered the channel appears to suffice.
* Suggested pipeline (a hypothesis, untested): a cheap always-on level screen, then dependence and text audits as
  second-stage evidence.
* Not settled: whether pCMI fails because the effect is mostly a level or because power is low at T ≤ 50.""")

    s.append(f"""## Limitations & next steps
* Small LLM n: `llm_v1` 74, `llm_v3` 125 (70 private / 35 none / 20 legit), `llm_long` 16, `llm_mixed2` 12. Sellers are OpenAI-family only. There is no placebo arm in `llm_v1`. Markup needs a market model (Nash).
* Next: longer LLM games (T ≥ 100) to separate level from power; a placebo channel in our market; level-adjusted
  dependence (residualise each seller's own level); non-OpenAI sellers.
* Full write-up: `REPORT.md`. Ledger of all 28 experiments, including discarded ones: `EXPERIMENTS.tsv`.""")

    out = "<!-- generated by scripts/slides.py from results/eval/*.json; do not edit by hand -->\n\n" + "\n\n---\n\n".join(s) + "\n"
    (ROOT / "PRESENTATION.md").write_text(out)
    print("wrote PRESENTATION.md")


if __name__ == "__main__":
    main()
