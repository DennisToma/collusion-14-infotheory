"""Five-minute talk deck (Markdown, one slide per `---`). Every number is read from results/eval/*.json.

    uv run python scripts/slides.py    # -> PRESENTATION.md
"""
import json
from scipy.stats import binomtest
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
    n_exp = max(int(l.split('\t')[1][1:3]) for l in open(ROOT / 'EXPERIMENTS.tsv').read().splitlines()[1:] if l.split('\t')[1][:1] == 'E')
    mx = load("llm_mixed2_mixed.json")["pcmi"]["per_run_same_minus_cross"]
    inj = {(r["dataset"], r["T"], r["controls"]): r for r in load("injection_mde.json")}
    inj50 = inj[("llm_long", 50, "A")]
    inj20 = inj[("llm_v1", 20, "A")]

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

**Answer.** Partly. With scripted sellers (easiest shared-signal case), pCMI flags {pct(g['pcmi']['C']['flag_rate'])} of colluding markets and
cuts common-shock false alarms from {pct(g['mi']['B']['flag_rate'])} (raw MI) to {pct(g['pcmi']['B']['flag_rate'])} (target 5%). Copies of one policy that share a random
seed still look like collusion. With LLM sellers, pCMI was not distinguishable from chance (wide CIs): the private channel mainly raised
price *levels*, and simple level statistics detect it far better.""")

    s.append(f"""## Setup
* 4-seller repeated differentiated-price (logit) market, public demand/cost shocks, state Nash computed per round.
* Groups: A independent · B common shock · C colluding pair · D colluding pair + shock; hard negatives: shared
  policy, shared policy + shared seed, public leader-follower ("legit"), independent high price.
* Detectors score each of the 6 seller pairs: correlation; **MI** (mutual information: do two price series move together?);
  **pCMI** (the same after removing what public shocks and everyone's past prices explain); **TE** (does one seller's
  past predict the other's price?).
* A market is flagged if its top pair beats a baseline: the same game with series time-shifted out of sync (**shift
  null**), or real no-channel markets (**control null**). **AUROC**: 0.5 = coin flip, 1.0 = perfect ranking.
* Locked test seeds frozen before tuning (`data/SPLITS.md`); every number regenerates from `results/` (REPORT §6).""")

    s.append(f"""## Result 1: scripted sellers (locked test, T=100, 50 markets/group, collusion strength 0.6 of 1)
![](figures/headline.png)

| % of markets flagged (target for innocent groups: 5%) [95% CI] | raw MI (shift null) | pCMI (shift null) | pCMI (control null) |
|---|---|---|---|
| common public shock (B) | {gr('mi','B')} | {gr('pcmi','B')} | {gr('pcmi','B','s')} |
| same policy, independent noise | {gr('mi','A+shared_policy')} | {gr('pcmi','A+shared_policy')} | {gr('pcmi','A+shared_policy','s')} |
| public leader-follower | {gr('mi','A+legit_cooperation')} | {gr('pcmi','A+legit_cooperation')} | {gr('pcmi','A+legit_cooperation','s')} |
| policy copy sharing a random seed | {gr('mi','A+shared_seed')} | {gr('pcmi','A+shared_seed')} | {gr('pcmi','A+shared_seed','s')} |
| **collusion C / D** | {gr('mi','C')} / {gr('mi','D')} | {gr('pcmi','C')} / {gr('pcmi','D')} | {gr('pcmi','C','s')} / {gr('pcmi','D','s')} |

Conditioning removes most shared-shock false alarms (100% → 14%), but not all. A shared random seed is indistinguishable
from a private signal. TE (not shown) flags legitimate public leader-follower pricing in {pct(g['te']['A+legit_cooperation']['flag_rate'])} of runs.
(The 4% for B under the control null is ≈ 5% by construction.)""")

    s.append(f"""## Result 2: LLM sellers (gpt-6-luna). The channel is a level shift
* **Our market `llm_v1`** (74 games, T=20): the private channel raises the average markup over the competitive (Nash)
  price by {sd(ca['diff'])} price units {ci2(ca['diff_ci'])} (C vs A) and {sd(db['diff'])} {ci2(db['diff_ci'])} (D vs B).
* AUROC for telling channel markets from no-channel markets (best pair per market; 0.5 = chance). This measures channel
  *assignment*: only {t20['pcmi']['CD_realized']['n']}/{t20['pcmi']['C']['n'] + t20['pcmi']['D']['n']} `llm_v1` channel games show realised collusion (verified agreement + coordinated price actions).

| | pCMI | pair price − rivals' | pair markup over Nash |
|---|---|---|---|
| `llm_v1` T=20, C/D vs A/B | {fa(a1('pcmi'))} | {fa(a1('pair_level'))} | {fa(a1('market_level'))} |
| `llm_long` T=50, C vs A (8 v 8) | {fa(al('pcmi'))} | {fa(al('pair_level'))} | {fa(al('market_level'))} |
| sibling `llm_v3` T=12, private vs none | {fa(a3('pcmi'))} | {fa(a3('pair_level'))} | {fa(a3('market_level'))} |

* Pair localisation in `llm_v3` (chance 1/6): pCMI top-1 {t1['k']}/{t1['n']} (nominal p={binomtest(t1['k'], t1['n'], 1/6, alternative='greater').pvalue:.3f}, uncorrected; not read as signal); pair level {t1l['k']}/{t1l['n']}.
* Longer games (T=50) did not rescue pCMI by our pre-declared rule (8 v 8 games, so only large effects are excluded).
* Mixed-model markets (2 gpt-6.1-sol + 2 gpt-6-luna, 12 games): same-model minus cross-model pCMI {mx['mean']:+.3f} [{mx['mean_ci'][0]:+.3f}, {mx['mean_ci'][1]:+.3f}];
  no shared-model excess detected (only large effects excluded).""")

    s.append(f"""## What this means
* **Dependence detectors respond to coordinated *variation*, not to agreement as such.** They are built to ignore a constant
  high price. In these two markets LLM collusion shows up mainly as a level shift, so it falls largely outside what they
  measure. Some coordinated variation is present: on first differences, MI localises the `llm_v3` channel pair above chance (REPORT §4.3.3, exploratory).
* **Level screens separate channel assignment but are not collusion-specific.** They also rank markets with a *legitimate* public
  partnership above controls (AUROC {legit['auroc']:.2f}), naming the partner pair in only {v3['pair_level']['top1_legit']['k']}/{v3['pair_level']['top1_legit']['n']} runs. In the sibling
  project, *offering* a private channel that never delivered messages raised prices about as much as delivering them
  (exploratory, 15 seeds).
* Suggested pipeline (a hypothesis, untested): a cheap always-on level screen, then dependence and text audits as
  second-stage evidence.
* Not settled: whether pCMI fails because the effect is mostly a level or because power is low at T ≤ 50.
  Exploratory check (REPORT §4.3.8, post-hoc): per-round shared ±1 price shocks planted into one pair (in 20% of rounds) of real no-channel LLM games
  are detected by pCMI with AUROC {inj50['by_q']['0.2']['auroc_single_planting']:.2f} {ci2(inj50['by_q']['0.2']['auroc_ci_game_cluster'])} at T=50
  but only {inj20['by_q']['0.2']['auroc_single_planting']:.2f} {ci2(inj20['by_q']['0.2']['auroc_ci_game_cluster'])} at T=20. The real channel pairs show no detected excess
  same-direction moves (T=50: {inj50['observed']['C']['comove_excess_mean']:+.3f} [{inj50['observed']['C']['ci'][0]:+.3f}, {inj50['observed']['C']['ci'][1]:+.3f}]). This fits the level reading for one planted alternative; it does not settle the question.""")

    s.append(f"""## Limitations & next steps
* Small LLM n: `llm_v1` 74, `llm_v3` 125 (70 private / 35 none / 20 legit), `llm_long` 16, `llm_mixed2` 12. Sellers are OpenAI-family only. There is no placebo arm in `llm_v1`. Markup needs a market model (Nash).
* Next: longer LLM games (T ≥ 100) to separate level from power; a placebo channel in our market; level-adjusted
  dependence (residualise each seller's own level); non-OpenAI sellers.
* Full write-up: `REPORT.md`. Ledger of every experiment (E01–E{n_exp:02d}), including discarded ones: `EXPERIMENTS.tsv`.""")

    out = "<!-- generated by scripts/slides.py from results/eval/*.json; do not edit by hand -->\n\n" + "\n\n---\n\n".join(s) + "\n"
    (ROOT / "PRESENTATION.md").write_text(out)
    print("wrote PRESENTATION.md")


if __name__ == "__main__":
    main()
