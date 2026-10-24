"""Directive 1 (gap 2): per-round assigned-pair premium (pair mean - rivals' mean) in C games, and market markup over
the per-round Nash price in C and A games, with game-bootstrap 95% bands. Descriptive; no detector involved.
    uv run python scripts/premium_decay_fig.py --name llm_long_p2   # -> figures/premium_decay_<name>.png
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
NASH = {6: 10, 8: 12}


def load(name):
    gt = {g["run_id"]: g for g in map(json.loads, open(ROOT / "data" / name / "ground_truth.jsonl"))}
    rows = {}
    for line in open(ROOT / "data" / name / "trajectories.jsonl"):
        r = json.loads(line)
        rows.setdefault(r["run_id"], []).append(r)
    out = {"A": {"markup": []}, "C": {"markup": [], "premium": []}}
    T = min(len(v) for v in rows.values())
    for rid, rs in rows.items():
        c = gt[rid]["condition"]
        if c not in out:
            continue
        rs = sorted(rs, key=lambda r: r["round"])[:T]
        P = {a["id"]: [] for a in rs[0]["agents"]}
        for r in rs:
            for a in r["agents"]:
                P[a["id"]].append(a["price"])
        P = {k: np.array(v, float) for k, v in P.items()}
        nash = np.array([NASH[r["market"]["cost"]] for r in rs])
        out[c]["markup"].append(np.mean(list(P.values()), 0) - nash)
        if c == "C":
            pair = gt[rid]["assigned_pair"]
            riv = [k for k in P if k not in pair]
            out[c]["premium"].append(np.mean([P[k] for k in pair], 0) - np.mean([P[k] for k in riv], 0))
    return out, T


def band(X, B=2000, seed=0):
    X = np.asarray(X)
    rng = np.random.default_rng(seed)
    bs = np.array([X[rng.integers(0, len(X), len(X))].mean(0) for _ in range(B)])
    return X.mean(0), np.percentile(bs, 2.5, 0), np.percentile(bs, 97.5, 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="llm_long_p2")
    a = ap.parse_args()
    d, T = load(a.name)
    x = np.arange(1, T + 1)
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.6), sharex=True)
    for c, col in (("C", "#c0392b"), ("A", "#2c7fb8")):
        m, lo, hi = band(d[c]["markup"])
        ax[0].plot(x, m, color=col, label=f"{c} (n={len(d[c]['markup'])})")
        ax[0].fill_between(x, lo, hi, color=col, alpha=.2, lw=0)
    m, lo, hi = band(d["C"]["premium"])
    ax[1].plot(x, m, color="#c0392b")
    ax[1].fill_between(x, lo, hi, color="#c0392b", alpha=.2, lw=0)
    for k in ax:
        k.axhline(0, color="grey", lw=.8, ls="--")
        k.set_xlabel("round")
    ax[0].set_ylabel("market mean price − Nash")
    ax[0].set_title("market markup over Nash")
    ax[0].legend(frameon=False)
    ax[1].set_ylabel("pair mean − rivals' mean")
    ax[1].set_title("assigned-pair premium (C games)")
    fig.suptitle(f"{a.name}: per-round means, game-bootstrap 95% bands", fontsize=10)
    fig.tight_layout()
    out = ROOT / "figures" / f"premium_decay_{a.name}.png"
    fig.savefig(out, dpi=130)
    print(out)


if __name__ == "__main__":
    main()
