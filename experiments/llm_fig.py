"""Directive-3 figure: run AUROC [95% CI] of dependence detectors vs level baselines on both LLM datasets.

    uv run python -m experiments.llm_fig     # -> figures/llm_auroc_both.png (llm_v1 panel only if its eval exists)
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DETS = [("pcmi", "pCMI"), ("mi", "MI"), ("te", "TE"), ("pearson", "|Pearson|"),
        ("pair_level", "pair level"), ("market_level", "markup/Nash")]
IT = {"pcmi", "mi", "te", "pearson"}


def panels():
    out = []
    p = ROOT / "results" / "eval" / "llm_v1.json"
    if p.exists():
        ev = json.load(open(p))
        T = max(ev["by_T"], key=int)
        m = ev["by_T"][T]
        out.append((f"llm_v1 (this repo), T={T}: C/D vs A/B",
                    [(m[d]["auroc_CD_vs_AB"], m[d]["auroc_ci"]) if "auroc_CD_vs_AB" in m.get(d, {}) else None for d, _ in DETS]))
    p = ROOT / "results" / "eval" / "llm_v3_ext.json"
    if p.exists():
        ev = json.load(open(p))
        g = ev["group_n"]
        out.append((f"llm_v3 (Q2.2 market), T=12: private ({g['private']}) vs none ({g['none']})",
                    [(ev["detectors"][d]["auroc_private_vs_none"]["auroc"], ev["detectors"][d]["auroc_private_vs_none"]["ci"])
                     for d, _ in DETS]))
    return out


def main():
    ps = panels()
    fig, axes = plt.subplots(1, len(ps), figsize=(5.5 * len(ps), 3.8), sharey=True, squeeze=False)
    for ax, (title, vals) in zip(axes[0], ps):
        for k, ((d, lab), v) in enumerate(zip(DETS, vals)):
            if v is None:
                continue
            a, (lo, hi) = v
            ax.bar(k, a, color="#4c72b0" if d in IT else "#dd8452")
            ax.errorbar(k, a, yerr=[[a - lo], [hi - a]], color="k", capsize=3, lw=1)
        ax.axhline(0.5, color="k", ls="--", lw=0.8)
        ax.set_xticks(range(len(DETS)), [l for _, l in DETS], rotation=30, fontsize=8)
        ax.set_ylim(0, 1.05); ax.set_title(title, fontsize=9)
    axes[0][0].set_ylabel("run AUROC [95% bootstrap CI]\nblue: dependence, orange: level")
    fig.tight_layout()
    fig.savefig(ROOT / "figures" / "llm_auroc_both.png", dpi=130)
    print("wrote figures/llm_auroc_both.png with", len(ps), "panel(s)")


if __name__ == "__main__":
    main()
