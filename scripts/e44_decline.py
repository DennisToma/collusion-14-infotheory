"""E44 follow-up (codex review 13:34): is the T=20 -> T=60 decline of pCMI AUROC (C vs A, same 40 games) itself significant?
Paired game bootstrap (games resampled once, both prefixes scored on the same resample; 4000 draws).
    uv run python scripts/e44_decline.py   # -> results/eval/e44_decline.json
"""
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parent.parent
e = json.load(open(ROOT / "results/eval/llm_long_p2_T60.json"))
gt = {g["run_id"]: g["condition"] for g in map(json.loads, open(ROOT / "data/llm_long_p2_T60/ground_truth.jsonl"))}
out = {}
for det in ("pcmi", "market_level"):
    s20, s60 = e["run_scores"]["20"][det], e["run_scores"]["60"][det]
    C, A = [r for r in s60 if gt[r] == "C"], [r for r in s60 if gt[r] == "A"]
    f = lambda s, c, a: roc_auc_score([1] * len(c) + [0] * len(a), [s[r] for r in c] + [s[r] for r in a])
    rng, d = np.random.default_rng(0), []
    for _ in range(4000):
        c, a = list(rng.choice(C, len(C))), list(rng.choice(A, len(A)))
        d.append(f(s60, c, a) - f(s20, c, a))
    out[det] = dict(auroc_T20=f(s20, C, A), auroc_T60=f(s60, C, A), diff=f(s60, C, A) - f(s20, C, A),
                    ci=[float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))])
(ROOT / "results/eval/e44_decline.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
