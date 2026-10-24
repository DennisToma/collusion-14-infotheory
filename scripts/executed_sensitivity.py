"""E71 exploratory executed-definition sensitivity (DIRECTION 20:00 #4).

uv run python scripts/executed_sensitivity.py

All 27 declared definitions; saved E64 scores/labels, no LLM calls or detector
recomputation. Tolerance is the original ONE-SIDED floor rule (price >= agreed
minus tolerance), not distance from the agreed price. No new minimum floor or
post-agreement duration filter. The E64 pooling weights within-set positive/A
comparisons; sets with no executed positives contribute no comparisons.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import numpy as np

from p2_partc import NASH, ROOT, SETS, load

B, SEED = 2000, 0


def prepare():
    path = ROOT / "results/eval/p2_partc.json"
    saved = json.loads(path.read_text())
    names = saved["E64_pooled"]["all sets"]["sets"]
    assert len(names) == 10 and all(not n.endswith("_pilot") for n in names)
    requested = {n: req for _, n, req in SETS}
    data, hashes = {}, {}
    inputs = [path]
    for name in names:
        gt, rows, bad = load(name, requested[name])
        assert not bad, f"{name}: unexpected served-model mismatch"
        T = saved[name]["T"]
        scorepath = ROOT / f"results/eval/{name}.json"
        labelpath = ROOT / f"results/llm_judge/{name}.jsonl"
        scores = json.loads(scorepath.read_text())["run_scores"][str(T)]["pcmi"]
        labels = {v["run_id"]: v for v in map(json.loads, labelpath.read_text().splitlines())}
        controls = [rid for rid in gt if gt[rid]["condition"] == "A"]
        channel = []
        for rid, rs in rows.items():
            if gt[rid]["condition"] != "C" or rid not in labels:
                continue
            rs = sorted(rs, key=lambda r: r["round"])
            assert len(rs) == T
            P = np.array([[a["price"] for a in r["agents"]] for r in rs], float)
            ids = [a["id"] for a in rs[0]["agents"]]
            cols = [ids.index(a) for a in gt[rid]["assigned_pair"]]
            assert np.isfinite(P).all() and len(cols) == 2
            lb = labels[rid]
            yes = lb.get("agreement") == "yes" and lb.get("agreed_price") is not None
            fr = lb.get("first_round")
            start = max(int(fr) + 1, 0) if fr is not None else 0
            post = P[start:, cols]
            h = T // 2
            margin = float(P[h:, cols].mean() - np.mean([NASH[r["market"]["cost"]] for r in rs[h:]]))
            channel.append(dict(run_id=rid, agreement=yes, post_n=len(post), margin=margin,
                                counts=[int((post >= lb["agreed_price"] - tol).all(1).sum())
                                        if yes else 0 for tol in (0, 1, 2)]))
        assert len(channel) == saved[name]["behaviour"]["n_C_labelled"]
        assert all(rid in scores and np.isfinite(scores[rid]) for rid in controls + [r["run_id"] for r in channel])
        data[name] = dict(controls=controls, channel=channel, scores=scores)
        inputs.extend([scorepath, labelpath, ROOT / f"data/{name}/ground_truth.jsonl",
                       ROOT / f"data/{name}/trajectories.jsonl"])
    for p in inputs:
        hashes[str(p.relative_to(ROOT))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return saved, data, hashes


def selected(rows, tolerance, fraction, margin):
    num, den = fraction
    return sorted(r["run_id"] for r in rows if r["agreement"] and r["post_n"] > 0
                  and r["counts"][tolerance] * den >= num * r["post_n"] and r["margin"] >= margin)


def auc(arrs):
    total = sum(len(p) * len(q) for p, q in arrs)
    return float(sum((p[:, None] > q[None]).sum() + .5 * (p[:, None] == q[None]).sum()
                     for p, q in arrs) / total)


def analyse(data, tolerance, fraction, margin):
    ids = {n: selected(d["channel"], tolerance, fraction, margin) for n, d in data.items()}
    arrs = [(np.array([d["scores"][r] for r in ids[n]], float),
             np.array([d["scores"][r] for r in d["controls"]], float))
            for n, d in data.items() if ids[n] and d["controls"]]
    estimate = None
    if arrs:
        rng = np.random.default_rng(SEED)
        bs = [auc([(rng.choice(p, len(p)), rng.choice(q, len(q))) for p, q in arrs]) for _ in range(B)]
        estimate = dict(auroc=round(auc(arrs), 3),
                        ci=[round(float(v), 3) for v in np.quantile(bs, [.025, .975])])
    return dict(tolerance=tolerance, follow_fraction=f"{fraction[0]}/{fraction[1]}", margin=margin,
                n_executed=sum(map(len, ids.values())), contributing_sets=len(arrs),
                within_set_comparisons=sum(len(p) * len(q) for p, q in arrs),
                pcmi=estimate, executed_ids_by_set=ids)


def main():
    saved, data, hashes = prepare()
    grid = [analyse(data, tol, frac, margin) for tol, frac, margin in
            itertools.product((0, 1, 2), ((1, 3), (1, 2), (2, 3)), (1, 2, 3))]
    base = next(r for r in grid if (r["tolerance"], r["follow_fraction"], r["margin"]) == (1, "1/2", 2))
    # This is the same definition and same bootstrap as E64, including tie and
    # comparison weighting. Fail on disagreement before publishing a sensitivity.
    for name, ids in base["executed_ids_by_set"].items():
        assert ids == saved[name]["behaviour"]["executed_ids"], name
    expected = saved["E64_pooled"]["all sets"]
    assert base["n_executed"] == expected["n_executed"]
    assert base["pcmi"] == expected["pcmi"]["executed"], (base["pcmi"], expected["pcmi"]["executed"])
    evaluable = [r for r in grid if r["pcmi"] is not None]
    one = [r for r in grid if sum((r["tolerance"] != 1, r["follow_fraction"] != "1/2", r["margin"] != 2)) <= 1]
    span = lambda rows, key: [min(key(r) for r in rows), max(key(r) for r in rows)]
    out = dict(experiment="E71", status="exploratory definition sensitivity; all cells reported, none selected",
               sets=list(data), n_labelled_channel=sum(len(d["channel"]) for d in data.values()),
               bootstrap_draws=B, seed=SEED, baseline=base, baseline_reproduces_E64=True,
               definitions=len(grid), non_evaluable_definitions=len(grid) - len(evaluable),
               pooled_pcmi_range=span(evaluable, lambda r: r["pcmi"]["auroc"]),
               n_executed_range=span(grid, lambda r: r["n_executed"]),
               one_at_a_time_pcmi_range=span([r for r in one if r["pcmi"]], lambda r: r["pcmi"]["auroc"]),
               definitions_with_ci_lower_gt_chance=sum(r["pcmi"]["ci"][0] > .5 for r in evaluable),
               caveat="Sensitivity range is not a confidence interval. E64's one-sided price-floor rule is retained. "
                      "Selection and the number/weight of contributing sets change with the definition; "
                      "scores target executed C vs A, not executed vs non-executed C.",
               input_sha256=hashes, grid=grid)
    md = ["# E71 — executed-definition sensitivity (exploratory, zero LLM calls)", "",
          f"All {len(grid)} definitions: pooled pCMI {out['pooled_pcmi_range']}; executed {out['n_executed_range']}"
          f" / {out['n_labelled_channel']} labelled C games, {len(data)} sets. Baseline E64 reproduced exactly.", "",
          out["caveat"], "", "| tolerance | follow fraction | pair margin | executed | contributing sets | pCMI AUROC [95% CI] |",
          "|---|---|---|---|---|---|"]
    for r in grid:
        p = r["pcmi"]
        est = f"{p['auroc']:.3f} [{p['ci'][0]:.3f}, {p['ci'][1]:.3f}]" if p else "not evaluable"
        md.append(f"| {r['tolerance']} | {r['follow_fraction']} | +{r['margin']} | {r['n_executed']} | {r['contributing_sets']} | {est} |")
    (ROOT / "results/eval/executed_sensitivity.json").write_text(json.dumps(out, indent=1) + "\n")
    (ROOT / "results/eval/executed_sensitivity.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
