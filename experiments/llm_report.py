"""Markdown tables + figures for an evaluated LLM dataset (numbers for REPORT §4.3 come from here).

    uv run python -m experiments.llm_report --name llm_v1        # needs results/eval/llm_v1.json (llm_eval eval)

Writes results/eval/<name>_report.md and figures/<name>_prices.png, figures/<name>_auroc.png,
figures/<name>_power_vs_T.png (only if the dataset has more than one T).
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from experiments.llm_eval import NASH, load  # noqa: E402
from experiments.scripted import wilson  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DETS = [("pearson", "|Pearson|"), ("mi", "MI"), ("cmi_state", "CMI | state"), ("pcmi", "pCMI (state+lags)"),
        ("te", "lagged CMI (TE)"), ("ni_pcmi", "pCMI, no-intercept"), ("pair_level", "pair price level (non-IT)"),
        ("market_level", "market price level (non-IT)")]
COND = {"A": "A no channel", "B": "B no channel + shocks", "C": "C pair channel", "D": "D pair channel + shocks"}


def fmt_ci(x, ci):
    return f"{x:.2f} [{ci[0]:.2f}, {ci[1]:.2f}]"


def label_table(gt):
    by = defaultdict(list)
    for g in gt.values():
        by[g["condition"]].append(g)
    lines = ["| condition | n | agreement verified | coordinated actions | realised collusion | tacit supra-competitive |",
             "|---|---|---|---|---|---|"]
    for c in sorted(by):
        gs = by[c]
        cells = []
        for key in ("agreement_verified", "coordinated_actions_verified", "realized_collusion", "tacit_supracompetitive"):
            vals = [g.get(key) for g in gs]
            known = [bool(v) for v in vals if v is not None]
            if not known:
                cells.append("—")
            else:
                k = sum(known)
                lo, hi = wilson(known)
                amb = len(vals) - len(known)
                cells.append(f"{k}/{len(known)} [{lo:.2f}, {hi:.2f}]" + (f" (+{amb} n/a)" if amb and c in "CD" else ""))
        lines.append(f"| {COND.get(c, c)} | {len(gs)} | " + " | ".join(cells) + " |")
    return lines


def detector_table(m, pre=""):
    lines = ["| detector | AUROC C/D vs A/B [95% CI] | shift-null flag C/D | shift-null flag A/B | surrogate flag C/D | top-1 pair (C/D realised) | binom p vs 1/6 |",
             "|---|---|---|---|---|---|---|"]
    for det, lab in DETS:
        md = m.get(det, {})
        au = md.get(pre + "auroc_CD_vs_AB")
        auc = fmt_ci(au, md[pre + "auroc_ci"]) if au is not None else "—"

        def rate(groups, key):
            num = den = 0
            for g in groups:
                dd = md.get(pre + g)
                if dd and key in dd:
                    num += dd[key] * dd["n"]; den += dd["n"]
            return f"{num / den:.2f} (n={den})" if den else "—"
        t1 = md.get(pre + "CD_realized", {})
        top = fmt_ci(t1["top1"], t1["top1_ci"]) + f" (n={t1['n']})" if "top1" in t1 else "—"
        bp = f"{t1['top1_binom_p_vs_1/6']:.3f}" if "top1" in t1 else "—"
        lines.append(f"| {lab.replace('|', '\\|')} | {auc} | {rate('CD', 'flag_rate')} | {rate('AB', 'flag_rate')} | "
                     f"{rate('CD', 'surrogate_flag_rate')} | {top} | {bp} |")
    return lines


def fig_prices(name, gt, rows):
    fig, axes = plt.subplots(1, 4, figsize=(16, 3.8), sharey=True)
    for ax, c in zip(axes, "ABCD"):
        rids = [r for r in rows if gt[r]["condition"] == c]
        if not rids:
            ax.set_visible(False); continue
        T = min(len(rows[r]) for r in rids)
        pair, riv, mk = [], [], []
        for r in rids:
            rs = rows[r][:T]
            P = np.array([[a["price"] for a in x["agents"]] for x in rs], float)
            ids = [a["id"] for a in rs[0]["agents"]]
            mk.append(P.mean(1))
            ax.plot(P.mean(1), color="0.8", lw=0.6)
            if gt[r].get("assigned_pair"):
                ix = [ids.index(a) for a in gt[r]["assigned_pair"]]
                pair.append(P[:, ix].mean(1)); riv.append(np.delete(P, ix, 1).mean(1))
        x = np.arange(T)
        if pair:
            ax.plot(x, np.mean(pair, 0), color="#d62728", lw=2, label="channel pair (mean)")
            ax.plot(x, np.mean(riv, 0), color="#1f77b4", lw=2, label="rivals (mean)")
        else:
            ax.plot(x, np.mean(mk, 0), color="k", lw=2, label="market (mean)")
        ax.axhline(NASH[6], color="k", ls="--", lw=0.8)
        ax.set_title(f"{COND[c]} (n={len(rids)})", fontsize=10); ax.set_xlabel("round")
        ax.legend(fontsize=7, loc="upper right")
    axes[0].set_ylabel("price (grey: per-run market mean)\ndashed: Nash at cost 6")
    fig.suptitle(f"{name}: LLM seller prices by condition")
    fig.tight_layout(); fig.savefig(ROOT / "figures" / f"{name}_prices.png", dpi=130); plt.close(fig)


def fig_auroc(name, m, T):
    fig, ax = plt.subplots(figsize=(8, 3.8))
    xs, labs = [], []
    for i, (det, lab) in enumerate(DETS):
        md = m.get(det, {})
        if "auroc_CD_vs_AB" not in md:
            continue
        a, (lo, hi) = md["auroc_CD_vs_AB"], md["auroc_ci"]
        col = "#7f7f7f" if det.endswith("_level") else "#d62728"
        ax.bar(len(xs), a, color=col, yerr=[[a - lo], [hi - a]], capsize=3)
        xs.append(len(xs)); labs.append(lab)
    ax.axhline(0.5, color="k", ls="--", lw=0.8)
    ax.set_xticks(xs); ax.set_xticklabels(labs, rotation=30, ha="right", fontsize=8)
    ax.set_ylim(0, 1); ax.set_ylabel("run-level AUROC, channel vs no channel")
    ax.set_title(f"{name}, T={T}: max-pair score separating C/D from A/B (red: info-theoretic, grey: price level)", fontsize=9)
    fig.tight_layout(); fig.savefig(ROOT / "figures" / f"{name}_auroc.png", dpi=130); plt.close(fig)


def fig_power(name, by_T):
    Ts = sorted(int(t) for t in by_T)
    if len(Ts) < 2:
        return False
    fig, ax = plt.subplots(figsize=(7, 3.8))
    for det, lab in DETS:
        ys = [by_T[str(t)].get(det, {}).get("auroc_CD_vs_AB", np.nan) for t in Ts]
        ax.plot(Ts, ys, "o-", label=lab, color="0.5" if det.endswith("_level") else None,
                ls=":" if det.endswith("_level") else "-")
    ax.axhline(0.5, color="k", ls="--", lw=0.8)
    ax.set_xlabel("rounds used (prefix of each game)"); ax.set_ylabel("AUROC C/D vs A/B")
    ax.legend(fontsize=7); ax.set_title(f"{name}: detectability vs T")
    fig.tight_layout(); fig.savefig(ROOT / "figures" / f"{name}_power_vs_T.png", dpi=130); plt.close(fig)
    return True


def main(name):
    _, gt, rows = load(name)
    ev = json.load(open(ROOT / "results" / "eval" / f"{name}.json"))
    by_T = ev["by_T"]
    Tmax = max(by_T, key=int)
    out = [f"# {name} — generated by `uv run python -m experiments.llm_report --name {name}`", "",
           "## Labels (Wilson 95% CI)", *label_table(gt), ""]
    pl = ev["price_level"]
    out += ["## Price level", f"- market mean price C/D {pl['market_mean_CD']:.2f} (n={pl['n_CD']}) vs A/B "
            f"{pl['market_mean_AB']:.2f} (n={pl['n_AB']}); diff {fmt_ci(pl['diff'], pl['diff_ci'])}, "
            f"Mann-Whitney one-sided p={pl['mannwhitney_p']:.3g}",
            f"- pair minus rivals (C/D): {fmt_ci(pl['pair_minus_rivals_CD'], pl['pair_minus_rivals_ci'])}", ""]
    for pre, title in (("", "all games (confirmatory)"), ("test:", "k>=6 subset (robustness)")):
        out += [f"## Detectors, T={Tmax}, {title}", *detector_table(by_T[Tmax], pre), ""]
    if len(by_T) > 1:
        out += ["## AUROC vs T (all games)", "| T | " + " | ".join(l.replace("|", "\\|") for _, l in DETS) + " |",
                "|---" * (len(DETS) + 1) + "|"]
        for t in sorted(by_T, key=int):
            out.append(f"| {t} | " + " | ".join(f"{by_T[t].get(d, {}).get('auroc_CD_vs_AB', float('nan')):.2f}"
                                                 for d, _ in DETS) + " |")
    (ROOT / "results" / "eval" / f"{name}_report.md").write_text("\n".join(out) + "\n")
    print("\n".join(out))
    fig_prices(name, gt, rows)
    fig_auroc(name, by_T[Tmax], Tmax)
    fig_power(name, by_T)
    print("wrote figures for", name)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    main(ap.parse_args().name)
