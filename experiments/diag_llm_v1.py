"""E19 (exploratory, after the llm_v1 review; not a headline): two checks the codex review asked for.

(1) Common-trend hypothesis for the raw-MI sign flip (C vs A AUROC 0.20, D vs B 0.82): if shared price trends drive raw
    dependence, then removing each seller's linear trend or taking first differences should pull both within-family
    AUROCs toward 0.5. Also reports the per-run slope of the market-mean price by condition.
(2) Incremental value: does pCMI (or MI) add to the level baseline when used *together* with it? Logistic regression,
    leave-one-out over runs, channel-assigned (C/D) vs control (A/B), features = max-pair markup (+ family dummy)
    vs the same + pCMI / + MI. Out-of-fold AUROCs and a paired bootstrap of the difference over runs.

    uv run python -m experiments.diag_llm_v1     # -> results/eval/llm_v1_diag.json
"""
from __future__ import annotations

import json

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

from detectors.infotheory import PAIRS, mi_mm
from experiments.diag_llm_v3 import _absr, _detrend
from experiments.llm_eval import ROOT, arrays, auroc_ci, load

VARIANTS = {
    "MI raw prices": lambda P, i, j: mi_mm(P[:, i].astype(int), P[:, j].astype(int)),
    "|Pearson| raw prices": lambda P, i, j: _absr(P[:, i], P[:, j]),
    "|Pearson| linear-detrended": lambda P, i, j: _absr(_detrend(P[:, i]), _detrend(P[:, j])),
    "|Pearson| first differences": lambda P, i, j: _absr(np.diff(P[:, i]), np.diff(P[:, j])),
    "MI first differences": lambda P, i, j: mi_mm(np.diff(P[:, i]).astype(int), np.diff(P[:, j]).astype(int)),
}


def common_trend(gt, rows):
    out = {}
    cond = {r: gt[r]["condition"] for r in rows}
    for name, f in VARIANTS.items():
        mx = {}
        for rid in rows:
            P, _, _ = arrays(rows[rid])
            mx[rid] = max(f(P, i, j) for i, j in PAIRS)
        out[name] = {}
        for a, b in (("C", "A"), ("D", "B")):
            out[name][f"{a}_vs_{b}"] = auroc_ci([mx[r] for r in rows if cond[r] == a], [mx[r] for r in rows if cond[r] == b])
        print(f"{name:32s} C vs A {out[name]['C_vs_A'][0]:.2f} {np.round(out[name]['C_vs_A'][1], 2)}   "
              f"D vs B {out[name]['D_vs_B'][0]:.2f} {np.round(out[name]['D_vs_B'][1], 2)}")
    slopes = {}
    for c in "ABCD":
        s = []
        for rid in rows:
            if cond[rid] != c:
                continue
            m = arrays(rows[rid])[0].mean(1)
            s.append(np.polyfit(np.arange(len(m)), m, 1)[0])
        s = np.array(s)
        slopes[c] = {"mean_slope_per_round": float(s.mean()), "abs_slope_mean": float(np.abs(s).mean()),
                     "frac_up": float((s > 0).mean()), "n": len(s)}
        print(f"market-mean slope {c}: mean {s.mean():+.3f}/round, |slope| {np.abs(s).mean():.3f}, up {(s > 0).mean():.2f} (n={len(s)})")
    return out, slopes


def incremental(gt, ev, B=2000, seed=0):
    sc = ev["run_scores"]["20"]
    rids = sorted(r for r in sc["pcmi"] if gt[r]["condition"] in "ABCD")
    y = np.array([gt[r]["condition"] in "CD" for r in rids], int)
    fam = np.array([gt[r]["condition"] in "BD" for r in rids], float)
    col = lambda d: np.array([sc[d][r] for r in rids], float)
    z = lambda x: (x - x.mean()) / (x.std() + 1e-12)
    feats = {"markup": [z(col("market_level")), fam],
             "markup+pCMI": [z(col("market_level")), fam, z(col("pcmi"))],
             "markup+MI": [z(col("market_level")), fam, z(col("mi"))],
             "markup+pCMI+MI+TE": [z(col("market_level")), fam, z(col("pcmi")), z(col("mi")), z(col("te"))]}
    oof = {}
    for k, cols in feats.items():
        X = np.column_stack(cols)
        p = np.zeros(len(y))
        for i in range(len(y)):  # leave-one-run-out
            m = np.ones(len(y), bool)
            m[i] = False
            p[i] = LogisticRegression(C=1.0, max_iter=1000).fit(X[m], y[m]).predict_proba(X[i:i + 1])[0, 1]
        oof[k] = p
    rng = np.random.default_rng(seed)
    pos, neg = np.where(y == 1)[0], np.where(y == 0)[0]
    out = {k: {"auroc_oof": float(roc_auc_score(y, p))} for k, p in oof.items()}
    for k in feats:
        if k == "markup":
            continue
        d = []
        for _ in range(B):
            idx = np.r_[rng.choice(pos, len(pos)), rng.choice(neg, len(neg))]
            d.append(roc_auc_score(y[idx], oof[k][idx]) - roc_auc_score(y[idx], oof["markup"][idx]))
        out[k]["diff_vs_markup"] = float(out[k]["auroc_oof"] - out["markup"]["auroc_oof"])
        out[k]["diff_ci"] = [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]
    for k, v in out.items():
        print(f"LOO logistic {k:20s} AUROC {v['auroc_oof']:.3f}" +
              (f"  diff vs markup {v['diff_vs_markup']:+.3f} [{v['diff_ci'][0]:+.3f}, {v['diff_ci'][1]:+.3f}]" if "diff_ci" in v else ""))
    return {"n_pos": int(y.sum()), "n_neg": int((1 - y).sum()), "models": out}


def main():
    _, gt, rows = load("llm_v1")
    ev = json.load(open(ROOT / "results" / "eval" / "llm_v1.json"))
    ct, slopes = common_trend(gt, rows)
    inc = incremental(gt, ev)
    (ROOT / "results" / "eval" / "llm_v1_diag.json").write_text(
        json.dumps({"common_trend_auroc": ct, "market_slopes": slopes, "incremental": inc}, indent=1))


if __name__ == "__main__":
    main()
