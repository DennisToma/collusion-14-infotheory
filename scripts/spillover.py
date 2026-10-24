"""E44 declared descriptive line (DIRECTION 09:35, directive 1): market-wide spillover of the private channel.
Per 10-round block b: spillover_b = mean over C games of the RIVALS' markup over Nash (the two non-pair sellers)
minus mean over A games of the market markup over Nash (all four sellers; A has no pair). Also pair_excess_b = C pair
markup - A market markup. Independent game-bootstrap 95% CIs (C and A resampled separately).
Declared reading: "market-wide spillover" iff the LAST block's spillover CI excludes 0 AND spillover >= 0.5 x
pair_excess in that block (point estimates). Descriptive; no detector, no threshold tuning.
    uv run python scripts/spillover.py --name llm_long_p2_T60   # -> results/eval/spillover_<name>.{json,md}
"""
import argparse
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
NASH = {6: 10, 8: 12}


def load(name):
    gt = {g["run_id"]: g for g in map(json.loads, open(ROOT / "data" / name / "ground_truth.jsonl"))}
    rows = {}
    for line in open(ROOT / "data" / name / "trajectories.jsonl"):
        r = json.loads(line)
        rows.setdefault(r["run_id"], []).append(r)
    T = min(len(v) for v in rows.values())
    out = {"A": [], "C_riv": [], "C_pair": []}
    for rid, rs in rows.items():
        c = gt[rid]["condition"]
        if c not in ("A", "C"):
            continue
        rs = sorted(rs, key=lambda r: r["round"])[:T]
        nash = np.array([NASH[r["market"]["cost"]] for r in rs], float)
        P = {a["id"]: np.array([[x for x in r["agents"] if x["id"] == a["id"]][0]["price"] for r in rs], float)
             for a in rs[0]["agents"]}
        if c == "A":
            out["A"].append(np.mean(list(P.values()), 0) - nash)
        else:
            pair = gt[rid]["assigned_pair"]
            out["C_riv"].append(np.mean([P[k] for k in P if k not in pair], 0) - nash)
            out["C_pair"].append(np.mean([P[k] for k in pair], 0) - nash)
    return {k: np.array(v) for k, v in out.items()}, T


def diff_ci(X, Y, B=4000, seed=0):
    rng = np.random.default_rng(seed)
    bs = [X[rng.integers(0, len(X), len(X))].mean() - Y[rng.integers(0, len(Y), len(Y))].mean() for _ in range(B)]
    return float(X.mean() - Y.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="llm_long_p2_T60")
    ap.add_argument("--block", type=int, default=10)
    a = ap.parse_args()
    d, T = load(a.name)
    blocks = []
    for s in range(0, T, a.block):
        e = min(s + a.block, T)
        A = d["A"][:, s:e].mean(1)
        sp = diff_ci(d["C_riv"][:, s:e].mean(1), A)
        pe = diff_ci(d["C_pair"][:, s:e].mean(1), A)
        blocks.append(dict(rounds=f"{s + 1}-{e}", spillover=sp, pair_excess=pe,
                           A_markup=float(A.mean()), C_rival_markup=float(d["C_riv"][:, s:e].mean()),
                           C_pair_markup=float(d["C_pair"][:, s:e].mean())))
    last = blocks[-1]
    verdict = ("market-wide spillover" if last["spillover"][1] > 0 and last["spillover"][0] >= .5 * last["pair_excess"][0]
               else "no market-wide spillover (declared rule not met)")
    res = dict(name=a.name, T=T, n_A=len(d["A"]), n_C=len(d["C_riv"]), blocks=blocks, verdict=verdict,
               rule="last-block spillover CI excludes 0 AND spillover >= 0.5 x pair_excess")
    od = ROOT / "results" / "eval"
    (od / f"spillover_{a.name}.json").write_text(json.dumps(res, indent=1))
    f = lambda t: f"{t[0]:+.2f} [{t[1]:+.2f}, {t[2]:+.2f}]"
    md = [f"# Spillover ({a.name}, T={T}, A n={res['n_A']}, C n={res['n_C']})", "",
          "| rounds | A market markup | C rival markup | C pair markup | spillover (C rivals − A) | pair excess (C pair − A) |",
          "|---|---|---|---|---|---|"]
    md += [f"| {b['rounds']} | {b['A_markup']:+.2f} | {b['C_rival_markup']:+.2f} | {b['C_pair_markup']:+.2f} | "
           f"{f(b['spillover'])} | {f(b['pair_excess'])} |" for b in blocks]
    md += ["", f"Verdict: **{verdict}** ({res['rule']})"]
    (od / f"spillover_{a.name}.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
