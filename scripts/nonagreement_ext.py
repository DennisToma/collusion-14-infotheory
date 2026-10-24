"""E35 (exploratory, post-hoc): frozen detectors on sibling strata where the channel was OFFERED but the judge found
NO agreement: llm_v3mon (announced price monitor; 14 private + 6 none) and llm_v3fp (firm framing; 16 private, no controls).

Question: do level screens track the channel offer itself (E32 reading) or need an agreement? Same frozen E13 config
and scorer as scripts/placebo_rep_ext.py; nothing tuned. Decision rule declared in EXPERIMENTS.tsv (E35-nonagreement-declared).

    uv run python scripts/nonagreement_ext.py     # -> results/eval/nonagreement_ext.json (+ _report.md)
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
from placebo_rep_ext import DETS, NAMES, hit_prob, score_all  # noqa: E402


def top1(runs, grp, det, rng):
    h = np.array([hit_prob(runs[r]["scores"], det, runs[r]["pair"]) for r in grp])
    ph = np.array([[hit_prob(runs[r]["scores"], det, p) for p in PAIR_NAMES] for r in grp])
    null = ph[np.arange(len(grp)), rng.integers(0, 6, (20000, len(grp)))].sum(1)
    return {"hits": float(h.sum()), "n": len(h), "p_vs_1/6": float((1 + (null >= h.sum() - 1e-9).sum()) / (1 + len(null)))}


def main(B=50):
    orig, src, z = it._design, ext.SRC, ext._Z["lev"]
    it._design = ext._design_numeric
    try:
        mon, fp = score_all("llm_v3mon", B), score_all("llm_v3fp", B)
    finally:  # restore module state
        it._design, ext.SRC, ext._Z["lev"] = orig, src, z
    runs = {**mon, **fp}
    mon_priv = sorted(r for r in mon if mon[r]["cond"] == "private")
    mon_none = sorted(r for r in mon if mon[r]["cond"] == "none")
    fp_priv = sorted(r for r in fp if fp[r]["cond"] == "private")
    rng = np.random.default_rng(1)
    res = {"n": {"mon_private": len(mon_priv), "mon_none": len(mon_none), "fp_private": len(fp_priv)}, "B": B,
           "bonferroni_alpha": 0.05 / len(DETS), "detectors": {}}
    for det in DETS:
        d = {"top1_mon": top1(runs, mon_priv, det, rng), "top1_fp": top1(runs, fp_priv, det, rng),
             "top1_pooled": top1(runs, mon_priv + fp_priv, det, rng)}
        mx = {r: max(runs[r]["scores"][p][det] for p in PAIR_NAMES) for r in mon}
        a, ci = auroc_ci([mx[r] for r in mon_priv], [mx[r] for r in mon_none])
        d["auroc_mon_private_vs_none"] = {"auroc": a, "ci": ci, "n": [len(mon_priv), len(mon_none)]}
        # mean score of the offered pair minus mean of the other 5 pairs (descriptive)
        gap = [runs[r]["scores"][runs[r]["pair"]][det] - np.mean([runs[r]["scores"][p][det] for p in PAIR_NAMES
                                                                 if p != runs[r]["pair"]]) for r in mon_priv + fp_priv]
        d["offered_minus_other_pairs_mean"] = float(np.mean(gap))
        res["detectors"][det] = d
    pl = res["detectors"]["pair_level"]["top1_pooled"]
    res["decision"] = ("supported" if pl["p_vs_1/6"] < res["bonferroni_alpha"] else
                       "contradicted" if pl["hits"] <= 30 / 6 + 2 else "inconclusive")
    res["per_pair_scores"] = [{"run_id": r, "pair": p, "detector": det, "score": runs[r]["scores"][p][det]}
                              for r in sorted(runs) for p in PAIR_NAMES for det in DETS]
    (ROOT / "results" / "eval" / "nonagreement_ext.json").write_text(json.dumps(res, indent=1))
    t = lambda x: f"{x['hits']:.1f}/{x['n']} (p={x['p_vs_1/6']:.2g})"
    L = [f"n = {res['n']}; decision (pair_level pooled, declared rule): {res['decision']}", "",
         "| detector | top-1 v3mon (monitor) | top-1 v3fp (firm) | top-1 pooled | AUROC v3mon private vs none |",
         "|---|---|---|---|---|"]
    for det in DETS:
        d = res["detectors"][det]
        x = d["auroc_mon_private_vs_none"]
        L.append(f"| {NAMES[det]} | {t(d['top1_mon'])} | {t(d['top1_fp'])} | {t(d['top1_pooled'])} | "
                 f"{x['auroc']:.2f} [{x['ci'][0]:.2f}, {x['ci'][1]:.2f}] |")
    (ROOT / "results" / "eval" / "nonagreement_ext_report.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
