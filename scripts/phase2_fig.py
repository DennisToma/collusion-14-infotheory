"""Nine-set Phase 2 overview; saved estimates only, no analysis or LLM calls.

uv run python scripts/phase2_fig.py -> figures/phase2_headline.png
The inclusion list is the frozen P2.13 main group (>=10 games per arm).
Intervals come from p2_partc.json; no cross-set meta-analysis is implied.
"""
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
BLUE, ORANGE, INK = "#2a78d6", "#d86226", "#23334b"


def main():
    ev = ROOT / "results/eval"
    claims = json.loads((ev / "claims_denominators.json").read_text())
    partc = json.loads((ev / "p2_partc.json").read_text())
    ss = [s for s in claims["sets"] if s["group"] == "main"]
    rows = [partc[s["set"]] for s in ss]
    labels = [f"{r['label']}\nT={r['T']}; n={r['n_A']} + {r['n_C']}" for r in rows]
    claim = {c["claim"]: c for c in claims["claims"] if c["group"] == "main"}
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 7.6), sharey=True,
                                   gridspec_kw={"width_ratios": [1, 1.25]})
    y = np.arange(len(rows))
    for i, r in enumerate(rows):
        ax1.plot(r["C_minus_A_ci"], [i, i], color=INK, lw=2)
        ax1.plot(r["C_minus_A_markup"], i, "o", color=INK, ms=6)
        for metric, offset, color, marker in (("market_level", -.13, BLUE, "o"),
                                              ("pcmi", .13, ORANGE, "s")):
            ax2.plot(r[f"auroc_{metric}_ci"], [i + offset] * 2, color=color, lw=1.8)
            ax2.plot(r[f"auroc_{metric}"], i + offset, marker, color=color, ms=6,
                     label={"market_level": "Market-level markup", "pcmi": "pCMI"}[metric] if i == 0 else None)
        if i % 2 == 0:
            for ax in (ax1, ax2):
                ax.axhspan(i - .48, i + .48, color="#f3f6fa", zorder=-1)
    ax1.axvline(0, color="#8996a8", ls="--", lw=1)
    ax2.axvline(.5, color="#8996a8", ls="--", lw=1)
    ax1.set_yticks(y, labels, fontsize=9)
    ax1.set_ylim(len(rows) - .5, -.5)
    ax1.set_xlabel("Channel − no-channel markup [95% CI]")
    ax2.set_xlabel("Run AUROC [95% CI]; 0.5 = chance")
    ax2.set_xlim(0, 1.02)
    ax1.set_title(f"(a) Positive channel effect: {claim['premium']['k']}/{claim['premium']['K']} sets",
                  fontsize=11, loc="left", pad=13)
    ax2.set_title(f"(b) Level beats pCMI: {claim['level_beats_pcmi']['k']}/{claim['level_beats_pcmi']['K']} sets",
                  fontsize=11, loc="left", pad=13)
    ax2.legend(loc="lower left", bbox_to_anchor=(0, 1.045), ncol=2, frameon=False, fontsize=9)
    for ax in (ax1, ax2):
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0)
        ax.grid(axis="x", color="#dce3ed", lw=.7)
        ax.set_axisbelow(True)
    fig.text(.02, .035, "Frozen P2.13 main sets; channel assignment is the target, not verified execution. "
             "Sets share designs/models; these are not nine independent replications.\n"
             "Base Qwen3.6 is the pCMI exception. Executed-only and strong-framing results are reported separately (P2.11).",
             fontsize=8.5, color=INK)
    fig.subplots_adjust(left=.32, right=.98, bottom=.13, top=.9, wspace=.16)
    out = ROOT / "figures/phase2_headline.png"
    fig.savefig(out, dpi=160, facecolor="white")
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    main()
