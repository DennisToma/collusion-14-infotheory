"""E54 (Phase 2 gap 3 hole, directive 4): out-of-sample calibration of a model-matched reference pool.

P2.3(c) showed a mismatched reference (mixed sol+luna markets) gives pCMI 11/21 = 52% false flags on all-luna no-channel
markets, but the matched pool there was leave-one-out on the same batch (<= alpha by construction). Here the reference pool is
FRESH, independently generated luna no-channel markets (Phase 2 batches), and the test sets are the llm_v1 games:
  llm_v1 A (21 no-channel luna markets) -> out-of-sample false-flag rate;  llm_v1 C (16 channel markets) -> power.
Pools (T=20; completed games only):
  fresh_all : llm_p2_<variant> A (E43, 5 prompt variants, seed 43) + llm_long_p2 A first-20-round prefixes (E44, seed 50)
  fresh_v0  : the prompt-matched subset (llm_p2_v0 A + llm_long_p2 A; same prompt as llm_v1)
  mixed     : llm_mixed2 A (the mismatched sol+luna pool of P2.3c, for comparison)
Reverse check: fresh_all games tested against the llm_v1 A pool. No new LLM calls; detectors frozen (score_run, B=0 scores).
Run score = max over the 6 pairs; surrogate p = (1 + #pool >= x) / (1 + |pool|). Rule declared in EXPERIMENTS.tsv (E54).

    uv run python scripts/matched_ref.py [--interim]   # -> results/eval/matched_ref.{json,md}
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
from scripts.same_model import surrogate  # noqa: E402

T = 20
DETS = ("pair_markup", "pair_level", "pcmi", "mi")
VARIANTS = ("v0", "para", "template", "order", "noreason")


def wilson(k, n, z=1.96):
    if n == 0:
        return [0.0, 1.0]
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [round(float(max(0, c - h)), 3), round(float(min(1, c + h)), 3)]


def score(name, cond):
    """Pair scores for the completed `cond` games of a dataset (first T rounds)."""
    if not (ROOT / "data" / name / "ground_truth.jsonl").exists():
        return {}
    _, gt, rows = load(name)
    out = {}
    for rid in sorted(gt):
        rs = rows.get(rid, [])
        if gt[rid]["condition"] != cond or len(rs) < T:
            continue
        rs = rs[:T]
        P, S, _ = arrays(rs)
        nash = np.array([NASH[r["market"]["cost"]] for r in rs], float)
        res = score_run(P, S, B=0)
        pairs = {}
        for (i, j), pn in zip(PAIRS, PAIR_NAMES):
            others = [k for k in range(4) if k not in (i, j)]
            sc = {k: res[pn]["score"][k] for k in ("pcmi", "mi")}
            sc["pair_level"] = float(P[:, [i, j]].mean() - P[:, others].mean())
            sc["pair_markup"] = float((P[:, [i, j]] - nash[:, None]).mean())
            pairs[pn] = {"score": sc}
        out[f"{name}:{rid}"] = {"cond": cond, "pairs": pairs, "mean_markup": float((P - nash[:, None]).mean())}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--interim", action="store_true", help="label the output as an interim run (pool incomplete)")
    a = ap.parse_args()
    v1A, v1C, mixed = score("llm_v1", "A"), score("llm_v1", "C"), score("llm_mixed2", "A")
    longA = score("llm_long_p2", "A")
    var = {v: score(f"llm_p2_{v}", "A") for v in VARIANTS}
    if not a.interim:
        need = {**{f"llm_p2_{v}": 6 for v in VARIANTS}, "llm_long_p2": 20}
        got = {**{f"llm_p2_{v}": len(d) for v, d in var.items()}, "llm_long_p2": len(longA)}
        if got != need:
            sys.exit(f"pool incomplete {got} (declared {need}); rerun with --interim")
    fresh_all = {k: x for d in list(var.values()) + [longA] for k, x in d.items()}
    fresh_v0 = {**var["v0"], **longA}
    pools = {"fresh_all": fresh_all, "fresh_v0": fresh_v0, "mixed": mixed}
    res = {"interim": a.interim, "T": T,
           "n": {"llm_v1_A": len(v1A), "llm_v1_C": len(v1C), "llm_long_p2_A": len(longA),
                 **{f"llm_p2_{v}_A": len(d) for v, d in var.items()}, **{f"pool_{k}": len(p) for k, p in pools.items()}},
           "rows": {}}
    for det in DETS:
        for alpha in (0.05, 0.10):
            r = {}
            for pk, pool in pools.items():
                if len(pool) == 0:
                    continue
                for tk, test in (("v1A", v1A), ("v1C", v1C)):
                    s = surrogate(test, pool, det, alpha)
                    s["wilson"] = wilson(s["flags"], s["n"])
                    r[f"{tk}|{pk}"] = s
            s = surrogate(fresh_all, v1A, det, alpha)
            s["wilson"] = wilson(s["flags"], s["n"])
            r["fresh_all|v1A"] = s
            s = surrogate(fresh_all, fresh_all, det, alpha)  # LOO within the fresh pool (<= alpha by construction)
            s["wilson"] = wilson(s["flags"], s["n"])
            r["fresh_all|fresh_all_LOO"] = s
            res["rows"][f"{det}@{alpha}"] = r
    # declared rule (alpha .05): restores iff v1A false-flag rate <= .10 and Wilson upper < .52
    res["rule"] = {}
    for det in DETS:
        x = res["rows"][f"{det}@0.05"].get("v1A|fresh_all")
        if x:
            res["rule"][det] = {"fpr": x["rate"], "wilson": x["wilson"], "pool_n": x["pool_n"],
                                "restores": bool(x["rate"] <= 0.10 and x["wilson"][1] < 0.52)}
    mk = lambda d: [v["mean_markup"] for v in d.values()]
    rng = np.random.default_rng(0)
    res["market_markup"] = {}
    for n, d in (("llm_v1 A", v1A), ("llm_v1 C", v1C), ("mixed2 A", mixed), ("fresh_all A", fresh_all),
                 ("fresh_v0 A", fresh_v0), *((f"llm_p2_{v} A", var[v]) for v in VARIANTS), ("llm_long_p2 A (T20)", longA)):
        if d:
            x = np.array(mk(d))
            bs = rng.choice(x, (5000, len(x))).mean(1)
            res["market_markup"][n] = {"n": len(x), "mean": round(float(x.mean()), 3),
                                       "ci": [round(float(q), 3) for q in np.percentile(bs, [2.5, 97.5])]}
    (ROOT / "results" / "eval").mkdir(parents=True, exist_ok=True)
    json.dump(res, open(ROOT / "results" / "eval" / "matched_ref.json", "w"), indent=1)
    md = [f"# E54 matched reference pool{' (INTERIM)' if a.interim else ''} (T={T})", "", "n: " + json.dumps(res["n"]), "",
          "| detector @ alpha | " + " | ".join(res["rows"]["pcmi@0.05"].keys()) + " |",
          "|---|" + "---|" * len(res["rows"]["pcmi@0.05"])]
    for k, r in res["rows"].items():
        md.append(f"| {k} | " + " | ".join(f"{x['flags']}/{x['n']} [{100*x['wilson'][0]:.0f}, {100*x['wilson'][1]:.0f}] (pool {x['pool_n']})"
                                           for x in r.values()) + " |")
    md += ["", "rule (alpha .05, v1A vs fresh_all): " + json.dumps(res["rule"]), "",
           "market mean markup over Nash:"] + [f"- {k}: {json.dumps(v)}" for k, v in res["market_markup"].items()]
    open(ROOT / "results" / "eval" / "matched_ref.md", "w").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
