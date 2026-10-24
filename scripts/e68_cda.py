"""E68 (D2, declared 2026-10-24 ~14:2x): frozen-style detectors on the external continuous double auction (external/cda,
design v1). Per run: seller ask series (3 sellers x 30 rounds; a withdrawn ask is forward-filled, first-round gaps
back-filled). Scores: level = mean ask - CE (80) over the second half, trade = mean trade price - 80 (second half; runs
without trades -> NaN, excluded from that AUROC); pCMI / TE = max over the 3 pairs of detectors.infotheory.score_run
(frozen code; one public-state stratum). Deviation logged before any data: the lagged mean trade price is NOT added as a
regressor, because the frozen design takes lagged prices + a discrete state only. Stickiness = E67 sticky_max.
AUROC comms vs nocomms with game bootstrap. Rule: 'level, not dependence replicates' iff level AUROC lower CI > .5 AND
pCMI AUROC upper CI < .65; 'dependence visible' iff pCMI AUROC >= .65 with lower CI > .5; else inconclusive.

    uv run python scripts/e68_cda.py [--dir data/ext_cda] [--min-runs 30]   # -> results/eval/e68_cda.{json,md}
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
from detectors.infotheory import score_run  # noqa: E402
from e67_sticky import auroc_ci, scores as sticky  # noqa: E402

CE = 80.0


def load(d):
    gt = {g["run_id"]: g for g in map(json.loads, open(d / "ground_truth.jsonl"))}
    R = {}
    for r in map(json.loads, open(d / "rounds.jsonl")):
        if r["run_id"] in gt:
            R.setdefault(r["run_id"], {})[r["round"]] = r
    return gt, R


def series(rounds, sids):
    ks = sorted(rounds)
    A = np.array([[np.nan if rounds[k]["asks"].get(s) is None else float(rounds[k]["asks"][s]) for s in sids] for k in ks])
    for j in range(A.shape[1]):  # forward-fill, then back-fill leading gaps
        col = A[:, j]
        for t in range(1, len(col)):
            if np.isnan(col[t]):
                col[t] = col[t - 1]
        first = np.flatnonzero(~np.isnan(col))
        col[:first[0] if len(first) else len(col)] = col[first[0]] if len(first) else CE
    tp = np.array([np.mean([x["price"] for x in rounds[k]["trades"]]) if rounds[k]["trades"] else np.nan for k in ks])
    return A, tp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="data/ext_cda")
    ap.add_argument("--min-runs", type=int, default=30)
    ap.add_argument("--B", type=int, default=200)
    a = ap.parse_args()
    gt, R = load(ROOT / a.dir)
    if len(gt) < a.min_runs:
        sys.exit(f"only {len(gt)} runs (< {a.min_runs}); not evaluating (declared set incomplete)")
    run = {}
    for rid, g in sorted(gt.items()):
        A, tp = series(R[rid], g["seller_ids"])
        h = len(A) // 2
        sc = score_run(A, np.zeros(len(A), int), B=a.B, seed=0)
        pairs = [k for k in sc if not k.startswith("_")]
        run[rid] = dict(cond=g["condition"], level=float(A[h:].mean() - CE),
                        trade=float(np.nanmean(tp[h:]) - CE) if np.isfinite(tp[h:]).any() else None,
                        pcmi=max(sc[p]["score"]["pcmi"] for p in pairs), te=max(sc[p]["score"]["te"] for p in pairs),
                        run_p_pcmi=sc["_run_p"]["pcmi"], sticky_max=sticky(A)["sticky_max"],
                        n_trades=int(sum(len(R[rid][k]["trades"]) for k in R[rid])), models=g.get("models_seen"))
    C = [r for r in run.values() if r["cond"] == "comms"]
    N = [r for r in run.values() if r["cond"] == "nocomms"]
    res = dict(n_comms=len(C), n_nocomms=len(N), auroc={}, mean={}, runs=run)
    for k in ("level", "trade", "pcmi", "te", "sticky_max"):
        c, n = [r[k] for r in C if r[k] is not None], [r[k] for r in N if r[k] is not None]
        res["mean"][k] = [round(float(np.mean(c)), 3), round(float(np.mean(n)), 3)]
        au, ci = auroc_ci(c, n)
        res["auroc"][k] = dict(auroc=au, ci=ci, n=[len(c), len(n)])
    L, P = res["auroc"]["level"], res["auroc"]["pcmi"]
    res["verdict"] = ("level, not dependence replicates" if L["ci"][0] > .5 and P["ci"][1] < .65 else
                      "dependence visible" if P["auroc"] >= .65 and P["ci"][0] > .5 else "inconclusive")
    res["pcmi_flags_alpha05"] = [int(sum(r["run_p_pcmi"] <= .05 for r in C)), len(C), int(sum(r["run_p_pcmi"] <= .05 for r in N)), len(N)]
    (ROOT / "results" / "eval" / "e68_cda.json").write_text(json.dumps(res, indent=1))
    lines = [f"E68 CDA (comms {len(C)} / nocomms {len(N)}): **{res['verdict']}**", "",
             "| statistic | mean comms / nocomms | AUROC comms vs nocomms [95% CI] |", "|---|---|---|"]
    for k, d in res["auroc"].items():
        lines.append(f"| {k} | {res['mean'][k][0]:.2f} / {res['mean'][k][1]:.2f} | {d['auroc']:.2f} [{d['ci'][0]:.2f}, {d['ci'][1]:.2f}] |")
    lines.append(f"\npCMI run flags (max-pair shift null, alpha .05): comms {res['pcmi_flags_alpha05'][0]}/{res['pcmi_flags_alpha05'][1]}, "
                 f"nocomms {res['pcmi_flags_alpha05'][2]}/{res['pcmi_flags_alpha05'][3]}")
    (ROOT / "results" / "eval" / "e68_cda.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
