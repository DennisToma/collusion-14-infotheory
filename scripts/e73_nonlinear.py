"""E73 (robustness, declared; DIRECTION 02:15 #1; zero LLM calls): is the co-movement null an artefact of the
linear-Gaussian pCMI?

    uv run python scripts/e73_nonlinear.py      -> results/eval/e73_nonlinear.json

Two estimators, one configuration each (no tuning), next to the frozen linear pCMI; run score = max over the 6 pairs:
  (a) copula pCMI: each seller's price series is replaced by its normal scores (average ranks within the game,
      Phi^-1(rank / (T + 1))), then the identical design (const + state dummies + lagged transformed prices),
      residualisation and gauss_cmi_from_resid (detectors.infotheory.score_run, B=0).
  (b) sign MI: Miller-Madow CMI(sign dp_i ; sign dp_j | public state at t), alphabet {-, 0, +}, cmi_mm.
AUROCs use raw run scores, as the linear pCMI AUROCs in REPORT do (the within-run shift null only gives per-run
p-values and is not needed for a run AUROC). E44 / executed-only / planting use the bootstrap their linear numbers
used; E70 uses e72_te_diag.boot (same within cell x arm game resampling as e70_grid, different draw order: linear CI
[0.431, 0.590] vs saved [0.429, 0.589]). Linear point estimates are asserted to reproduce (E70 0.51, E44 0.34, exec 0.42).
Sensitivity: planted shared +-1 move (E30 method, scripts/injection_mde.run: 10 plantings per game, same seeds) at
q = 0.1 on the E44 no-channel controls at T = 20 and T = 60, all three estimators on the same plantings.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import norm, rankdata

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from detectors.infotheory import PAIR_NAMES, PAIRS, cmi_mm, score_run  # noqa: E402
from experiments.llm_eval import arrays, load  # noqa: E402
from e72_te_diag import auroc_strat, boot  # noqa: E402
from long_power import boot_auc  # noqa: E402
import executed_sensitivity as es  # noqa: E402

EST = ("pcmi", "copula_pcmi", "sign_mi")


def normal_scores(P):
    T = len(P)
    return np.column_stack([norm.ppf(rankdata(P[:, k]) / (T + 1)) for k in range(P.shape[1])])


def scores(P, S, per_pair=False):
    lin = score_run(P, S, B=0)
    cop = score_run(normal_scores(P), S, B=0)
    sg = np.sign(np.diff(P, axis=0))
    St = S[1:]
    return {"pcmi": max(lin[n]["score"]["pcmi"] for n in PAIR_NAMES),
            "copula_pcmi": max(cop[n]["score"]["pcmi"] for n in PAIR_NAMES),
            "sign_mi": max(cmi_mm(sg[:, i], sg[:, j], St) for i, j in PAIRS),
            **({"_lin_pairs": {n: lin[n]["score"]["pcmi"] for n in PAIR_NAMES}} if per_pair else {})}


def rnd(a, ci):
    return {"auroc": round(float(a), 3), "ci": [round(float(c), 3) for c in ci]}


def e70():
    e = json.load(open(ROOT / "results/eval/e70_grid.json"))
    rows = {}
    for cell in sorted({g["cell"] for g in e["games"]}):
        for r in map(json.loads, open(ROOT / "data" / f"llm_grid_p2_{cell}" / "trajectories.jsonl")):
            rows.setdefault(r["run_id"], []).append(r)
    games, dev = [], 0.0
    for g0 in e["games"]:
        P, S, _ = arrays(sorted(rows[g0["run_id"]], key=lambda r: r["round"]))
        sc = scores(P, S)
        dev = max(dev, abs(sc["pcmi"] - g0["scores"]["pcmi"]))
        games.append(dict(cell=g0["cell"], channel=g0["channel"], **sc))
    assert dev < 1e-9, f"E70 linear pCMI not reproduced ({dev})"
    out = {k: rnd(auroc_strat(games, k), boot(games, lambda b, k=k: auroc_strat(b, k))) for k in EST}
    out["n"] = len(games)
    return out


def e44(T=60):
    _, gt, rows = load("llm_long_p2")
    sc = {c: [scores(*arrays(rows[r][:T])[:2]) for r in sorted(gt) if gt[r]["condition"] == c and len(rows.get(r, [])) >= T]
          for c in "AC"}
    out = {"n_C": len(sc["C"]), "n_A": len(sc["A"])}
    for k in EST:
        a, ci = boot_auc([s[k] for s in sc["C"]], [s[k] for s in sc["A"]])
        out[k] = rnd(a, ci)
    return out


def executed():
    saved = json.load(open(ROOT / "results/eval/p2_partc.json"))
    req = {n: r for _, n, r in es.SETS}
    per = {k: [] for k in EST}
    n_exec = 0
    for name in saved["E64_pooled"]["all sets"]["sets"]:
        gt, rows, bad = es.load(name, req[name])
        assert not bad
        T = saved[name]["T"]
        ex = saved[name]["behaviour"]["executed_ids"]
        ctrl = [r for r in gt if gt[r]["condition"] == "A"]
        if not ex or not ctrl:
            continue
        n_exec += len(ex)
        sc = {r: scores(*arrays(sorted(rows[r], key=lambda x: x["round"])[:T])[:2]) for r in ex + ctrl}
        for k in EST:
            per[k].append((np.array([sc[r][k] for r in ex]), np.array([sc[r][k] for r in ctrl])))
    out = {"n_executed": n_exec, "sets_contributing": len(per["pcmi"])}
    for k in EST:
        rng = np.random.default_rng(es.SEED)
        bs = [es.auc([(rng.choice(p, len(p)), rng.choice(q, len(q))) for p, q in per[k]]) for _ in range(es.B)]
        out[k] = rnd(es.auc(per[k]), np.quantile(bs, [.025, .975]))
    return out


def sensitivity(T, q=0.1, reps=10, seed=0):
    """Same procedure and RNG stream as scripts/injection_mde.run (one control order, 10 plantings per game)."""
    _, gt, rows = load("llm_long_p2")
    ctrl = sorted(r for r in rows if gt[r]["condition"] == "A" and len(rows[r]) >= T)
    rng = np.random.default_rng(seed)
    base = {r: arrays(rows[r][:T])[:2] for r in ctrl}
    neg = {r: scores(*base[r]) for r in ctrl}
    pos = {k: np.zeros((len(ctrl), reps)) for k in EST}
    for qq in (0.0, q):  # injection_mde.run loops QS = (0.0, 0.1, ...) on one RNG; replay q = 0 to reach the same draws
        for gi, r in enumerate(ctrl):
            P, S = base[r]
            for rep in range(reps):
                i, j = PAIRS[int(rng.integers(6))]
                z = rng.choice([-1, 0, 1], size=T, p=[qq / 2, 1 - qq, qq / 2])
                Pi = P.copy()
                Pi[:, i] += z
                Pi[:, j] += z
                sc = scores(Pi, S, per_pair=True)
                lp = sc["_lin_pairs"]
                rng.choice([n for n in PAIR_NAMES if lp[n] >= max(lp.values()) - 1e-12])  # same tie-break draw
                if qq == q:
                    for k in EST:
                        pos[k][gi, rep] = sc[k]
    out = {"T": T, "q": q, "n_controls": len(ctrl)}
    for k in EST:
        pm, ng = pos[k], np.array([neg[r][k] for r in ctrl])
        a = lambda p, n: float(np.mean((p.ravel()[:, None] > n[None]) + .5 * (p.ravel()[:, None] == n[None])))
        brng = np.random.default_rng(2)
        bs = []
        for _ in range(2000):
            g = brng.integers(len(ctrl), size=len(ctrl))
            bs.append(a(pm[g], ng[g]))
        out[k] = rnd(a(pm, ng), np.quantile(bs, [.025, .975]))
    return out


def main():
    res = {"experiment": "E73", "status": "robustness, declared before computing (EXPERIMENTS.tsv E73-declared, STATUS iter 61)",
           "estimators": {"pcmi": "frozen linear-Gaussian pCMI (reference)",
                          "copula_pcmi": "normal-score rank transform per seller, then identical pCMI",
                          "sign_mi": "Miller-Madow CMI(sign dp_i; sign dp_j | public state)"},
           "E70": e70(), "E44_T60": e44(60), "executed_only": executed(),
           "sensitivity_q0.1": [sensitivity(20), sensitivity(60)]}
    ref = {"E70": 0.51, "E44_T60": 0.34, "executed_only": 0.42}
    for sv, v in zip(res["sensitivity_q0.1"], (0.622, 0.79)):  # long_power_llm_long_p2_T60.json mde[T][0.1]
        assert abs(sv["pcmi"]["auroc"] - v) < 0.006, sv
    for s, v in ref.items():
        assert abs(res[s]["pcmi"]["auroc"] - v) < 0.006, (s, res[s]["pcmi"])
    fires = any(res[s][k]["ci"][0] > 0.5 for s in ("E70", "E44_T60") for k in ("copula_pcmi", "sign_mi"))
    res["branch"] = "finding: a nonlinear estimator detects co-movement" if fires else \
        "null: both nonlinear estimators' CIs include 0.5 (or lie below) on E70 and E44"
    (ROOT / "results/eval/e73_nonlinear.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
