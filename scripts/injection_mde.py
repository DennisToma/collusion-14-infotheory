"""E30 (exploratory, post-hoc; not a headline): minimum detectable coordinated variation for pCMI on real LLM backgrounds.

Semi-synthetic: take each no-channel LLM control game, pick one random pair, and add the same integer move
z_t in {-1, 0, +1} (P(z_t = +1) = P(z_t = -1) = q/2) to both sellers' prices in every round. The rest of the game
(the other two sellers, the state, the sellers' own noise) is the real LLM data. Frozen detectors (score_run).
Metrics per (dataset, T, q): run AUROC of max-pair pCMI, injected vs the same games un-injected (bootstrap CI over
games), and top-1 localisation of the planted pair (vs chance 1/6).
Observed side: co-movement excess of the assigned pair in channel games (fraction of rounds where both sellers move in
the same direction, minus the mean over the 5 rival pairs), compared with the same statistic on injected controls.

    uv run python scripts/injection_mde.py     # -> results/eval/injection_mde.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from detectors.infotheory import PAIR_NAMES, PAIRS, score_run  # noqa: E402
from experiments.llm_eval import ROOT, arrays, auroc_ci, load  # noqa: E402

QS = (0.0, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0)
REPS = 10


def comove(P, i, j):
    d = np.diff(P, axis=0)
    return float(np.mean((d[:, i] * d[:, j]) > 0))


def comove_excess(P, pair):
    i, j = pair
    rivals = [comove(P, a, b) for a, b in PAIRS if (a, b) != (i, j)]
    return comove(P, i, j) - float(np.mean(rivals))


def pcmi_scores(P, S):
    r = score_run(P, S, B=0)
    return {n: r[n]["score"]["pcmi"] for n in PAIR_NAMES}


def run(name, conds, T, ctrl_conds, seed=0):
    _, gt, rows = load(name)
    ctrl = sorted(r for r in rows if gt[r]["condition"] in ctrl_conds and len(rows[r]) >= T)
    rng = np.random.default_rng(seed)
    base = {}
    for rid in ctrl:
        P, S, _ = arrays(rows[rid][:T])
        base[rid] = (P, S, max(pcmi_scores(P, S).values()))
    out = {"dataset": name, "T": T, "controls": ctrl_conds, "n_controls": len(ctrl), "by_q": {}}
    neg = [base[r][2] for r in ctrl]
    for q in QS:
        pos, top1, cmx = [], [], []
        for rid in ctrl:
            P, S, _ = base[rid]
            for _ in range(REPS):
                k = int(rng.integers(6))
                i, j = PAIRS[k]
                z = rng.choice([-1, 0, 1], size=T, p=[q / 2, 1 - q, q / 2])
                Pi = P.copy()
                Pi[:, i] += z
                Pi[:, j] += z
                sc = pcmi_scores(Pi, S)
                pos.append(max(sc.values()))
                best = max(sc.values())
                tied = [n for n in PAIR_NAMES if sc[n] >= best - 1e-12]
                top1.append(rng.choice(tied) == PAIR_NAMES[k])
                cmx.append(comove_excess(Pi, (i, j)))
        # one score per game (mean over reps) so the bootstrap is over games, not reps
        pos_g = np.array(pos).reshape(len(ctrl), REPS).mean(1)
        a, ci = auroc_ci(list(pos_g), neg)
        out["by_q"][str(q)] = {"auroc_game_mean": a, "auroc_ci": ci,
                               "auroc_all_reps": auroc_ci(pos, neg)[0],
                               "top1": float(np.mean(top1)), "comove_excess_mean": float(np.mean(cmx))}
        print(f"{name} T={T} {''.join(ctrl_conds)} q={q:.2f}: AUROC {a:.2f} {np.round(ci, 2)} "
              f"top1 {np.mean(top1):.2f} comove_excess {np.mean(cmx):+.3f}")
    obs = {}
    for c in conds:
        rids = [r for r in rows if gt[r]["condition"] == c and len(rows[r]) >= T]
        v = []
        for rid in rids:
            P, _, ids = arrays(rows[rid][:T])
            pr = tuple(sorted(ids.index(a) for a in gt[rid]["assigned_pair"]))
            v.append(comove_excess(P, pr))
        v = np.array(v)
        bs = np.random.default_rng(1).choice(v, size=(5000, len(v))).mean(1)
        obs[c] = {"n": len(v), "comove_excess_mean": float(v.mean()),
                  "ci": [float(np.quantile(bs, .025)), float(np.quantile(bs, .975))]}
        print(f"  observed {c}: assigned-pair co-move excess {v.mean():+.3f} {np.round(obs[c]['ci'], 3)} (n={len(v)})")
    out["observed"] = obs
    return out


if __name__ == "__main__":
    res = [run("llm_v1", "C", 20, "A"), run("llm_v1", "D", 20, "B"),
           run("llm_long", "C", 20, "A"), run("llm_long", "C", 50, "A")]
    json.dump(res, open(ROOT / "results" / "eval" / "injection_mde.json", "w"), indent=1)
