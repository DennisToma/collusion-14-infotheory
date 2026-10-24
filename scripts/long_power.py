"""E55 (Phase 2 gap 2, directive 1): does pCMI fail on LLM data for lack of rounds? Declared in EXPERIMENTS.tsv before
any llm_long_p2 detector output was computed.

    uv run python scripts/long_power.py [--name llm_long_p2] [--Ts 10,20,30,40,50,60]   # -> results/eval/long_power_<name>.{json,md}

(a) prefix power: run AUROC C vs A (game bootstrap CI) of max-pair pCMI, max-pair markup over Nash and max-pair pair_level
    on the first T rounds of every completed game (frozen detectors, score_run B=0 scores).
(b) injection sensitivity (E30 method, scripts/injection_mde.run) on the A controls at T=20/40/60: single-planting pCMI AUROC vs
    the rate q of a planted shared +-1 price offset; q80(T) = smallest grid q with AUROC >= .80 (a grid crossing of a
    discrimination curve, not a power-based MDE); observed assigned-pair co-move excess in C games.
Primary decision: the E44 rule declared before generation (see the code); (b) and (c) are supporting.
(c) decay: per-round assigned-pair premium (pair mean - mean of the two rivals) in C games, 10-round bins (game-bootstrap
    CI) and the mean per-game OLS slope of premium on round (CI).
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
from scripts import injection_mde  # noqa: E402

DETS = ("pcmi", "pair_markup", "pair_level")


def auc(pos, neg):
    pos, neg = np.asarray(pos)[:, None], np.asarray(neg)[None, :]
    return float(np.mean((pos > neg) + 0.5 * (pos == neg)))


def run_scores(P, S, nash):
    r = score_run(P, S, B=0)
    out = {"pcmi": max(r[n]["score"]["pcmi"] for n in PAIR_NAMES)}
    pm, pl = [], []
    for i, j in PAIRS:
        others = [k for k in range(4) if k not in (i, j)]
        pm.append(float((P[:, [i, j]] - nash[:, None]).mean()))
        pl.append(float(P[:, [i, j]].mean() - P[:, others].mean()))
    out["pair_markup"], out["pair_level"] = max(pm), max(pl)
    return out


def boot_auc(pos, neg, B=2000, seed=0):
    """Full precision (decisions use these); rounding only in the Markdown."""
    rng = np.random.default_rng(seed)
    pos, neg = np.asarray(pos), np.asarray(neg)
    bs = [auc(rng.choice(pos, len(pos)), rng.choice(neg, len(neg))) for _ in range(B)]
    return [auc(pos, neg), [float(x) for x in np.percentile(bs, [2.5, 97.5])]]


def mean_ci(x, B=5000, seed=1):
    x = np.asarray(x, float)
    bs = np.random.default_rng(seed).choice(x, (B, len(x))).mean(1)
    return [float(x.mean()), [float(q) for q in np.percentile(bs, [2.5, 97.5])]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="llm_long_p2")
    ap.add_argument("--Ts", default="10,20,30,40,50,60")
    ap.add_argument("--mde-Ts", default="20,40,60")
    ap.add_argument("--declared-T", type=int, default=60, help="E44 primary horizon; must equal max(--Ts)")
    ap.add_argument("--declared-n", type=int, default=20, help="E44 games per condition (0 = no check, pilots)")
    a = ap.parse_args()
    Ts = [int(t) for t in a.Ts.split(",")]
    _, gt, rows = load(a.name)
    Tmax = max(Ts)
    if Tmax != a.declared_T:
        sys.exit(f"max(--Ts)={Tmax} != declared horizon {a.declared_T} (pass --declared-T for pilots)")
    games = {c: sorted(r for r in gt if gt[r]["condition"] == c and len(rows.get(r, [])) >= Tmax) for c in "AC"}
    if a.declared_n and any(len(v) != a.declared_n for v in games.values()):
        sys.exit(f"incomplete cohort {({c: len(v) for c, v in games.items()})}; declared n={a.declared_n} per condition")
    keep = set(games["A"]) | set(games["C"])
    rows = {r: v for r, v in rows.items() if r in keep}  # the injection analysis sees exactly the same games
    injection_mde.load = lambda name, _g=gt, _r=rows: (None, _g, _r)
    res = {"name": a.name, "n": {c: len(v) for c, v in games.items()}, "prefix": {}, "mde": {}, "decay": {}}
    # (a) prefix power
    for T in Ts:
        sc = {c: [] for c in "AC"}
        for c in "AC":
            for rid in games[c]:
                rs = rows[rid][:T]
                P, S, _ = arrays(rs)
                nash = np.array([NASH[r["market"]["cost"]] for r in rs], float)
                sc[c].append(run_scores(P, S, nash))
        res["prefix"][str(T)] = {d: boot_auc([s[d] for s in sc["C"]], [s[d] for s in sc["A"]]) for d in DETS}
        print(f"T={T}: " + "  ".join(f"{d} {v[0]:.2f} [{v[1][0]:.2f},{v[1][1]:.2f}]" for d, v in res["prefix"][str(T)].items()))
    # (b) injection MDE on the A controls
    for T in (int(t) for t in a.mde_Ts.split(",")):
        if T > Tmax:
            continue
        m = injection_mde.run(a.name, "C", T, "A")
        mde = next((float(q) for q, v in m["by_q"].items() if v["auroc_single_planting"] >= 0.80), None)
        res["mde"][str(T)] = {"mde_q_auroc80": mde,
                              "by_q": {q: {"auroc": round(v["auroc_single_planting"], 3),
                                           "ci": [round(x, 3) for x in v["auroc_ci_game_cluster"]],
                                           "comove_excess_injected": round(v["comove_excess_mean"], 3)}
                                       for q, v in m["by_q"].items()},
                              "observed_C_comove_excess": m["observed"].get("C")}
    # (c) premium decay in C games
    prem, slopes = [], []
    for rid in games["C"]:
        rs = rows[rid][:Tmax]
        P, _, ids = arrays(rs)
        i, j = sorted(ids.index(x) for x in gt[rid]["assigned_pair"])
        others = [k for k in range(4) if k not in (i, j)]
        p = P[:, [i, j]].mean(1) - P[:, others].mean(1)
        prem.append(p)
        slopes.append(float(np.polyfit(np.arange(1, Tmax + 1), p, 1)[0]))
    prem = np.array(prem)
    res["decay"]["per_round_mean"] = [round(float(x), 3) for x in prem.mean(0)]
    res["decay"]["bins10"] = {f"{b + 1}-{b + 10}": mean_ci(prem[:, b:b + 10].mean(1)) for b in range(0, Tmax, 10)}
    res["decay"]["slope_per_round"] = mean_ci(slopes)
    last, first = prem[:, -10:].mean(1), prem[:, :10].mean(1)
    res["decay"]["last_minus_first_bin"] = mean_ci(last - first)
    res["decay"]["n_games_last_bin_below_half_first"] = int(np.sum(last < 0.5 * first))
    # PRIMARY decision = the E44 rule declared 06:29 (same as E20), at the amended horizon T=60:
    #   'too short' iff AUROC(pCMI,T) >= .65, CI lower > .5 and +.15 over the T=20 prefix;
    #   'level, not short' iff CI upper < .65 (moderate effects excluded); else inconclusive.
    # Supporting (E55, amended 08:15 before any E44 output): injection grid crossing q80 and co-move comparison.
    T60, T20 = res["prefix"].get(str(Tmax)), res["prefix"].get("20")
    m60 = res["mde"].get(str(Tmax), {})
    dec = {}
    if T60 and T20:
        a60, (lo, hi) = T60["pcmi"]
        dec["E44_rule"] = ("too_short" if a60 >= 0.65 and lo > 0.5 and a60 - T20["pcmi"][0] >= 0.15
                           else "level_not_short" if hi < 0.65 else "inconclusive")
    if m60.get("mde_q_auroc80") is not None and m60.get("observed_C_comove_excess"):
        # supporting only: observed upper CI below the excess of the SMALLEST planted grid point (q=.1)
        inj = m60["by_q"]["0.1"]["comove_excess_injected"]
        dec["observed_comove_upper_below_q0.1_planting"] = bool(m60["observed_C_comove_excess"]["ci"][1] < inj)
    sl, lf = res["decay"]["slope_per_round"], res["decay"]["last_minus_first_bin"]
    dec["collusion_decays"] = bool(sl[1][1] < 0 and lf[1][1] < 0)
    res["decision"] = dec
    out = ROOT / "results" / "eval" / f"long_power_{a.name}"
    json.dump(res, open(f"{out}.json", "w"), indent=1)
    md = [f"# E55 long-game power ({a.name}, n={res['n']})", "", "| T | " + " | ".join(DETS) + " |", "|---|" + "---|" * len(DETS)]
    for T, v in res["prefix"].items():
        md.append(f"| {T} | " + " | ".join(f"{v[d][0]:.2f} [{v[d][1][0]:.2f}, {v[d][1][1]:.2f}]" for d in DETS) + " |")
    md += ["", "q80 grid crossing (smallest planted q with single-planting AUROC >= .80), observed C co-move excess: " + json.dumps({T: (v["mde_q_auroc80"], v["observed_C_comove_excess"]) for T, v in res["mde"].items()}),
           "", "decay bins: " + json.dumps(res["decay"]["bins10"]), "slope: " + json.dumps(res["decay"]["slope_per_round"]),
           "last-first: " + json.dumps(res["decay"]["last_minus_first_bin"]), "", "decision: " + json.dumps(dec)]
    open(f"{out}.md", "w").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
