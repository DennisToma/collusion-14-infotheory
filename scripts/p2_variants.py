"""Phase 2 E43: prompt-wording robustness of the llm_v1 pattern (declared rule in EXPERIMENTS.tsv, E43-prompt-variants-declared).

Per arm (llm_p2_<variant>, A vs C, T=20): C - A mean market markup over the per-round Nash price (run bootstrap CI) and run AUROC
(C vs A) of markup (= market_level, max-pair markup), pair_level and pCMI from the frozen evaluator results/eval/<name>.json
(run `uv run python -m experiments.llm_eval eval --name llm_p2_<variant> --Ts 20` first; --run-eval does it).
    uv run python scripts/p2_variants.py [--run-eval]   # -> results/eval/p2_variants.json, results/eval/p2_variants.md
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
VARIANTS = ("v0", "para", "template", "order", "noreason")
NASH = {6: 10, 8: 12}
DETS = ("market_level", "pair_level", "pcmi")


def markups(name):
    gt = {json.loads(l)["run_id"]: json.loads(l) for l in open(ROOT / "data" / name / "ground_truth.jsonl")}
    acc = {}
    for line in open(ROOT / "data" / name / "trajectories.jsonl"):
        r = json.loads(line)
        nash = NASH[r["market"]["cost"]]
        acc.setdefault(r["run_id"], []).append(np.mean([a["price"] for a in r["agents"]]) - nash)
    by = {"A": [], "B": [], "C": [], "D": []}
    for rid, xs in acc.items():
        by[gt[rid]["condition"]].append(float(np.mean(xs)))
    return by, gt


def boot_diff(c, a, B=10000, seed=0):
    rng = np.random.default_rng(seed)
    c, a = np.asarray(c), np.asarray(a)
    d = [rng.choice(c, len(c)).mean() - rng.choice(a, len(a)).mean() for _ in range(B)]
    return float(c.mean() - a.mean()), [float(np.quantile(d, .025)), float(np.quantile(d, .975))]


def heterogeneity(out, B=10000, seed=0):
    """Variant x condition interaction: Cochran's Q over the per-arm C - A markups, SEs from a run bootstrap (E43 amendment)."""
    from scipy.stats import chi2
    d, se = [], []
    for v, r in out.items():
        if r.get("n_A", 0) < 2 or r.get("n_C", 0) < 2:
            continue
        by, _ = markups(f"llm_p2_{v}")
        rng = np.random.default_rng(seed)
        c, a = np.asarray(by["C"]), np.asarray(by["A"])
        bs = [rng.choice(c, len(c)).mean() - rng.choice(a, len(a)).mean() for _ in range(B)]
        d.append(c.mean() - a.mean())
        se.append(float(np.std(bs)))
    if len(d) < 2:
        return None
    d, w = np.array(d), 1 / np.array(se) ** 2
    pooled = float((w * d).sum() / w.sum())
    Q = float((w * (d - pooled) ** 2).sum())
    k = len(d)
    return {"k": k, "Q": round(Q, 2), "p": round(float(chi2.sf(Q, k - 1)), 4),
            "I2": round(max(0.0, (Q - (k - 1)) / Q) if Q > 0 else 0.0, 3),
            "fixed_effect_C_minus_A": round(pooled, 3), "fixed_effect_se": round(float(np.sqrt(1 / w.sum())), 3)}


def pooled_auroc(variants, B=2000, seed=0):
    """AUROC of C vs A where each C game is compared only with A games of the same wording; stratified game bootstrap."""
    if not variants:
        return {}
    sc = {}
    for v in variants:
        ev = json.load(open(ROOT / "results" / "eval" / f"llm_p2_{v}.json"))["run_scores"]["20"]
        _, gt = markups(f"llm_p2_{v}")
        sc[v] = {d: {c: np.array([s for rid, s in ev[d].items() if gt[rid]["condition"] == c]) for c in "AC"} for d in DETS}

    def auc(arms):
        num = den = 0.0
        for x in arms:
            p, n = x["C"][:, None], x["A"][None, :]
            num += float(((p > n) + 0.5 * (p == n)).sum())
            den += p.size * n.size
        return num / den
    rng = np.random.default_rng(seed)
    out = {}
    for d in DETS:
        arms = [sc[v][d] for v in variants]
        bs = [auc([{c: rng.choice(x[c], len(x[c])) for c in "AC"} for x in arms]) for _ in range(B)]
        out[d] = [round(auc(arms), 3), [round(float(q), 3) for q in np.percentile(bs, [2.5, 97.5])]]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-eval", action="store_true")
    a = ap.parse_args()
    out, pooled = {}, {"A": [], "C": []}
    for v in VARIANTS:
        name = f"llm_p2_{v}"
        if not (ROOT / "data" / name / "ground_truth.jsonl").exists():
            continue
        if a.run_eval:
            subprocess.run([sys.executable, "-m", "experiments.llm_eval", "eval", "--name", name, "--Ts", "20"],
                           cwd=ROOT, check=True)
        by, gt = markups(name)
        models = sorted({m for g in gt.values() for m in (g.get("model") or {}).values()})
        row = dict(n_A=len(by["A"]), n_C=len(by["C"]), models=models)
        if by["A"] and by["C"]:
            row["C_minus_A_markup"], row["C_minus_A_ci"] = boot_diff(by["C"], by["A"])
            row["A_markup"], row["C_markup"] = float(np.mean(by["A"])), float(np.mean(by["C"]))
        ev = ROOT / "results" / "eval" / f"{name}.json"
        if ev.exists():
            m = json.load(open(ev))["by_T"]["20"]
            for d in DETS:
                row[f"auroc_{d}"] = m[d].get("auroc_C_vs_A")
                row[f"auroc_{d}_ci"] = m[d].get("auroc_ci_C_vs_A")
        out[v] = row
        for c in "AC":
            pooled[c] += by[c]
    res = {"arms": out}
    if pooled["A"] and pooled["C"]:
        res["pooled_C_minus_A"], res["pooled_ci"] = boot_diff(pooled["C"], pooled["A"])
        res["pooled_n"] = [len(pooled["C"]), len(pooled["A"])]
    het = heterogeneity(out)
    if het:
        res["heterogeneity"] = het
    res["pooled_within_arm_auroc"] = pooled_auroc([v for v in out if (ROOT / "results" / "eval" / f"llm_p2_{v}.json").exists()])
    done = [r for r in out.values() if "C_minus_A_markup" in r and "auroc_pcmi" in r]
    if len(done) == len(VARIANTS):
        pos = sum(r["C_minus_A_markup"] > 0 for r in done)
        lvl = sum(r["auroc_market_level"] > r["auroc_pcmi"] for r in done)
        holds = pos >= 4 and res["pooled_ci"][0] > 0 and lvl >= 4
        fails = sum(r["C_minus_A_markup"] <= 0 for r in done) >= 2
        res["rule"] = dict(arms_markup_pos=pos, arms_level_beats_pcmi=lvl,
                           verdict="HOLDS" if holds else "FAILS" if fails else "PARTIAL")
        res["band"] = {k: [min(r[k] for r in done), max(r[k] for r in done)]
                       for k in ("C_minus_A_markup", "auroc_market_level", "auroc_pair_level", "auroc_pcmi")}
    json.dump(res, open(ROOT / "results" / "eval" / "p2_variants.json", "w"), indent=1)
    lines = ["| wording | n C/A | C − A markup [95% CI] | AUROC markup | AUROC pair_level | AUROC pCMI |", "|---|---|---|---|---|---|"]
    f = lambda x, ci: "–" if x is None else f"{x:.2f} [{ci[0]:.2f}, {ci[1]:.2f}]"
    for v, r in out.items():
        lines.append(f"| {v} | {r['n_C']}/{r['n_A']} | {f(r.get('C_minus_A_markup'), r.get('C_minus_A_ci', [0, 0]))} | "
                     + " | ".join(f(r.get(f'auroc_{d}'), r.get(f'auroc_{d}_ci') or [0, 0]) for d in DETS) + " |")
    if "pooled_C_minus_A" in res:
        lines.append(f"| pooled | {res['pooled_n'][0]}/{res['pooled_n'][1]} | {f(res['pooled_C_minus_A'], res['pooled_ci'])} | | | |")
    if het:
        lines.append(f"\nHeterogeneity of C − A markup across wordings (Cochran Q, bootstrap SEs): {het}")
    if res["pooled_within_arm_auroc"]:
        lines.append(f"\nPooled within-arm AUROC C vs A (pairs compared only within a wording): {res['pooled_within_arm_auroc']}")
    if "rule" in res:
        lines.append(f"\nDeclared rule (E43): {res['rule']}; band over wordings: {res['band']}")
    (ROOT / "results" / "eval" / "p2_variants.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
