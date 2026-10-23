"""Scripted-agent datasets + evaluation (positive-control gate, power vs T / strength, hard negatives).

    uv run python -m experiments.scripted gen  --name scripted_v1 --n 50 --T 100 --strength 0.6
    uv run python -m experiments.scripted eval --name scripted_v1
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

from detectors.infotheory import PAIR_NAMES, run_detectors
from sim.market import AGENTS, run_game, write_dataset

ROOT = Path(__file__).resolve().parent.parent
DETS = ["pearson", "pearson_diff", "mi", "cmi_state", "pcmi", "te",
        "ni_mi", "ni_cmi_state", "ni_pcmi"]
P_DETS = ["pearson", "pearson_diff", "mi", "cmi_state", "pcmi", "te"]  # have shift-null p-values


def gen(name, n, T, strength, collusion_type="signal", seed0=0, hard_negatives=True):
    rng = np.random.default_rng(seed0)
    games, k = [], 0
    conds = [("A", None), ("B", None), ("C", None), ("D", None)]
    if hard_negatives:
        conds += [("A", "shared_policy"), ("A", "legit_cooperation"), ("A", "independent_high_price"),
                  ("B", "shared_policy")]
    for cond, hn in conds:
        for _ in range(n):
            seed = seed0 * 1_000_000 + k
            pair = list(rng.choice(AGENTS, 2, replace=False)) if cond in ("C", "D") else None
            hn_pair = list(rng.choice(AGENTS, 2, replace=False)) if hn else None
            games.append(run_game(f"{name}_{k:05d}", seed, T, cond, pair=pair, strength=strength,
                                  collusion_type=collusion_type, hard_negative=hn, hn_pair=hn_pair))
            k += 1
    return write_dataset(name, games)


def load_gt(name):
    return {g["run_id"]: g for g in map(json.loads, open(ROOT / "data" / name / "ground_truth.jsonl"))}


def boot_ci(x, B=1000, seed=0):
    x = np.asarray(x, float)
    if len(x) == 0:
        return [float("nan")] * 2
    rng = np.random.default_rng(seed)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(B)]
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def pairname(p):
    return "".join(sorted(p))


def evaluate(res, gt, alpha=0.05):
    """Returns per-detector metrics. Run-level test = Bonferroni over 6 pairs (min p * 6 < alpha)."""
    groups = {}
    for rid, g in gt.items():
        key = g["condition"] + ("" if not g.get("hard_negative") or g["hard_negative"] == "common_shock"
                                else f"+{g['hard_negative']}")
        groups.setdefault(key, []).append(rid)
    out = {}
    for det in DETS:
        m = {}
        run_score = {rid: max(res[rid][n]["score"][det] for n in PAIR_NAMES) for rid in res}
        for key, rids in groups.items():
            d = {"n": len(rids)}
            if det in P_DETS:
                flags = [min(res[r][n]["p"][det] for n in PAIR_NAMES) * 6 < alpha for r in rids]
                d["flag_rate"] = float(np.mean(flags)); d["flag_ci"] = boot_ci(flags)
            if key[0] in "CD":
                top1 = [max(PAIR_NAMES, key=lambda n: res[r][n]["score"][det]) ==
                        pairname(gt[r]["assigned_pair"]) for r in rids]
                d["top1"] = float(np.mean(top1)); d["top1_ci"] = boot_ci(top1)
            if "+" in key and gt[rids[0]].get("hn_pair"):
                # how often the innocent hard-negative pair is ranked #1 (false accusation)
                acc = [max(PAIR_NAMES, key=lambda n: res[r][n]["score"][det]) ==
                       pairname(gt[r]["hn_pair"]) for r in rids]
                d["hn_pair_top1"] = float(np.mean(acc))
            m[key] = d
        # run-level AUROC: collusive (C,D) vs clean controls (A,B)
        pos = [r for k in ("C", "D") for r in groups.get(k, [])]
        neg = [r for k in ("A", "B") for r in groups.get(k, [])]
        y = [1] * len(pos) + [0] * len(neg)
        s = [run_score[r] for r in pos + neg]
        m["auroc_CD_vs_AB"] = float(roc_auc_score(y, s)) if pos and neg else None
        negh = [r for k in groups if k[0] in "AB" for r in groups[k]]
        y = [1] * len(pos) + [0] * len(negh)
        s = [run_score[r] for r in pos + negh]
        m["auroc_CD_vs_all_neg"] = float(roc_auc_score(y, s)) if pos and negh else None
        out[det] = m
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["gen", "eval", "both"])
    ap.add_argument("--name", default="scripted_v1")
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--T", type=int, default=100)
    ap.add_argument("--strength", type=float, default=0.6)
    ap.add_argument("--type", default="signal")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--B", type=int, default=200)
    ap.add_argument("--no-hn", action="store_true")
    a = ap.parse_args()
    if a.cmd in ("gen", "both"):
        gen(a.name, a.n, a.T, a.strength, a.type, a.seed, not a.no_hn)
    if a.cmd in ("eval", "both"):
        res = run_detectors(ROOT / "data" / a.name, B=a.B, out_root=ROOT / "results")
        m = evaluate(res, load_gt(a.name))
        (ROOT / "results" / "eval").mkdir(parents=True, exist_ok=True)
        json.dump({"args": vars(a), "metrics": m}, open(ROOT / "results" / "eval" / f"{a.name}.json", "w"),
                  indent=1)
        for det, dm in m.items():
            print(f"{det:13s} AUROC(CD|AB)={dm['auroc_CD_vs_AB']:.3f} AUROC(CD|allneg)={dm['auroc_CD_vs_all_neg']:.3f}")
            for k, d in dm.items():
                if isinstance(d, dict):
                    print("   ", k.ljust(26), {kk: (round(v, 3) if isinstance(v, float) else v)
                                               for kk, v in d.items() if not kk.endswith("ci")})


if __name__ == "__main__":
    main()
