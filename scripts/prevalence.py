"""Phase 2 (E46): precision of the headline detectors at realistic collusion prevalence.

At the frozen thresholds (alpha=0.05 run-level flags; shift null or control-surrogate null), take the
observed flag rate on colluding markets (TPR) and on each kind of negative market (FPR) from the saved
evaluation JSONs and compute, for prevalence pi in {1%, 5%, 20%}:
    precision = pi*TPR / (pi*TPR + (1-pi)*FPR),  false alarms per true alarm = (1-pi)*FPR / (pi*TPR),
    alarms per 1000 markets = 1000*(pi*TPR + (1-pi)*FPR).
95% intervals: independent Jeffreys Beta(k+1/2, n-k+1/2) draws for TPR and FPR (20k draws).
Caveat carried into the output: surrogate-null FPR on the reference controls themselves is <= alpha by
construction (leave-one-out), so those rows are flagged `fpr_by_construction`.

    uv run python scripts/prevalence.py   # -> results/eval/prevalence.json, results/eval/prevalence.md
"""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
EV = ROOT / "results" / "eval"
PIS = (0.01, 0.05, 0.20)


def counts(rate, n):
    return int(round(rate * n)), n


def rows():
    out = []
    g = json.load(open(EV / "gate_test.json"))["metrics"]
    for det in ("mi", "pcmi"):
        for null, key in (("shift", "flag_rate"), ("surrogate", "surrogate_flag_rate")):
            pos = g[det]["C"]
            for neg in ("A", "B", "A+shared_policy", "A+shared_seed", "A+legit_cooperation"):
                out.append(dict(setting="scripted gate_test (T=100, signal s=0.6)", detector=det, null=null,
                                pos="C", tp=counts(pos[key], pos["n"]), neg=neg,
                                fp=counts(g[det][neg][key], g[det][neg]["n"]),
                                fpr_by_construction=(null == "surrogate" and neg == "A")))
    v = json.load(open(EV / "llm_v1.json"))["by_T"]["20"]
    for det, null, key in (("pcmi", "shift", "flag_rate"), ("pcmi", "surrogate", "surrogate_flag_rate"),
                           ("market_level", "surrogate", "surrogate_flag_rate"),
                           ("pair_level", "surrogate", "surrogate_flag_rate")):
        tp = tuple(map(sum, zip(*(counts(v[det][c][key], v[det][c]["n"]) for c in "CD"))))
        fp = tuple(map(sum, zip(*(counts(v[det][c][key], v[det][c]["n"]) for c in "AB"))))
        out.append(dict(setting="LLM llm_v1 (T=20)", detector=det, null=null, pos="C+D", tp=tp, neg="A+B",
                        fp=fp, fpr_by_construction=null == "surrogate"))
    x = json.load(open(EV / "llm_v3_ext.json"))["detectors"]
    for det in ("pcmi", "pair_level"):
        p = x[det]["surrogate_flag_private"]
        for neg in ("none", "legit"):
            q = x[det][f"surrogate_flag_{neg}"]
            out.append(dict(setting="LLM sibling llm_v3 (T=12)", detector=det, null="surrogate", pos="private",
                            tp=counts(p["rate"], p["n"]), neg=neg, fp=counts(q["rate"], q["n"]),
                            fpr_by_construction=neg == "none"))
    return out


def summarise(r, draws=20000, seed=0):
    rng = np.random.default_rng(seed)
    (k1, n1), (k0, n0) = r["tp"], r["fp"]
    tpr = rng.beta(k1 + .5, n1 - k1 + .5, draws)
    fpr = rng.beta(k0 + .5, n0 - k0 + .5, draws)
    r = dict(r, tpr=k1 / n1, fpr=k0 / n0)
    for pi in PIS:
        prec = pi * tpr / (pi * tpr + (1 - pi) * fpr)
        pt = (pi * k1 / n1 / (pi * k1 / n1 + (1 - pi) * k0 / n0)) if (k1 + k0) else float("nan")
        r[f"precision@{pi:g}"] = pt
        r[f"precision@{pi:g}_ci"] = [float(np.quantile(prec, .025)), float(np.quantile(prec, .975))]
        r[f"false_per_true@{pi:g}"] = ((1 - pi) * k0 / n0 / (pi * k1 / n1)) if k1 else float("inf")
        r[f"alarms_per_1000@{pi:g}"] = 1000 * (pi * k1 / n1 + (1 - pi) * k0 / n0)
    return r


def main():
    res = [summarise(r) for r in rows()]
    json.dump(res, open(EV / "prevalence.json", "w"), indent=1)
    lines = ["| setting | detector | null | TPR (pos) | FPR (neg) | precision @1% | @5% | @20% | false alarms per true alarm @5% |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in res:
        def cell(pi):
            p, ci = r[f"precision@{pi:g}"], r[f"precision@{pi:g}_ci"]
            return "n/a (no alarms)" if p != p else f"{p:.2f} [{ci[0]:.2f}, {ci[1]:.2f}]"
        star = "*" if r["fpr_by_construction"] else ""
        fpt = r["false_per_true@0.05"]
        lines.append(f"| {r['setting']} | {r['detector']} | {r['null']} | {r['tp'][0]}/{r['tp'][1]} ({r['pos']}) | "
                     f"{r['fp'][0]}/{r['fp'][1]} ({r['neg']}){star} | {cell(.01)} | {cell(.05)} | {cell(.2)} | "
                     f"{'∞ (TPR 0)' if fpt == float('inf') else f'{fpt:.1f}'} |")
    lines.append("\n\\* FPR on the surrogate reference controls themselves is ≤ α by construction (leave-one-out); "
                 "only hard-negative FPRs are independent evidence.")
    (EV / "prevalence.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
