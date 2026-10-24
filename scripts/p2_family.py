"""Phase 2 E45: second seller family (deepseek-v4.1-flash via OpenCode Go) in our market vs llm_v1 (gpt-6-luna, same seed 10).

Declared rule (EXPERIMENTS.tsv E45-deepseek-family-declared): HOLDS iff the C - A markup CI excludes 0 AND run AUROC (C vs A, T=20)
of markup (market_level) > pCMI. Amendment (E45-analysis-amendment): family x condition interaction and a degeneracy check.
    uv run python scripts/p2_family.py [--run-eval]   # -> results/eval/p2_family.{json,md}
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from p2_variants import DETS, NASH, ROOT, boot_diff, markups  # noqa: E402

NAME, REF = "llm_ds_p2", "llm_v1"


def degeneracy(name):
    prices = {}
    for line in open(ROOT / "data" / name / "trajectories.jsonl"):
        r = json.loads(line)
        for a in r["agents"]:
            prices.setdefault((r["run_id"], a["id"]), []).append(a["price"])
    sd = np.array([np.std(p) for p in prices.values()])
    nd = np.array([len(set(p)) for p in prices.values()])
    return dict(n_sellers=len(prices), sd_median=round(float(np.median(sd)), 2), sd_min=round(float(sd.min()), 2),
                constant_sellers=int((sd == 0).sum()), distinct_prices_median=float(np.median(nd)))


def interaction(by1, by0, B=10000, seed=0):
    rng = np.random.default_rng(seed)
    arr = [np.asarray(by1["C"]), np.asarray(by1["A"]), np.asarray(by0["C"]), np.asarray(by0["A"])]
    d = lambda x: x[0].mean() - x[1].mean() - (x[2].mean() - x[3].mean())
    bs = [d([rng.choice(x, len(x)) for x in arr]) for _ in range(B)]
    return round(float(d(arr)), 3), [round(float(np.quantile(bs, q)), 3) for q in (.025, .975)]


def row(name):
    by, gt = markups(name)
    r = dict(n_A=len(by["A"]), n_C=len(by["C"]),
             models=sorted({m for g in gt.values() for m in (g.get("model") or {}).values()}),
             A_markup=round(float(np.mean(by["A"])), 3), C_markup=round(float(np.mean(by["C"])), 3))
    d, ci = boot_diff(by["C"], by["A"])
    r["C_minus_A_markup"], r["C_minus_A_ci"] = round(d, 3), [round(x, 3) for x in ci]
    ev = ROOT / "results" / "eval" / f"{name}.json"
    if ev.exists():
        m = json.load(open(ev))["by_T"]["20"]
        for k in DETS:
            r[f"auroc_{k}"] = m[k].get("auroc_C_vs_A")
            r[f"auroc_{k}_ci"] = m[k].get("auroc_ci_C_vs_A")
            r[f"flag_rate_{k}"] = {c: m[k].get(c, {}).get("flag_rate") for c in "AC"}
    return r, by


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-eval", action="store_true")
    a = ap.parse_args()
    if a.run_eval:
        subprocess.run([sys.executable, "-m", "experiments.llm_eval", "eval", "--name", NAME, "--Ts", "20"], cwd=ROOT, check=True)
    ds, by1 = row(NAME)
    ref, by0 = row(REF)
    ds["degeneracy"] = degeneracy(NAME)
    ref["degeneracy"] = degeneracy(REF)
    res = {"deepseek": ds, "luna_llm_v1": ref, "interaction_C_minus_A_ds_minus_luna": interaction(by1, by0)}
    if "auroc_pcmi" in ds:
        ok_n = ds["n_A"] >= 8 and ds["n_C"] >= 8
        holds = ds["C_minus_A_ci"][0] > 0 and ds["auroc_market_level"] > ds["auroc_pcmi"]
        res["rule"] = dict(markup_ci_excludes_0=ds["C_minus_A_ci"][0] > 0,
                           level_beats_pcmi=ds["auroc_market_level"] > ds["auroc_pcmi"], n_ok_for_auroc=ok_n,
                           verdict=("HOLDS" if holds else "FAILS") if ok_n else "INCONCLUSIVE (n<8+8)")
    json.dump(res, open(ROOT / "results" / "eval" / "p2_family.json", "w"), indent=1)
    f = lambda x, ci: "–" if x is None else f"{x:.2f} [{ci[0]:.2f}, {ci[1]:.2f}]"
    lines = ["| family (dataset) | n C/A | A markup | C markup | C − A markup [95% CI] | AUROC markup | AUROC pair_level | AUROC pCMI | seller price SD (median) |",
             "|---|---|---|---|---|---|---|---|---|"]
    for lab, r in (("deepseek-v4.1-flash (`llm_ds_p2`)", ds), ("gpt-6-luna (`llm_v1`)", ref)):
        lines.append(f"| {lab} | {r['n_C']}/{r['n_A']} | {r['A_markup']:+.2f} | {r['C_markup']:+.2f} | {f(r['C_minus_A_markup'], r['C_minus_A_ci'])} | "
                     + " | ".join(f(r.get(f'auroc_{k}'), r.get(f'auroc_{k}_ci') or [0, 0]) for k in DETS)
                     + f" | {r['degeneracy']['sd_median']} |")
    i = res["interaction_C_minus_A_ds_minus_luna"]
    lines.append(f"\nFamily x condition interaction (C − A deepseek minus C − A luna): {i[0]:+.2f} [{i[1][0]:.2f}, {i[1][1]:.2f}]")
    lines.append(f"\nDegeneracy: deepseek {ds['degeneracy']}; luna {ref['degeneracy']}")
    if "rule" in res:
        lines.append(f"\nDeclared rule (E45): {res['rule']}")
    (ROOT / "results" / "eval" / "p2_family.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
