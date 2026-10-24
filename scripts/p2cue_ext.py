"""E57 (exploratory, no new calls): frozen detectors on the sibling's six matched channel arms (llm_p2cue).

Arms (15 matched seeds each, gpt-6-luna, T=12): private, neutral (delivered message box, no "private" wording),
notes (undelivered notepad), placebo (undelivered), randpartner (all firms, random re-matching), none.
Frozen E13 configuration (numeric-state pCMI/TE, Nash markup), same tables as E32 (scripts/placebo_rep_ext.py).
    uv run python scripts/p2cue_ext.py     # -> results/eval/p2cue_ext.{json,md}
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import detectors.infotheory as it  # noqa: E402
import experiments.ext_llm_v3 as ext  # noqa: E402
from detectors.infotheory import PAIR_NAMES  # noqa: E402
from experiments.llm_eval import auroc_ci  # noqa: E402
from placebo_rep_ext import NAMES, hit_prob, score_all  # noqa: E402

DETS = ["pcmi", "te", "mi", "pair_level", "market_level"]
ARMS = ["private", "neutral", "notes", "placebo", "randpartner"]


def main(B=50):
    orig, src, z = it._design, ext.SRC, ext._Z["lev"]
    it._design = ext._design_numeric
    try:
        runs = score_all("llm_p2cue", B)
    finally:
        it._design, ext.SRC, ext._Z["lev"] = orig, src, z
    lab = {g["run_id"]: g for g in map(json.loads, open(ROOT / "data" / "ext_llm_p2cue" / "labels.jsonl"))}
    by = {c: sorted([r for r in runs if runs[r]["cond"] == c], key=lambda r: runs[r]["seed"]) for c in ARMS + ["none"]}
    seed_of = {c: {runs[r]["seed"]: r for r in by[c]} for c in by}
    rng, rng_null = np.random.default_rng(0), np.random.default_rng(1)
    res = {"n": {c: len(v) for c, v in by.items()}, "B": B, "agreement_rate": {}, "detectors": {}}
    for c in by:
        ys = [lab[r]["y"] for r in by[c] if r in lab]
        res["agreement_rate"][c] = [int(sum(ys)), len(ys)]
    mx_all = {det: {r: max(runs[r]["scores"][p][det] for p in PAIR_NAMES) for r in runs} for det in DETS}
    for det in DETS:
        d, mx = {}, mx_all[det]
        for c in ARMS:
            grp = by[c]
            h = np.array([hit_prob(runs[r]["scores"], det, runs[r]["pair"]) for r in grp])
            ph = np.array([[hit_prob(runs[r]["scores"], det, p) for p in PAIR_NAMES] for r in grp])
            null = ph[np.arange(len(grp)), rng_null.integers(0, 6, (20000, len(grp)))].sum(1)
            a, ci = auroc_ci([mx[r] for r in grp], [mx[r] for r in by["none"]])
            d[c] = {"top1_hits": float(h.sum()), "n": len(grp),
                    "top1_p_vs_1/6": float((1 + (null >= h.sum() - 1e-9).sum()) / (1 + len(null))),
                    "auroc_vs_none": a, "auroc_vs_none_ci": ci}
            if c != "private":  # private vs arm on matched seeds, paired bootstrap of AUROC over seeds
                common = sorted(set(seed_of["private"]) & set(seed_of[c]))
                va = np.array([mx[seed_of["private"][s]] for s in common])
                vb = np.array([mx[seed_of[c][s]] for s in common])
                auc = lambda x, y: float(((x[:, None] > y[None]) + 0.5 * (x[:, None] == y[None])).mean())
                bs = [auc(va[i], vb[i]) for i in (rng.integers(0, len(va), len(va)) for _ in range(2000))]
                d[c]["auroc_private_vs_arm"] = auc(va, vb)
                d[c]["auroc_private_vs_arm_ci"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
        res["detectors"][det] = d
    # market markup over Nash (mean over all four firms), arm minus none, matched seeds, seed bootstrap
    mk = {r: float(np.mean([runs[r]["scores"][p]["market_level"] for p in PAIR_NAMES])) for r in runs}
    res["market_markup"] = {}
    for c in ARMS:
        common = sorted(set(seed_of["none"]) & set(seed_of[c]))
        dd = np.array([mk[seed_of[c][s]] - mk[seed_of["none"][s]] for s in common])
        bs = [dd[rng.integers(0, len(dd), len(dd))].mean() for _ in range(5000)]
        res["market_markup"][c] = {"diff_vs_none": float(dd.mean()), "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], "n": len(dd)}
    (ROOT / "results" / "eval" / "p2cue_ext.json").write_text(json.dumps(res, indent=1))
    f = lambda a, ci: f"{a:.2f} [{ci[0]:.2f}, {ci[1]:.2f}]"
    L = [f"n = {res['n']}; judge agreement (y=1 / labelled) = {res['agreement_rate']}", "",
         "| detector | arm | top-1 assigned pair (chance 2.5/15; p) | AUROC max-pair score, arm vs none | AUROC private vs arm (matched seeds) |",
         "|---|---|---|---|---|"]
    for det in DETS:
        for c in ARMS:
            x = res["detectors"][det][c]
            pv = f(x["auroc_private_vs_arm"], x["auroc_private_vs_arm_ci"]) if "auroc_private_vs_arm" in x else "–"
            L.append(f"| {NAMES[det].replace('|', chr(92) + '|')} | {c} | {x['top1_hits']:.1f}/{x['n']} (p={x['top1_p_vs_1/6']:.2g}) | "
                     f"{f(x['auroc_vs_none'], x['auroc_vs_none_ci'])} | {pv} |")
    L.append("\nMarket markup over Nash, arm − none (matched seeds, seed bootstrap): "
             + "; ".join(f"{c} {v['diff_vs_none']:+.2f} [{v['ci'][0]:+.2f}, {v['ci'][1]:+.2f}]" for c, v in res["market_markup"].items()))
    (ROOT / "results" / "eval" / "p2cue_ext.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
