"""Pair-minus-rivals price premium per condition on the sibling's llm_v3 (read-only), for REPORT §4.4.
Usage: uv run python -m experiments.premium_llm_v3  -> results/eval/llm_v3_premium.json"""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
D = ROOT.parent / "collusion-22-say-vs-do" / "data" / "llm_v3"


def main(B=5000):
    gt = {g["run_id"]: g for g in map(json.loads, open(D / "ground_truth.jsonl"))}
    prices = defaultdict(lambda: defaultdict(list))
    for r in map(json.loads, open(D / "trajectories.jsonl")):
        for a in r["agents"]:
            prices[r["run_id"]][a["id"]].append(a["price"])
    gaps = defaultdict(list)
    for rid, ps in prices.items():
        pair = set(gt[rid]["assigned_pair"])
        pm = np.mean([np.mean(v) for k, v in ps.items() if k in pair])
        rm = np.mean([np.mean(v) for k, v in ps.items() if k not in pair])
        gaps[gt[rid]["condition"]].append(pm - rm)
    rng = np.random.default_rng(0)
    out = {}
    for c, g in sorted(gaps.items()):
        g = np.array(g)
        bs = [rng.choice(g, len(g)).mean() for _ in range(B)]
        out[c] = {"n": len(g), "mean": float(g.mean()), "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                  "q10_q90": [float(np.percentile(g, 10)), float(np.percentile(g, 90))]}
    print(json.dumps(out, indent=1))
    json.dump(out, open(ROOT / "results" / "eval" / "llm_v3_premium.json", "w"), indent=1)


if __name__ == "__main__":
    main()
