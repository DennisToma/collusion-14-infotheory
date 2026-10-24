"""Descriptive (§4.3.2): range of per-game market mean price by condition group in llm_v1 (all games).
uv run python scripts/market_mean_ranges.py -> results/eval/llm_v1_market_mean_ranges.json"""
import json, collections
import numpy as np
cond = {json.loads(l)["run_id"]: json.loads(l)["condition"] for l in open("data/llm_v1/ground_truth.jsonl")}
P = collections.defaultdict(list)
for l in open("data/llm_v1/trajectories.jsonl"):
    r = json.loads(l)
    P[r["run_id"]] += [a["price"] for a in r["agents"]]
out = {}
for name, cs in [("CD", "CD"), ("AB", "AB")] + [(c, c) for c in "ABCD"]:
    m = [float(np.mean(v)) for rid, v in P.items() if cond[rid] in cs]
    out[name] = {"n_games": len(m), "min": min(m), "max": max(m), "median": float(np.median(m))}
print(json.dumps(out, indent=1))
json.dump(out, open("results/eval/llm_v1_market_mean_ranges.json", "w"), indent=1)
