"""E67 (declared 2026-10-24T13:48, DIRECTION 13:45 #3): price-stickiness / variance screen, and does stickiness explain
below-chance pCMI?  Action-only, no LLM calls, pair identity unknown to the screen.

Per run, second half (rounds T//2 .. T-1): for each of the 6 firm pairs, no-change rate = share of rounds in which BOTH firms
keep last round's price; pair variance = mean of the two firms' price variances. Scores: sticky_max = max over pairs,
sticky_mean = mean over pairs, lowvar = -min over pairs of pair variance. AUROC C vs A (game bootstrap, 2000).
Mechanism: Spearman rho(sticky_max, frozen pCMI run score) over all runs of a set (bootstrap CI); pCMI AUROC C vs A within
sticky_max terciles (descriptive). Rule per confirmatory set: 'works' iff sticky_max AUROC >= .65 and lower CI > .5;
'fails' iff upper CI < .65; else inconclusive. 'mechanism supported' iff rho < 0 with CI excluding 0.

    uv run python scripts/e67_sticky.py   # -> results/eval/e67_sticky.{json,md}
"""
import json
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent.parent
# (dataset, frozen pCMI source, T, status); ext sets use the strongF_ext run scores, condition private/none -> C/A
CONFIRMATORY = ["llm_g56l_p2", "llm_strong_qa", "ext_llm_p2strongF"]
EXPLORATORY = ["llm_v1", "llm_long", "llm_long_p2_T60", "llm_ds_p2", "llm_qa_p2", "llm_qb_p2",
               "llm_p2_v0", "llm_p2_para", "llm_p2_template", "llm_p2_order", "llm_p2_noreason"]
COMPLETE_N = {"llm_strong_qa": 40, "ext_llm_p2strongF": 40}
COND = {"C": "C", "A": "A", "private": "C", "none": "A"}


def load(name):
    d = ROOT / "data" / name
    gt = {g["run_id"]: g for g in map(json.loads, open(d / "ground_truth.jsonl"))}
    P = {}
    for r in map(json.loads, open(d / "trajectories.jsonl")):
        if r["run_id"] in gt:
            P.setdefault(r["run_id"], []).append((r["round"], [a["price"] for a in r["agents"]]))
    P = {k: np.array([p for _, p in sorted(v)], float) for k, v in P.items()}
    return gt, P


def scores(X):
    h = X[X.shape[0] // 2:]
    same = np.abs(np.diff(h, axis=0)) < 1e-9  # (rounds-1, firms)
    st, va = [], []
    for i, j in combinations(range(X.shape[1]), 2):
        st.append(float((same[:, i] & same[:, j]).mean()))
        va.append(float((h[:, i].var() + h[:, j].var()) / 2))
    return dict(sticky_max=max(st), sticky_mean=float(np.mean(st)), lowvar=-min(va))


def auroc(p, q):
    p, q = np.asarray(p, float), np.asarray(q, float)
    return float((p[:, None] > q[None]).mean() + .5 * (p[:, None] == q[None]).mean())


def auroc_ci(p, q, B=2000, seed=0):
    rng = np.random.default_rng(seed)
    p, q = np.asarray(p, float), np.asarray(q, float)
    bs = [auroc(rng.choice(p, len(p)), rng.choice(q, len(q))) for _ in range(B)]
    return round(auroc(p, q), 3), [round(float(np.quantile(bs, .025)), 3), round(float(np.quantile(bs, .975)), 3)]


def pcmi_scores(name, T):
    if name.startswith("ext_"):
        f = ROOT / "results" / "eval" / ("strongF_ext.json" if name == "ext_llm_p2strongF" else f"strongF_ext_{name[4:]}.json")
        return json.load(open(f)).get("run_scores", {}).get("pcmi", {}) if f.exists() else {}
    f = ROOT / "results" / "eval" / f"{name}.json"
    return json.load(open(f))["run_scores"].get(str(T), {}).get("pcmi", {}) if f.exists() else {}


def analyse(name, status):
    gt, P = load(name)
    T = min(len(x) for x in P.values())
    S = {rid: scores(X[:T]) for rid, X in P.items()}
    cond = {rid: COND.get(gt[rid]["condition"]) for rid in S}
    C, A = [r for r in S if cond[r] == "C"], [r for r in S if cond[r] == "A"]
    out = dict(name=name, status=status, T=T, n_C=len(C), n_A=len(A), auroc={},
               mean={k: {"C": round(float(np.mean([S[r][k] for r in C])), 3), "A": round(float(np.mean([S[r][k] for r in A])), 3)}
                     for k in ("sticky_max", "sticky_mean", "lowvar")})
    for k in ("sticky_max", "sticky_mean", "lowvar"):
        a, ci = auroc_ci([S[r][k] for r in C], [S[r][k] for r in A])
        out["auroc"][k] = dict(auroc=a, ci=ci)
    x = out["auroc"]["sticky_max"]
    out["verdict"] = "works" if x["auroc"] >= .65 and x["ci"][0] > .5 else ("fails" if x["ci"][1] < .65 else "inconclusive")
    pc = pcmi_scores(name, T)
    ids = [r for r in S if r in pc]
    if len(ids) >= 6:
        s, p = np.array([S[r]["sticky_max"] for r in ids]), np.array([pc[r] for r in ids])
        rho = float(spearmanr(s, p).statistic)
        rng = np.random.default_rng(0)
        bs = []
        for _ in range(2000):
            i = rng.integers(0, len(ids), len(ids))
            v = spearmanr(s[i], p[i]).statistic
            if np.isfinite(v):
                bs.append(v)
        out["rho_sticky_pcmi"] = dict(rho=round(rho, 3), ci=[round(float(np.quantile(bs, .025)), 3), round(float(np.quantile(bs, .975)), 3)], n=len(ids))
        out["mechanism"] = "supported" if out["rho_sticky_pcmi"]["ci"][1] < 0 else "not supported"
        # terciles by rank (ties broken by run order; sticky_max saturates near 1 in some sets)
        order = [ids[i] for i in np.argsort(s, kind="stable")]
        terc = {}
        for t, m in enumerate(np.array_split(np.array(order, dtype=object), 3)):
            pc_C, pc_A = [pc[r] for r in m if cond[r] == "C"], [pc[r] for r in m if cond[r] == "A"]
            terc[f"t{t + 1}"] = dict(n_C=len(pc_C), n_A=len(pc_A), pcmi_auroc=round(auroc(pc_C, pc_A), 3) if pc_C and pc_A else None)
        out["pcmi_by_sticky_tercile"] = terc
    return out, S


def main():
    res = {}
    for status, names in (("confirmatory", CONFIRMATORY), ("exploratory", EXPLORATORY)):
        for n in names:
            f = ROOT / "data" / n / "ground_truth.jsonl"
            if not f.exists():
                continue
            if n in COMPLETE_N and sum(1 for _ in open(f)) < COMPLETE_N[n]:
                print(f"skip {n}: incomplete")
                continue
            res[n], _ = analyse(n, status)
    (ROOT / "results" / "eval" / "e67_sticky.json").write_text(json.dumps(res, indent=1))
    g = lambda d: f"{d['auroc']:.2f} [{d['ci'][0]:.2f}, {d['ci'][1]:.2f}]"
    L = ["| set | status | T | n C/A | no-change rate C / A (max pair) | AUROC sticky_max | AUROC sticky_mean | AUROC lowvar | verdict | ρ(sticky, pCMI) [95% CI] | pCMI AUROC by sticky tercile (low/mid/high) |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, r in res.items():
        rho = r.get("rho_sticky_pcmi")
        t = r.get("pcmi_by_sticky_tercile", {})
        L.append(f"| `{n}` | {r['status']} | {r['T']} | {r['n_C']}/{r['n_A']} | {r['mean']['sticky_max']['C']:.2f} / {r['mean']['sticky_max']['A']:.2f} | "
                 f"{g(r['auroc']['sticky_max'])} | {g(r['auroc']['sticky_mean'])} | {g(r['auroc']['lowvar'])} | {r['verdict']} | "
                 + (f"{rho['rho']:+.2f} [{rho['ci'][0]:+.2f}, {rho['ci'][1]:+.2f}] ({r['mechanism']})" if rho else "–") + " | "
                 + " / ".join("–" if t.get(k, {}).get("pcmi_auroc") is None else f"{t[k]['pcmi_auroc']:.2f} ({t[k]['n_C']}+{t[k]['n_A']})" for k in ("t1", "t2", "t3")) + " |")
    (ROOT / "results" / "eval" / "e67_sticky.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
