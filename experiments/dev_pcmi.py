"""DEV-split tuning of the pCMI design (see data/SPLITS.md: dev seeds only, never the locked test seed).

Compares residualisation designs ("lin" vs "inter" = + state x lag interactions) under the shift null,
plus a control-surrogate null (run-level max-pair score ranked against no-channel control runs of the
same shock condition, leave-one-out). Datasets go to /var/tmp; metrics to results/dev/.
    uv run python -m experiments.dev_pcmi --seed 11 --n 40 --T 100 50 --workers 2
"""
from __future__ import annotations

import argparse
import json
from multiprocessing import Pool
from pathlib import Path

import numpy as np

import detectors.infotheory as it
from experiments.scripted import evaluate, gen, load_gt, wilson

SCRATCH = Path("/var/tmp/c14_dev")
DEV_SEEDS = set(range(1, 100))  # locked test seeds are >= 1000 (data/SPLITS.md)


def surrogate_flags(res, gt, det, alpha=0.05):
    """Control-surrogate null: reference = max-pair scores of clean controls (A for A-family, B for B-family)."""
    mx = {r: max(res[r][n]["score"][det] for n in it.PAIR_NAMES) for r in res}
    ref = {fam: [r for r, g in gt.items() if g["condition"] == fam and g.get("hard_negative") in (None, "common_shock")]
           for fam in "AB"}
    out = {}
    for r, g in gt.items():
        fam = {"A": "A", "C": "A", "B": "B", "D": "B"}[g["condition"]]
        null = np.array([mx[q] for q in ref[fam] if q != r])
        out[r] = (1 + (null >= mx[r] - 1e-12).sum()) / (1 + len(null)) < alpha
    return out


def one(cfg):
    design, T, n, seed, B = cfg
    assert seed in DEV_SEEDS
    it.DESIGN = design
    name = f"dev_s{seed}_T{T}"
    if not (SCRATCH / name / "ground_truth.jsonl").exists():
        gen(name, n, T, 0.6, "signal", seed, hard_negatives=True, root=SCRATCH)
    gt = load_gt(name, root=SCRATCH)
    res = it.run_detectors(SCRATCH / name, B=B)
    m = evaluate(res, gt)
    rows = {}
    for det in ["pcmi", "te", "cmi_state"]:
        sf = surrogate_flags(res, gt, det)
        for key, d in m[det].items():
            if not isinstance(d, dict):
                continue
            rids = [r for r, g in gt.items() if (g["condition"] + ("" if g.get("hard_negative") in (None, "common_shock")
                                                                    else "+" + g["hard_negative"])) == key]
            f = [sf[r] for r in rids]
            rows.setdefault(det, {})[key] = {"shift": d.get("flag_rate"), "surrogate": float(np.mean(f)),
                                             "surrogate_ci": wilson(f), "top1": d.get("top1")}
    return {"design": design, "T": T, "n": n, "seed": seed, "B": B, "rows": rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--T", type=int, nargs="+", default=[100, 50])
    ap.add_argument("--B", type=int, default=200)
    ap.add_argument("--designs", nargs="+", default=["lin", "inter"])
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    for T in a.T:  # generate once, serially (avoid races)
        name = f"dev_s{a.seed}_T{T}"
        if not (SCRATCH / name / "ground_truth.jsonl").exists():
            gen(name, a.n, T, 0.6, "signal", a.seed, hard_negatives=True, root=SCRATCH)
    cfgs = [(d, T, a.n, a.seed, a.B) for d in a.designs for T in a.T]
    with Pool(a.workers) as pool:
        out = list(pool.imap_unordered(one, cfgs))
    for r in sorted(out, key=lambda r: (r["T"], r["design"])):
        print(f"== design={r['design']} T={r['T']}")
        for det, groups in r["rows"].items():
            print("  ", det, {k: (v["shift"], round(v["surrogate"], 2), v["top1"]) for k, v in groups.items()})
    p = Path(a.out or f"results/dev/pcmi_design_seed{a.seed}.json")
    p.parent.mkdir(parents=True, exist_ok=True)
    json.dump({"args": vars(a), "results": out}, open(p, "w"), indent=1)


if __name__ == "__main__":
    main()
