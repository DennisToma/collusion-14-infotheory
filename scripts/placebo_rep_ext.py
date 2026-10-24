"""E32 (exploratory, post-hoc): frozen detectors on the sibling's replication (llm_v3rep) and placebo (llm_v3plc) sets.

Placebo = same prompt and seed as a llm_v3rep `private` run, but private messages are never delivered.
Question: does the co-movement localisation seen in llm_v3 (E15) need *delivered* messages, whereas the
level premium does not? Frozen E13 configuration (numeric-state pCMI/TE, Nash markup); nothing tuned.

    uv run python scripts/placebo_rep_ext.py     # -> results/eval/placebo_rep_ext.json
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import detectors.infotheory as it  # noqa: E402
import experiments.ext_llm_v3 as ext  # noqa: E402
from detectors.infotheory import PAIR_NAMES, PAIRS, score_run  # noqa: E402
from experiments.diag_llm_v3 import VARIANTS  # noqa: E402
from experiments.llm_eval import auroc_ci  # noqa: E402

DETS = ["pcmi", "mi", "te", "pearson", "mi_diff", "pearson_diff1", "pair_level", "market_level"]
NAMES = {"pcmi": "pCMI (state+lags)", "mi": "MI (raw prices)", "te": "lagged CMI (TE)", "pearson": "|Pearson|",
         "mi_diff": "MI first differences", "pearson_diff1": "|Pearson| first differences",
         "pair_level": "pair_level (non-IT)", "market_level": "markup over Nash (non-IT)"}


def load(name):
    ext.SRC = ROOT / "data" / f"ext_{name}"
    return ext.load()


def score_all(name, B=50):
    gt, _, rows = load(name)
    out = {}
    for n, (rid, rs) in enumerate(sorted(rows.items())):
        P = np.array([[a["price"] for a in r["agents"]] for r in rs], float)
        st = [(r["market"]["cost"], r["market"]["demand_shock"]) for r in rs]
        lev = sorted(set(st))
        S = np.array([lev.index(s) for s in st])
        ext._Z["lev"] = np.array([[c, ext.DEM[d]] for c, d in lev], float)
        r = score_run(P, S, B=B, seed=n)
        ne = np.array([ext.nash(c, d) for c, d in st])
        sc = {}
        for (i, j), pn in zip(PAIRS, PAIR_NAMES):
            oth = [k for k in range(4) if k not in (i, j)]
            sc[pn] = {d: float(r[pn]["score"][d]) for d in ("pcmi", "mi", "te", "pearson")}
            sc[pn]["mi_diff"] = float(VARIANTS["MI first differences"](P, i, j))
            sc[pn]["pearson_diff1"] = float(VARIANTS["|Pearson| first differences"](P, i, j))
            sc[pn]["pair_level"] = float(P[:, [i, j]].mean() - P[:, oth].mean())
            sc[pn]["market_level"] = float((P[:, [i, j]] - ne[:, None]).mean())
        g = gt[rid]
        out[rid] = {"cond": g["condition"], "seed": g["seed"], "pair": "".join(sorted(g["assigned_pair"])), "scores": sc}
    return out


def hit_prob(sc, det, truth):
    """P(top-1 = truth) under uniform random tie-breaking (exact expectation, not sampled)."""
    v = {p: sc[p][det] for p in PAIR_NAMES}
    best = max(v.values())
    tied = [p for p in PAIR_NAMES if v[p] >= best - 1e-12]
    return (truth in tied) / len(tied)


def main(B=50):
    orig, src, z = it._design, ext.SRC, ext._Z["lev"]
    it._design = ext._design_numeric
    try:
        runs = {**score_all("llm_v3rep", B), **score_all("llm_v3plc", B)}
    finally:  # restore module state so later in-process evaluations are unaffected
        it._design, ext.SRC, ext._Z["lev"] = orig, src, z
    by = lambda c: sorted([r for r in runs if runs[r]["cond"] == c], key=lambda r: runs[r]["seed"])
    priv, plc, none, legit = by("private"), by("placebo"), by("none"), by("legit")
    seed2priv = {runs[r]["seed"]: r for r in priv}
    matched = [(seed2priv[runs[q]["seed"]], q) for q in plc if runs[q]["seed"] in seed2priv]
    rng, rng_null = np.random.default_rng(0), np.random.default_rng(1)
    res = {"n": {"private": len(priv), "placebo": len(plc), "none": len(none), "legit": len(legit),
                 "matched_pairs": len(matched)}, "B": B, "detectors": {}}
    for det in DETS:
        d = {}
        for tag, grp in (("private", priv), ("placebo", plc), ("legit", legit)):
            h = np.array([hit_prob(runs[r]["scores"], det, runs[r]["pair"]) for r in grp])
            # pair-label randomisation null for the fractional (tie-averaged) hit count: truth uniform over 6 pairs
            ph = np.array([[hit_prob(runs[r]["scores"], det, p) for p in PAIR_NAMES] for r in grp])
            null = ph[np.arange(len(grp)), rng_null.integers(0, 6, (20000, len(grp)))].sum(1)
            d[f"top1_{tag}"] = {"hits": float(h.sum()), "n": len(h),
                                "p_vs_1/6": float((1 + (null >= h.sum() - 1e-9).sum()) / (1 + len(null)))}
        dh = np.array([hit_prob(runs[a]["scores"], det, runs[a]["pair"]) - hit_prob(runs[b]["scores"], det, runs[b]["pair"])
                       for a, b in matched])
        bs = [dh[rng.integers(0, len(dh), len(dh))].mean() for _ in range(2000)]
        flips = np.array(list(itertools.product([1, -1], repeat=len(dh))))  # exact paired sign-flip test (2^15)
        p_sf = float((np.abs((flips * dh).mean(1)) >= abs(dh.mean()) - 1e-12).mean())
        d["top1_private_minus_placebo"] = {"diff": float(dh.mean()), "ci": [float(np.percentile(bs, 2.5)),
                                                                             float(np.percentile(bs, 97.5))],
                                           "p_signflip_exact": p_sf, "n_pos": int((dh > 0).sum()), "n_neg": int((dh < 0).sum())}
        mx = {r: max(runs[r]["scores"][p][det] for p in PAIR_NAMES) for r in runs}
        for tag, pos, neg in (("private_vs_none", priv, none), ("placebo_vs_none", plc, none)):
            a, ci = auroc_ci([mx[r] for r in pos], [mx[r] for r in neg])
            d[f"auroc_{tag}"] = {"auroc": a, "ci": ci, "n": [len(pos), len(neg)]}
        # private vs placebo: matched seeds -> resample seed pairs jointly
        va, vb = np.array([mx[a] for a, _ in matched]), np.array([mx[b] for _, b in matched])
        auc = lambda x, y: float(((x[:, None] > y[None]) + 0.5 * (x[:, None] == y[None])).mean())
        bsa = [auc(va[i], vb[i]) for i in (rng.integers(0, len(va), len(va)) for _ in range(2000))]
        d["auroc_private_vs_placebo"] = {"auroc": auc(va, vb), "ci": [float(np.percentile(bsa, 2.5)),
                                         float(np.percentile(bsa, 97.5))], "n": [len(va), len(vb)], "paired_bootstrap": True}
        res["detectors"][det] = d
    res["per_pair_scores"] = [{"run_id": r, "pair": p, "detector": det, "score": runs[r]["scores"][p][det]}
                              for r in sorted(runs) for p in PAIR_NAMES for det in DETS]
    (ROOT / "results" / "eval" / "placebo_rep_ext.json").write_text(json.dumps(res, indent=1))
    f = lambda x: f"{x['auroc']:.2f} [{x['ci'][0]:.2f}, {x['ci'][1]:.2f}]"
    L = [f"n = {res['n']}", "",
         "| detector | top-1 private | top-1 placebo | private − placebo (matched; bootstrap CI; exact sign-flip p) | AUROC private vs none | AUROC placebo vs none | AUROC private vs placebo |",
         "|---|---|---|---|---|---|---|"]
    for det in DETS:
        d = res["detectors"][det]
        t = lambda k: f"{d[k]['hits']:.1f}/{d[k]['n']} (p={d[k]['p_vs_1/6']:.2g})"
        m = d["top1_private_minus_placebo"]
        L.append(f"| {NAMES[det]} | {t('top1_private')} | {t('top1_placebo')} | {m['diff']:+.2f} [{m['ci'][0]:+.2f}, {m['ci'][1]:+.2f}]; p={m['p_signflip_exact']:.2g} | "
                 f"{f(d['auroc_private_vs_none'])} | {f(d['auroc_placebo_vs_none'])} | {f(d['auroc_private_vs_placebo'])} |")
    (ROOT / "results" / "eval" / "placebo_rep_ext_report.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
