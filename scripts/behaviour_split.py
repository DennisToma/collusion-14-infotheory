"""E56 (exploratory; cross-pollination from Q2.2 E84): split channel (C) games by BEHAVIOUR, not condition.

Uses the existing gpt-6.1-sol judge labels (results/llm_judge/<name>.jsonl: agreement, agreed_price, first_round; produced by
`experiments.llm_eval label`, blind to nothing new). Classes per C game:
  followed     agreement and, over rounds after the agreement (pre-play = all rounds), both pair firms price >= agreed - 1
               in at least half of them (the Q2.2 E84 rule)
  abandoned    agreement, not followed
  no_agreement no agreement extracted (or ambiguous)
Per class: assigned-pair premium (NOTE: assigned-pair C scores vs max-of-6-pairs A scores is conservative and depresses
the AUROCs; the class means are the comparable quantities) (pair mean - rival mean), assigned-pair markup over Nash, assigned-pair pCMI, and AUROC of each
against the max-pair score of the A controls of the same dataset (frozen detectors, score_run B=0). Descriptive only.

    uv run python scripts/behaviour_split.py [--names llm_v1,llm_long,llm_long_p2] [--T 20]   # -> results/eval/behaviour_split.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from detectors.infotheory import PAIR_NAMES, PAIRS, score_run  # noqa: E402
from experiments.llm_eval import NASH, arrays, load  # noqa: E402


def auc(pos, neg):
    if not len(pos) or not len(neg):
        return None
    pos, neg = np.asarray(pos)[:, None], np.asarray(neg)[None, :]
    return round(float(np.mean((pos > neg) + 0.5 * (pos == neg))), 3)


def pair_stats(P, S, nash, i, j):
    r = score_run(P, S, B=0)
    pn = PAIR_NAMES[PAIRS.index((i, j))]
    others = [k for k in range(4) if k not in (i, j)]
    return {"premium": float(P[:, [i, j]].mean() - P[:, others].mean()),
            "markup": float((P[:, [i, j]] - nash[:, None]).mean()), "pcmi": r[pn]["score"]["pcmi"]}


def max_pair(P, S, nash):
    r = score_run(P, S, B=0)
    best = {"premium": -1e9, "markup": -1e9, "pcmi": max(r[n]["score"]["pcmi"] for n in PAIR_NAMES)}
    for i, j in PAIRS:
        others = [k for k in range(4) if k not in (i, j)]
        best["premium"] = max(best["premium"], float(P[:, [i, j]].mean() - P[:, others].mean()))
        best["markup"] = max(best["markup"], float((P[:, [i, j]] - nash[:, None]).mean()))
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--names", default="llm_v1,llm_long")
    ap.add_argument("--T", type=int, default=0, help="prefix length (0 = full game)")
    a = ap.parse_args()
    res = {}
    for name in a.names.split(","):
        jp = ROOT / "results" / "llm_judge" / f"{name}.jsonl"
        if not jp.exists():
            print(f"{name}: no judge labels, skipped")
            continue
        lab = {j["run_id"]: j for j in map(json.loads, open(jp))}
        _, gt, rows = load(name)
        cls, ctrl = {}, []
        for rid in sorted(gt):
            rs = rows[rid][:a.T] if a.T else rows[rid]
            P, S, ids = arrays(rs)
            nash = np.array([NASH[r["market"]["cost"]] for r in rs], float)
            if gt[rid]["condition"] == "A":
                ctrl.append(max_pair(P, S, nash))
                continue
            if gt[rid]["condition"] != "C":
                continue
            i, j = sorted(ids.index(x) for x in gt[rid]["assigned_pair"])
            lb = lab.get(rid, {})
            if lb.get("agreement") == "yes" and lb.get("agreed_price") is not None:
                # rounds are 0-indexed; a message in round k first affects round k+1 prices; pre-play (-1) -> all rounds
                fr = lb.get("first_round")
                start = max(int(fr) + 1, 0) if fr is not None else 0
                post = P[start:, [i, j]]
                if len(post) == 0:
                    c = "undetermined"
                else:
                    c = "followed" if (post >= lb["agreed_price"] - 1).all(1).mean() >= 0.5 else "abandoned"
            else:
                c = "no_agreement"
            cls.setdefault(c, []).append(dict(pair_stats(P, S, nash, i, j), run_id=rid, agreed=lb.get("agreed_price")))
        out = {"T": a.T or "full", "n_A": len(ctrl)}
        for c, v in cls.items():
            out[c] = {"n": len(v), **{k: round(float(np.mean([x[k] for x in v])), 3) for k in ("premium", "markup", "pcmi")},
                      **{f"auroc_{k}_vs_A_maxpair": auc([x[k] for x in v], [x[k] for x in ctrl]) for k in ("premium", "markup", "pcmi")},
                      "agreed_prices": sorted(x["agreed"] for x in v if x["agreed"] is not None)}
        res[name] = out
        print(name, json.dumps(out))
    json.dump(res, open(ROOT / "results" / "eval" / "behaviour_split.json", "w"), indent=1)


if __name__ == "__main__":
    main()
