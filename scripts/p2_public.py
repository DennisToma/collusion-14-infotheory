"""Phase 2 E59 (DIRECTION directive 3, declared in EXPERIMENTS.tsv before generation): does public cheap talk alone raise
deepseek's no-channel markup, and do absolute level screens then false-flag no-channel markets?
A_pub = llm_ds_p2pub (condition A + public board, same seeds as llm_ds_p2 A: seed 10, hash 'seed:A:k').
(i) market markup A_pub - A, paired by seed index k (bootstrap over pairs); C - A from llm_ds_p2 for comparison.
(ii) AUROC of the max-pair markup (market_level) C vs A_pub.   (iii) false-flag rate of A_pub at the frozen absolute
threshold = 95th percentile of llm_ds_p2 A max-pair markup (Jeffreys CI).   (iv) pCMI shift-null flag rate in A_pub
(alpha .05).   (v) share of public messages naming a price number (descriptive).
Rule: "public talk raises markup" iff the (i) CI excludes 0.
    uv run python scripts/p2_public.py [--run-eval] [--name llm_ds_p2pub --ref llm_ds_p2]
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.stats import beta

sys.path.insert(0, str(Path(__file__).resolve().parent))
from p2_variants import NASH, ROOT, boot_diff, markups  # noqa: E402


def per_run_markup(name):
    """Per-run market markup over Nash keyed by run id (markups() only returns per-condition lists; we pair by seed)."""
    _, gt = markups(name)
    rows = {}
    for line in open(ROOT / "data" / name / "trajectories.jsonl"):
        r = json.loads(line)
        rows.setdefault(r["run_id"], []).append(np.mean([a["price"] for a in r["agents"]]) - NASH[r["market"]["cost"]])
    return {rid: float(np.mean(v)) for rid, v in rows.items()}, gt


def jeffreys(k, n):
    return [float(beta.ppf(.025, k + .5, n - k + .5)) if k > 0 else 0.0,
            float(beta.ppf(.975, k + .5, n - k + .5)) if k < n else 1.0]


def auroc(pos, neg):
    pos, neg = np.asarray(pos), np.asarray(neg)
    return float(((pos[:, None] > neg[None]) + .5 * (pos[:, None] == neg[None])).mean())


def auroc_ci(pos, neg, B=4000, seed=0):
    rng = np.random.default_rng(seed)
    bs = [auroc(rng.choice(pos, len(pos)), rng.choice(neg, len(neg))) for _ in range(B)]
    return auroc(pos, neg), [float(np.quantile(bs, .025)), float(np.quantile(bs, .975))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="llm_ds_p2pub")
    ap.add_argument("--ref", default="llm_ds_p2")
    ap.add_argument("--run-eval", action="store_true")
    a = ap.parse_args()
    if a.run_eval:
        subprocess.run([sys.executable, "-m", "experiments.llm_eval", "eval", "--name", a.name, "--Ts", "20"], cwd=ROOT, check=True)
    mp, _ = per_run_markup(a.name)
    mr, gtr = per_run_markup(a.ref)
    k_of = lambda rid: rid.rsplit("_", 1)[1]
    refA = {k_of(r): v for r, v in mr.items() if gtr[r]["condition"] == "A"}
    refC = [v for r, v in mr.items() if gtr[r]["condition"] == "C"]
    pairs = [(v, refA[k_of(r)]) for r, v in sorted(mp.items()) if k_of(r) in refA]
    d = np.array([x - y for x, y in pairs])
    rng = np.random.default_rng(0)
    bs = [rng.choice(d, len(d)).mean() for _ in range(10000)]
    res = dict(name=a.name, ref=a.ref, n_pub=len(mp), n_pairs=len(pairs),
               A_markup=float(np.mean(list(refA.values()))), A_pub_markup=float(np.mean(list(mp.values()))),
               C_markup=float(np.mean(refC)),
               A_pub_minus_A=float(d.mean()), A_pub_minus_A_ci=[float(np.quantile(bs, q)) for q in (.025, .975)])
    cd, cci = boot_diff(refC, list(refA.values()))
    res["C_minus_A"], res["C_minus_A_ci"] = cd, cci
    res["verdict"] = ("public talk raises markup" if res["A_pub_minus_A_ci"][0] > 0 else
                      "public talk lowers markup" if res["A_pub_minus_A_ci"][1] < 0 else "no detectable change")
    evp, evr = ROOT / "results" / "eval" / f"{a.name}.json", ROOT / "results" / "eval" / f"{a.ref}.json"
    if evp.exists():
        sp = json.load(open(evp))["run_scores"]["20"]
        sr = json.load(open(evr))["run_scores"]["20"]
        scA = [v for r, v in sr["market_level"].items() if gtr[r]["condition"] == "A"]
        scC = [v for r, v in sr["market_level"].items() if gtr[r]["condition"] == "C"]
        scP = list(sp["market_level"].values())
        thr = float(np.quantile(scA, .95))
        k = int(sum(x > thr for x in scP))
        res["auroc_markup_C_vs_Apub"], res["auroc_markup_C_vs_Apub_ci"] = auroc_ci(scC, scP)
        res["auroc_markup_Apub_vs_A"], res["auroc_markup_Apub_vs_A_ci"] = auroc_ci(scP, scA)
        res["frozen_threshold_A95"] = thr
        res["Apub_false_flags"] = [k, len(scP)]
        res["Apub_false_flag_ci_jeffreys"] = jeffreys(k, len(scP))
        pc = json.load(open(evp))["by_T"]["20"]["pcmi"]["A"]
        kp = int(round(pc["flag_rate"] * pc["n"]))
        res["Apub_pcmi_flags"] = [kp, pc["n"]]
        res["Apub_pcmi_flag_ci_jeffreys"] = jeffreys(kp, pc["n"])
        res["auroc_pcmi_C_vs_Apub"], res["auroc_pcmi_C_vs_Apub_ci"] = auroc_ci(
            [v for r, v in sr["pcmi"].items() if gtr[r]["condition"] == "C"], list(sp["pcmi"].values()))
    msgs = [ag.get("public_message", "") for line in open(ROOT / "data" / a.name / "trajectories.jsonl")
            for ag in json.loads(line)["agents"]]
    msgs = [m for m in msgs if m and m.strip()]
    res["public_messages"] = len(msgs)
    res["public_messages_with_price_number"] = sum(bool(re.search(r"\b\d{1,2}\b", m)) for m in msgs)
    out = ROOT / "results" / "eval" / f"p2_public_{a.name}.json"
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
