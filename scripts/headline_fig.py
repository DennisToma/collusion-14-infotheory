"""Figure 1 (headline, one glance): (a) scripted locked test — flag rate of raw MI vs pCMI on hard negatives and
collusion; (b) LLM markets — run AUROC of pCMI vs level statistics. Reads results/eval/*.json only.

    uv run python scripts/headline_fig.py    # -> figures/headline.png
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EV = ROOT / "results" / "eval"

GROUPS = [("A", "independent"), ("B", "common\nshock"), ("A+shared_policy", "shared\npolicy"),
          ("B+shared_policy", "shared policy\n+ shock"), ("A+shared_seed", "shared policy\n+ shared seed"),
          ("C", "COLLUSION"), ("D", "COLLUSION\n+ shock")]


def main():
    gate = json.load(open(EV / "gate_test.json"))["metrics"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.2), gridspec_kw={"width_ratios": [1.35, 1]})

    w = 0.38
    for j, (det, lab, col) in enumerate([("mi", "raw MI", "#9aa5b8"), ("pcmi", "pCMI (conditioned)", "#1f4e9c")]):
        for i, (g, _) in enumerate(GROUPS):
            m = gate[det][g]
            r, (lo, hi) = m["flag_rate"], m["flag_ci"]
            ax1.bar(i + (j - 0.5) * w, r, w, color=col, label=lab if i == 0 else None)
            ax1.errorbar(i + (j - 0.5) * w, r, yerr=[[r - lo], [hi - r]], color="k", capsize=2, lw=0.8)
    ax1.axhline(0.05, color="k", ls="--", lw=0.8)
    ax1.axvspan(4.5, 6.5, color="#f2d7d5", alpha=0.5, zorder=0)
    ax1.set_xticks(range(len(GROUPS)), [l for _, l in GROUPS], fontsize=8)
    ax1.set_ylim(0, 1.08)
    ax1.set_ylabel("markets flagged (α=0.05, shift null)\n[Wilson 95% CI]")
    ax1.set_title("(a) Scripted sellers, locked test (T=100, 50 markets/group)", fontsize=10)
    ax1.legend(fontsize=8, loc="upper left")

    v1 = json.load(open(EV / "llm_v1.json"))["by_T"]["20"]
    lg = json.load(open(EV / "llm_long.json"))["by_T"]["50"]
    v3 = json.load(open(EV / "llm_v3_ext.json"))["detectors"]
    sets = [("llm_v1\nT=20, C/D vs A/B", lambda d: (v1[d]["auroc_CD_vs_AB"], v1[d]["auroc_ci"])),
            ("llm_long\nT=50, C vs A", lambda d: (lg[d]["auroc_C_vs_A"], lg[d]["auroc_ci_C_vs_A"])),
            ("llm_v3 (sibling)\nT=12, private vs none",
             lambda d: (v3[d]["auroc_private_vs_none"]["auroc"], v3[d]["auroc_private_vs_none"]["ci"]))]
    dets = [("pcmi", "pCMI", "#1f4e9c"), ("pair_level", "pair price level", "#dd8452"),
            ("market_level", "markup over Nash", "#b04a1f")]
    w = 0.27
    for i, (_, get) in enumerate(sets):
        for j, (d, lab, col) in enumerate(dets):
            a, (lo, hi) = get(d)
            x = i + (j - 1) * w
            ax2.bar(x, a, w, color=col, label=lab if i == 0 else None)
            ax2.errorbar(x, a, yerr=[[a - lo], [hi - a]], color="k", capsize=2, lw=0.8)
    ax2.axhline(0.5, color="k", ls="--", lw=0.8)
    ax2.set_xticks(range(len(sets)), [s for s, _ in sets], fontsize=8)
    ax2.set_ylim(0, 1.08)
    ax2.set_ylabel("run AUROC, channel vs no-channel\n[bootstrap 95% CI]")
    ax2.set_title("(b) LLM sellers (gpt-6-luna): collusion is a price level", fontsize=10)
    ax2.legend(fontsize=8, loc="lower right")

    fig.tight_layout()
    fig.savefig(ROOT / "figures" / "headline.png", dpi=130)
    print("wrote figures/headline.png")


if __name__ == "__main__":
    main()
