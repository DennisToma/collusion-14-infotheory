"""Figures from results/sweeps/power.json:  uv run python -m experiments.plot_sweeps"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DETS = [("pearson", "|Pearson|", "#9e9e9e"), ("mi", "MI", "#1f77b4"), ("cmi_state", "CMI | state", "#2ca02c"),
        ("pcmi", "CMI | state + lags (Gaussian)", "#d62728"), ("te", "lagged CMI (TE)", "#9467bd")]
TYPES = {"signal": "shared-signal collusion", "tft": "tit-for-tat price matching", "fixed_high": "independent 'stay high'"}


def main(path=ROOT / "results/sweeps/power.json"):
    rows = json.load(open(path))["rows"]
    for xkey, fixed, xlabel, fname in [("strength", ("T", 100), "collusion strength (prob. of coordinated play per round)", "power_vs_strength.png"),
                                       ("T", ("strength", 0.3), "rounds T", "power_vs_T.png")]:
        fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=True)
        for ax, (typ, title) in zip(axes, TYPES.items()):
            sub = sorted([r for r in rows if r["type"] == typ and r[fixed[0]] == fixed[1]], key=lambda r: r[xkey])
            xs = [r[xkey] for r in sub]
            for det, lab, col in DETS:
                ys = [(r["metrics"][det]["C"]["flag_rate"] + r["metrics"][det]["D"]["flag_rate"]) / 2 for r in sub]
                fp = [(r["metrics"][det]["A"]["flag_rate"] + r["metrics"][det]["B"]["flag_rate"]) / 2 for r in sub]
                ax.plot(xs, ys, "o-", color=col, label=lab)
                ax.plot(xs, fp, ":", color=col, alpha=0.6)
            ax.axhline(0.05, color="k", lw=0.8, ls="--")
            ax.set_title(title); ax.set_xlabel(xlabel)
            if xkey == "T":
                ax.set_xscale("log")
        axes[0].set_ylabel("run-level detection rate at α=0.05\n(solid: collusive C/D, dotted: controls A/B)")
        axes[-1].legend(fontsize=8, loc="center right")
        fig.suptitle(f"Scripted market: power vs {xkey} ({fixed[0]}={fixed[1]}, n=20 runs per condition)")
        fig.tight_layout(); fig.savefig(ROOT / "figures" / fname, dpi=130); plt.close(fig)
        print("wrote", fname)


if __name__ == "__main__":
    main()


def hard_negatives(name="gate_s06_T100"):
    """Bar chart of run-level flag rate per condition / hard negative for each detector."""
    import numpy as np
    m = json.load(open(ROOT / "results/eval" / f"{name}.json"))["metrics"]
    groups = ["A", "B", "A+independent_high_price", "A+legit_cooperation", "A+shared_policy",
              "B+shared_policy", "C", "D"]
    labels = ["A indep.", "B common shock", "indep. high-price", "leader-follower", "shared policy",
              "shared policy\n+ common shock", "C collusion", "D collusion\n+ common shock"]
    fig, ax = plt.subplots(figsize=(13, 4.2))
    w = 0.8 / len(DETS)
    for k, (det, lab, col) in enumerate(DETS):
        ys = [m[det][g]["flag_rate"] for g in groups]
        lo = [ys[i] - m[det][g]["flag_ci"][0] for i, g in enumerate(groups)]
        hi = [m[det][g]["flag_ci"][1] - ys[i] for i, g in enumerate(groups)]
        ax.bar(np.arange(len(groups)) + (k - 2) * w, ys, w, yerr=[lo, hi], color=col, label=lab, capsize=2)
    ax.axhline(0.05, color="k", lw=0.8, ls="--")
    ax.axvline(5.5, color="k", lw=0.6)
    ax.set_xticks(range(len(groups))); ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("runs flagged at α=0.05"); ax.legend(fontsize=7, ncol=5, loc="upper left")
    ax.set_title("Scripted market, T=100, strength 0.6 (n=%d runs/group): left of line = no collusion" %
                 m["pcmi"]["A"]["n"])
    fig.tight_layout(); fig.savefig(ROOT / "figures" / "hard_negatives.png", dpi=130); plt.close(fig)
    print("wrote hard_negatives.png")


if __name__ == "__main__":
    hard_negatives()
