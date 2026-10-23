"""E15 (exploratory, not a headline): where does raw-price MI/Pearson localisation on llm_v3 come from?

Hypothesis: the channel pair *drifts up together* (a shared level trend), so raw-price dependence localises it,
while anything that removes trends/levels (first differences, lagged-price conditioning as in pCMI) does not.
Top-1 localisation of the assigned pair in `private` runs (ties broken uniformly at random), chance 1/6.

    uv run python -m experiments.diag_llm_v3   # -> results/eval/llm_v3_diag.json
"""
from __future__ import annotations

import json

import numpy as np
from scipy.stats import binomtest

from detectors.infotheory import PAIR_NAMES, PAIRS, mi_mm
from experiments.ext_llm_v3 import ROOT, load
from experiments.llm_eval import auroc_ci


def _absr(x, y):
    if x.std() == 0 or y.std() == 0:
        return 0.0
    return float(abs(np.corrcoef(x, y)[0, 1]))


def _detrend(x):
    t = np.arange(len(x))
    return x - np.polyval(np.polyfit(t, x, 1), t)


VARIANTS = {
    "MI raw prices": lambda P, i, j: mi_mm(P[:, i].astype(int), P[:, j].astype(int)),
    "|Pearson| raw prices": lambda P, i, j: _absr(P[:, i], P[:, j]),
    "|Pearson| linear-detrended": lambda P, i, j: _absr(_detrend(P[:, i]), _detrend(P[:, j])),
    "|Pearson| first differences": lambda P, i, j: _absr(np.diff(P[:, i]), np.diff(P[:, j])),
    "MI first differences": lambda P, i, j: mi_mm(np.diff(P[:, i]).astype(int), np.diff(P[:, j]).astype(int)),
    "pair_level (pair mean - rivals mean)": lambda P, i, j: float(
        P[:, [i, j]].mean() - P[:, [k for k in range(4) if k not in (i, j)]].mean()),
}


def main(n_rep=200):
    gt, _, rows = load()
    rng = np.random.default_rng(0)
    out = {}
    priv = [r for r in sorted(rows) if gt[r]["condition"] == "private"]
    for name, f in VARIANTS.items():
        hits_rep = []
        for _ in range(n_rep):  # average over random tie-breaks (many sellers are near-constant at T=12)
            h = 0
            for rid in priv:
                P = np.array([[a["price"] for a in r["agents"]] for r in rows[rid]], float)
                truth = "".join(sorted(gt[rid]["assigned_pair"]))
                sc = {pn: f(P, i, j) for (i, j), pn in zip(PAIRS, PAIR_NAMES)}
                best = max(sc.values())
                h += rng.choice([p for p in PAIR_NAMES if sc[p] >= best - 1e-12]) == truth
            hits_rep.append(h)
        mx = {rid: max(f(np.array([[a["price"] for a in r["agents"]] for r in rows[rid]], float), i, j)
                       for i, j in PAIRS) for rid in rows}
        pos = [mx[r] for r in priv]
        neg = [mx[r] for r in rows if gt[r]["condition"] == "none"]
        auc = auroc_ci(pos, neg)
        k = int(round(np.mean(hits_rep)))
        out[name] = {"n": len(priv), "top1_mean_hits": float(np.mean(hits_rep)),
                     "p_binom_vs_1/6": binomtest(k, len(priv), 1 / 6, alternative="greater").pvalue,
                     "auroc_private_vs_none": auc, "n_none": len(neg)}
        print(f"{name:40s} top-1 {np.mean(hits_rep):5.1f}/{len(priv)}  p={out[name]['p_binom_vs_1/6']:.2g}  AUROC priv vs none {auc}")
    (ROOT / "results/eval/llm_v3_diag.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
