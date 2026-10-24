"""Descriptive: per-seller mean price by model in llm_mixed2 (sol vs luna), per-run difference with bootstrap CI.
uv run python scripts/mixed_price_by_model.py  -> results/eval/llm_mixed2_price_by_model.json"""
import json, collections
import numpy as np
gt = {json.loads(l)["run_id"]: json.loads(l) for l in open("data/llm_mixed2/ground_truth.jsonl")}
P = collections.defaultdict(list)
states = set()
for l in open("data/llm_mixed2/trajectories.jsonl"):
    r = json.loads(l)
    states.add((r["market"]["demand_shock"], r["market"]["cost"]))
    for a in r["agents"]:
        P[(r["run_id"], a["id"])].append(a["price"])
R = collections.defaultdict(list)
for (rid, a), v in P.items():
    R[gt[rid]["model"][a]].append((np.mean(v), np.std(v)))
out = {"n_states": len(states)}
for m, v in R.items():
    v = np.array(v)
    out[m] = {"n_sellers": len(v), "mean_price": float(v[:, 0].mean()), "mean_within_sd": float(v[:, 1].mean())}
d = np.array([np.mean([np.mean(P[(rid, a)]) for a in "ABCD" if g["model"][a] == "gpt-6.1-sol"])
              - np.mean([np.mean(P[(rid, a)]) for a in "ABCD" if g["model"][a] == "gpt-6-luna"]) for rid, g in gt.items()])
bs = np.random.default_rng(0).choice(d, (5000, len(d))).mean(1)
out["sol_minus_luna_per_run"] = {"n_runs": len(d), "mean": float(d.mean()), "ci": [float(x) for x in np.percentile(bs, [2.5, 97.5])],
                                 "n_positive": int((d > 0).sum())}
print(json.dumps(out, indent=1))
json.dump(out, open("results/eval/llm_mixed2_price_by_model.json", "w"), indent=1)
