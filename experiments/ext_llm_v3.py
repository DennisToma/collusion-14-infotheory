"""External-validity check (E13): frozen detectors on the sibling project's LLM market (Q2.2 `llm_v3`).

Read-only input: ../collusion-22-say-vs-do/data/llm_v3 (same SCHEMA; lab framing, price grid 6-30, T=12,
public board; conditions private / none / legit; legit = publicly announced shipping deal = hard negative).
No tuning. Two adaptations declared before computing (EXPERIMENTS.tsv E13), both forced by T=12:
  * pCMI/TE residualise on numeric state (cost, demand -1/0/1) instead of one dummy per state level
    (up to 12 levels in 11 usable rows would leave no residual);
  * market_level = pair markup over the static Nash of the round's state (bench() of the sibling sim).
The shift null needs T >= ~25, so here only scores are used: run AUROC (max-pair score), pair top-1
localisation vs 1/6, and the control-surrogate null against the `none` runs (pool >= 20 -> can reach 0.05).

    uv run python -m experiments.ext_llm_v3            # -> results/eval/llm_v3_ext.json
"""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import binomtest
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import detectors.infotheory as it  # noqa: E402
from detectors.infotheory import PAIR_NAMES, PAIRS, score_run  # noqa: E402
from experiments.llm_eval import auroc_ci  # noqa: E402
from experiments.scripted import wilson  # noqa: E402

SRC = ROOT.parent / "collusion-22-say-vs-do" / "data" / "llm_v3"
DETS = ["pearson", "pearson_diff", "mi", "cmi_state", "pcmi", "te", "pair_level", "market_level"]
DEM = {"low": -1, "normal": 0, "high": 1}

# --- sibling market (llm_market.py, sim llm-0.3): logit demand, static Nash per state -------------------
PMIN, PMAX, A_Q, MU = 6, 30, 16.0, 4.0
SIZE = {"low": 80, "normal": 100, "high": 130}


def _profit(ps, cost, shock):
    ex = [math.exp((A_Q - p) / MU) for p in ps]
    den = sum(ex) + 1.0
    return [(p - cost) * SIZE[shock] * e / den for p, e in zip(ps, ex)]


def nash(cost, shock, _c={}):
    if (cost, shock) not in _c:
        P = range(PMIN, PMAX + 1)
        ne = [p for p in P if max(P, key=lambda q: _profit([q, p, p, p], cost, shock)[0]) == p]
        _c[cost, shock] = float(np.mean(ne))
    return _c[cost, shock]


# --- numeric-state design (declared adaptation) -----------------------------------------------------
_Z = {"lev": None}


def _design_numeric(S, P, t_idx, exclude_lag=None, design=None):
    Z = _Z["lev"][S[t_idx]]
    lags = [P[t_idx - 1, k] for k in range(P.shape[1]) if k != exclude_lag]
    cols = [np.ones(len(t_idx))] + [Z[:, 0], Z[:, 1]] + lags
    X = np.column_stack(cols)
    return X[:, np.r_[0, 1 + np.flatnonzero(X[:, 1:3].std(0) > 0), 3:X.shape[1]]]  # drop constant state cols




def load():
    gt = {g["run_id"]: g for g in map(json.loads, open(SRC / "ground_truth.jsonl"))}
    lab = {g["run_id"]: g for g in map(json.loads, open(SRC / "labels.jsonl"))} if (SRC / "labels.jsonl").exists() else {}
    rows = defaultdict(list)
    for line in open(SRC / "trajectories.jsonl"):
        r = json.loads(line)
        rows[r["run_id"]].append(r)
    for v in rows.values():
        v.sort(key=lambda r: r["round"])
    return gt, lab, {k: v for k, v in rows.items() if k in gt and len(v) == gt[k]["rounds"]}


def split_of(rid):  # sibling data/SPLITS.md: 0000-0029 dev, 0030-0124 locked test (theirs; we tune nothing)
    return "dev" if int(rid.rsplit("_", 1)[1]) <= 29 else "test"


def top1(scores, truth, rng):
    """Top-1 pair with uniform random tie-breaking (ties are common at T=12: constant sellers)."""
    best = max(scores.values())
    tied = [p for p in PAIR_NAMES if scores[p] >= best - 1e-12]
    return rng.choice(tied) == truth, len(tied) > 1


def main(B=50):
    orig = it._design
    it._design = _design_numeric  # scoped: restored below so other evaluations in-process are unaffected
    try:
        _main(B)
    finally:
        it._design = orig


def _main(B):
    gt, lab, rows = load()
    per_pair, res = [], {}
    for n, (rid, rs) in enumerate(sorted(rows.items())):
        P = np.array([[a["price"] for a in r["agents"]] for r in rs], float)
        st = [(r["market"]["cost"], r["market"]["demand_shock"]) for r in rs]
        lev = sorted(set(st))
        S = np.array([lev.index(s) for s in st])
        _Z["lev"] = np.array([[c, DEM[d]] for c, d in lev], float)
        r = score_run(P, S, B=B, seed=n)
        ne = np.array([nash(c, d) for c, d in st])
        for (i, j), pn in zip(PAIRS, PAIR_NAMES):
            oth = [k for k in range(4) if k not in (i, j)]
            r[pn]["score"]["pair_level"] = float(P[:, [i, j]].mean() - P[:, oth].mean())
            r[pn]["score"]["market_level"] = float((P[:, [i, j]] - ne[:, None]).mean())
            for det in DETS:
                per_pair.append({"run_id": rid, "pair": pn, "detector": det, "score": r[pn]["score"][det]})
        r["_flat"] = int((P.std(0) < 0.25).sum())
        res[rid] = r
    cond = {r: gt[r]["condition"] for r in res}
    # communication-only label (judge says explicit agreement) vs the sibling's explicit_collusion, which also
    # requires pair premium >= 1 -> price-selected, circular for the level baselines (reported separately)
    agree = {r: lab.get(r, {}).get("agreement") in ("explicit", "info_exchange") for r in res}
    expl = {r: bool(lab.get(r, {}).get("explicit_collusion")) for r in res}
    groups = {"private": [r for r in res if cond[r] == "private"],
              "private_agreement": [r for r in res if cond[r] == "private" and agree[r]],
              "private_explicit_price_selected": [r for r in res if cond[r] == "private" and expl[r]],
              "none": [r for r in res if cond[r] == "none"],
              "legit": [r for r in res if cond[r] == "legit"]}
    out = {"n_runs": len(res), "group_n": {k: len(v) for k, v in groups.items()},
           "labels_available": sum(r in lab for r in res), "B": B,
           "near_constant_sellers": sum(res[r]["_flat"] for r in res), "detectors": {}}
    for det in DETS:
        mx = {r: max(res[r][p]["score"][det] for p in PAIR_NAMES) for r in res}
        dd = {}
        for tag, pos, neg in (("private_vs_none", "private", "none"), ("agreement_vs_none", "private_agreement", "none"),
                              ("price_selected_vs_none", "private_explicit_price_selected", "none"),
                              ("legit_vs_none", "legit", "none"), ("private_vs_legit", "private", "legit")):
            for sp in ("all", "test"):
                ps = [r for r in groups[pos] if sp == "all" or split_of(r) == sp]
                ns = [r for r in groups[neg] if sp == "all" or split_of(r) == sp]
                if len(ps) >= 2 and len(ns) >= 2:
                    a, ci = auroc_ci([mx[r] for r in ps], [mx[r] for r in ns])
                    dd[f"auroc_{tag}" + ("" if sp == "all" else "_test")] = {"auroc": a, "ci": ci, "n": [len(ps), len(ns)]}
        for g in ("private", "private_agreement", "private_explicit_price_selected", "legit"):  # top-1 localisation
            rng = np.random.default_rng(1)
            tt = [top1({p: res[r][p]["score"][det] for p in PAIR_NAMES}, "".join(sorted(gt[r]["assigned_pair"])), rng)
                  for r in groups[g]]
            t1 = [bool(a) for a, _ in tt]
            if t1:
                dd[f"top1_{g}"] = {"rate": float(np.mean(t1)), "ci": wilson(t1), "k": int(sum(t1)), "n": len(t1),
                                   "n_tied_runs": int(sum(b for _, b in tt)),
                                   "binom_p_vs_1/6": float(binomtest(sum(t1), len(t1), 1 / 6, alternative="greater").pvalue)}
        pool = groups["none"]
        if len(pool) >= 20:  # control-surrogate null: rank vs no-channel runs (leave-one-out for controls)
            for g in ("private", "private_agreement", "legit", "none"):
                fl = []
                for r in groups[g]:
                    null = np.array([mx[q] for q in pool if q != r])
                    fl.append((1 + (null >= mx[r] - 1e-12).sum()) / (1 + len(null)) < 0.05)
                if fl:
                    dd[f"surrogate_flag_{g}"] = {"rate": float(np.mean(fl)), "ci": wilson(fl), "n": len(fl)}
        out["detectors"][det] = dd
    # paired bootstrap: does a dependence score add anything beyond the level baselines?
    rng = np.random.default_rng(0)
    pos, neg = groups["private"], groups["none"]
    if len(pos) >= 2 and len(neg) >= 2:
        y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
        idx = [np.r_[rng.integers(0, len(pos), len(pos)), len(pos) + rng.integers(0, len(neg), len(neg))] for _ in range(2000)]
        out["auroc_diff_private_vs_none"] = {}
        for a, b in (("pcmi", "pair_level"), ("pcmi", "market_level"), ("mi", "pair_level"), ("te", "pair_level"),
                     ("pair_level", "market_level")):
            va = np.array([max(res[r][p]["score"][a] for p in PAIR_NAMES) for r in pos + neg])
            vb = np.array([max(res[r][p]["score"][b] for p in PAIR_NAMES) for r in pos + neg])
            bs = [roc_auc_score(y[i], va[i]) - roc_auc_score(y[i], vb[i]) for i in idx]
            out["auroc_diff_private_vs_none"][f"{a}-{b}"] = {
                "diff": float(roc_auc_score(y, va) - roc_auc_score(y, vb)),
                "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]}
    out["per_pair_scores"] = per_pair
    (ROOT / "results" / "eval").mkdir(parents=True, exist_ok=True)
    json.dump(out, open(ROOT / "results" / "eval" / "llm_v3_ext.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "per_pair_scores" and k != "detectors"}, indent=1))
    write_table(out)
    for det, dd in out["detectors"].items():
        print(det, {k: (round(v.get("auroc", v.get("rate", 0)), 2), v.get("n")) for k, v in dd.items()})


def write_table(out):
    """Markdown table for REPORT §4.3 -> results/eval/llm_v3_ext_report.md."""
    lab = [("pcmi", "pCMI (state+lags)"), ("mi", "MI (raw prices)"), ("te", "lagged CMI (TE)"),
           ("pearson", "\\|Pearson\\|"), ("pair_level", "pair_level (non-IT)"), ("market_level", "markup over Nash (non-IT)")]
    g = out["group_n"]
    a = lambda d, k: f"{d[k]['auroc']:.2f} [{d[k]['ci'][0]:.2f}, {d[k]['ci'][1]:.2f}]" if k in d else "—"
    t = lambda d, k: (f"{d[k]['k']}/{d[k]['n']} (p={d[k]['binom_p_vs_1/6']:.2g}" +
                      (f", {d[k]['n_tied_runs']} tied" if d[k].get("n_tied_runs") else "") + ")") if k in d else "—"
    L = [f"n runs = {out['n_runs']} (private {g['private']}, of which judge-verified agreement {g['private_agreement']}; "
         f"none {g['none']}; legit {g['legit']})", "",
         f"| detector | AUROC private vs none | AUROC agreement vs none | AUROC legit vs none | top-1, private | top-1, agreement |",
         "|---|---|---|---|---|---|"]
    for det, name in lab:
        d = out["detectors"][det]
        L.append(f"| {name} | {a(d, 'auroc_private_vs_none')} | {a(d, 'auroc_agreement_vs_none')} | "
                 f"{a(d, 'auroc_legit_vs_none')} | {t(d, 'top1_private')} | {t(d, 'top1_private_agreement')} |")
    L += ["", "Paired-bootstrap AUROC differences (private vs none): " + "; ".join(
        f"{k} {v['diff']:+.2f} [{v['ci'][0]:+.2f}, {v['ci'][1]:+.2f}]" for k, v in out.get("auroc_diff_private_vs_none", {}).items())]
    sf = {det: out["detectors"][det].get("surrogate_flag_private") for det, _ in lab}
    if any(sf.values()):
        L += ["", "Control-surrogate null (vs none pool, α=0.05) flag rate, private / legit / none(LOO): " + "; ".join(
            f"{det} {out['detectors'][det]['surrogate_flag_private']['rate']:.2f} / "
            f"{out['detectors'][det]['surrogate_flag_legit']['rate']:.2f} / {out['detectors'][det]['surrogate_flag_none']['rate']:.2f}"
            for det, _ in lab if sf[det])]
    (ROOT / "results" / "eval" / "llm_v3_ext_report.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
