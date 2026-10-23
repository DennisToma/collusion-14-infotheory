"""Power sweeps on scripted data: detection vs collusion strength and vs number of rounds T.

Datasets are regenerated deterministically into /var/tmp (not committed); only metrics are saved.
    uv run python -m experiments.sweep --out results/sweeps/power.json --workers 3
"""
from __future__ import annotations

import argparse
import itertools
import json
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from detectors.infotheory import PAIR_NAMES, run_detectors
from experiments.scripted import DETS, evaluate, gen, load_gt

SCRATCH = Path("/var/tmp/c14_sweeps")
TYPES = ["signal", "tft", "fixed_high"]
STRENGTHS = [0.0, 0.1, 0.2, 0.3, 0.45, 0.6, 0.8]
TS = [10, 20, 50, 100, 200]
S_FOR_T, T_FOR_S = 0.3, 100


def one(cfg):
    typ, s, T, n, B, seed = cfg
    name = f"sw_{typ}_s{s:.2f}_T{T}_seed{seed}"
    gen(name, n, T, s, typ, seed, hard_negatives=False, root=SCRATCH)
    res = run_detectors(SCRATCH / name, B=B)
    m = evaluate(res, load_gt(name, root=SCRATCH))
    return {"type": typ, "strength": s, "T": T, "n_per_cond": n, "B": B, "seed": seed, "metrics": m}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/sweeps/power.json")
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--B", type=int, default=100)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--seed", type=int, default=100)
    a = ap.parse_args()
    cfgs = [(t, s, T_FOR_S, a.n, a.B, a.seed) for t, s in itertools.product(TYPES, STRENGTHS)]
    cfgs += [(t, S_FOR_T, T, a.n, a.B, a.seed) for t, T in itertools.product(TYPES, TS) if T != T_FOR_S]
    with Pool(a.workers) as pool:
        rows = []
        for r in pool.imap_unordered(one, cfgs):
            rows.append(r)
            pc = r["metrics"]["pcmi"]
            print(r["type"], r["strength"], r["T"], "pcmi flag C/D",
                  pc["C"]["flag_rate"], pc["D"]["flag_rate"], "top1", pc["C"]["top1"], flush=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump({"args": vars(a), "rows": rows}, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
