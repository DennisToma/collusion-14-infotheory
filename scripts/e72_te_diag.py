"""E72 (exploratory, post hoc, zero LLM calls): what does E70's confirmed TE AUROC 0.62 mean?

  uv run python scripts/e72_te_diag.py      -> results/eval/e72_te_diag.{json,md}

Frozen TE estimator (detectors.infotheory: _te_pairs + gauss_cmi_from_resid, max over the two directions,
run score = max over the 6 pairs) on the saved E70 games (results/eval/e70_grid.json games[], 4 sellers).
(a) pair naming: share of channel games whose TE max pair is the assigned pair (uniform tie-break, seed 1),
    Wilson CI vs chance 1/6.
(b) timing: pooled within-cell C-vs-A TE AUROC (e70 auroc_strat) with the estimator re-run on rounds 1-10
    and on rounds 11-20; game-cluster bootstrap (within cell x arm) CI for late - early.
    Secondary: full-series residuals, lagged-residual correlation restricted to early / late target rounds.
(c) pooled TE AUROC of executed C vs A and of non-executed C vs A (E70 games[].executed).
Wording branches were pre-committed in STATUS (iteration 46) before this ran.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from detectors.infotheory import PAIR_NAMES, _te_pairs, gauss_cmi_from_resid  # noqa: E402
from experiments.llm_eval import arrays  # noqa: E402
from experiments.scripted import wilson  # noqa: E402

PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]


def te_scores(P, S, rows=None):
    """Per-pair TE (frozen estimator). rows: optional boolean mask over target rounds t=1..T-1 to restrict
    the residual correlation to (secondary timing analysis; residuals still fit on the full series)."""
    t_idx = np.arange(1, len(P))
    out = {}
    for (i, j), n in zip(PAIRS, PAIR_NAMES):
        v = []
        for a, b in _te_pairs(P, S, t_idx, i, j):
            if rows is not None:
                a, b = a[rows], b[rows]
                a, b = (a - a.mean()) / (a.std() + 1e-12), (b - b.mean()) / (b.std() + 1e-12)
            v.append(gauss_cmi_from_resid(a, b))
        out[n] = max(v)
    return out


def auroc_strat(games, key):
    num = den = 0.0
    for c in sorted({g["cell"] for g in games}):
        p = np.array([g[key] for g in games if g["cell"] == c and g["channel"]], float)
        q = np.array([g[key] for g in games if g["cell"] == c and not g["channel"]], float)
        if len(p) and len(q):
            num += (p[:, None] > q[None]).sum() + .5 * (p[:, None] == q[None]).sum()
            den += len(p) * len(q)
    return float(num / den)


def boot(games, fn, B=2000, seed=0):
    rng = np.random.default_rng(seed)
    groups = {}
    for g in games:
        groups.setdefault((g["cell"], g["channel"]), []).append(g)
    out = []
    for _ in range(B):
        bb = [v[i] for v in groups.values() for i in rng.integers(0, len(v), len(v))]
        out.append(fn(bb))
    return [round(float(np.quantile(out, .025)), 3), round(float(np.quantile(out, .975)), 3)]


def main():
    e70 = json.load(open(ROOT / "results" / "eval" / "e70_grid.json"))
    gts, rows = {}, {}
    for cell in sorted({g["cell"] for g in e70["games"]}):
        d = ROOT / "data" / f"llm_grid_p2_{cell}"
        gts.update({g["run_id"]: g for g in map(json.loads, open(d / "ground_truth.jsonl"))})
        for r in map(json.loads, open(d / "trajectories.jsonl")):
            rows.setdefault(r["run_id"], []).append(r)
    games, max_dev = [], 0.0
    rng_t = np.random.default_rng(1)
    for g0 in e70["games"]:
        rid = g0["run_id"]
        rs = sorted(rows[rid], key=lambda r: r["round"])
        assert [r["round"] for r in rs] == list(range(20)), rid
        P, S, ids = arrays(rs)
        full = te_scores(P, S)
        max_dev = max(max_dev, abs(max(full.values()) - g0["scores"]["te"]))  # must reproduce frozen score
        Pe, Se, _ = arrays(rs[:10])
        Pl, Sl, _ = arrays(rs[10:])
        t = np.arange(1, 20)
        g = dict(cell=g0["cell"], run_id=rid, channel=g0["channel"], executed=g0["executed"],
                 price_sd=float(P.std(0).mean()), change_share=float((np.diff(P, axis=0) != 0).mean()),
                 te=max(full.values()), te_early=max(te_scores(Pe, Se).values()),
                 te_late=max(te_scores(Pl, Sl).values()),
                 te_early_res=max(te_scores(P, S, t <= 9).values()), te_late_res=max(te_scores(P, S, t >= 10).values()))
        if g0["channel"]:
            pair = "".join(sorted(gts[rid]["assigned_pair"]))
            best = max(full.values())
            tied = [p for p in PAIR_NAMES if full[p] >= best - 1e-12]
            g.update(assigned=pair, top_pair=str(rng_t.choice(tied)), n_tied=len(tied),
                     assigned_rank=1 + int(sum(full[p] > full[pair] + 1e-12 for p in PAIR_NAMES)))
            g["named"] = g["top_pair"] == pair
            lv = {n: float(P[:, [i, j]].mean()) for (i, j), n in zip(PAIRS, PAIR_NAMES)}  # context: level naming
            tl = [p for p in PAIR_NAMES if lv[p] >= max(lv.values()) - 1e-12]
            g["level_named"] = str(rng_t.choice(tl)) == pair
            g["te_top_is_level_top"] = g["top_pair"] in tl
        games.append(g)
    assert max_dev < 1e-9, f"does not reproduce frozen E70 TE scores (max dev {max_dev})"
    C = [g for g in games if g["channel"]]
    k = sum(g["named"] for g in C)
    ranks = [g["assigned_rank"] for g in C]
    out = dict(note="exploratory/post hoc; zero LLM calls; frozen TE estimator; reproduces E70 TE run scores "
                    f"(max abs dev {max_dev:.1e})", n_games=len(games), n_channel=len(C))
    out["a_pair_naming"] = dict(k=k, n=len(C), share=round(k / len(C), 3), wilson_ci=[round(x, 3) for x in wilson([g["named"] for g in C])],
                                chance=round(1 / 6, 3),
                                binom_p_greater=float(binomtest(k, len(C), 1 / 6, alternative="greater").pvalue),
                                mean_rank_of_assigned_pair=round(float(np.mean(ranks)), 2), chance_mean_rank=3.5,
                                rank_counts={r: ranks.count(r) for r in range(1, 7)},
                                games_with_ties=sum(g["n_tied"] > 1 for g in C),
                                context_level_names_pair=dict(k=sum(g["level_named"] for g in C), n=len(C),
                                                              wilson_ci=[round(x, 3) for x in wilson([g["level_named"] for g in C])]),
                                context_te_top_is_highest_priced_pair=sum(g["te_top_is_level_top"] for g in C))
    for tag, sub in (("executed", [g for g in C if g["executed"]]), ("not_executed", [g for g in C if not g["executed"]])):
        kk = sum(g["named"] for g in sub)
        out["a_pair_naming"][tag] = dict(k=kk, n=len(sub), wilson_ci=[round(x, 3) for x in wilson([g["named"] for g in sub])])
    tim = {}
    for lab, (e, l) in (("windows_1_10_vs_11_20", ("te_early", "te_late")),
                        ("full_fit_residuals_split", ("te_early_res", "te_late_res"))):
        tim[lab] = dict(full=dict(auroc=round(auroc_strat(games, "te"), 3)),
                        early=dict(auroc=round(auroc_strat(games, e), 3), ci=boot(games, lambda b: auroc_strat(b, e))),
                        late=dict(auroc=round(auroc_strat(games, l), 3), ci=boot(games, lambda b: auroc_strat(b, l))),
                        late_minus_early=dict(diff=round(auroc_strat(games, l) - auroc_strat(games, e), 3),
                                              ci=boot(games, lambda b: auroc_strat(b, l) - auroc_strat(b, e))))
    tim["primary"] = "windows_1_10_vs_11_20"
    out["b_timing"] = tim
    A = [g for g in games if not g["channel"]]
    ex = {}
    for tag, sub in (("executed", [g for g in C if g["executed"]]), ("not_executed", [g for g in C if not g["executed"]])):
        gg = sub + A  # cells without a positive drop out of the stratified pool
        ex[tag] = dict(n_C=len(sub), auroc=round(auroc_strat(gg, "te"), 3), ci=boot(gg, lambda b: auroc_strat(b, "te")))
    lab = {}
    for cell in sorted({g["cell"] for g in games}):
        jp = ROOT / "results" / "llm_judge" / f"llm_grid_p2_{cell}.jsonl"
        lab.update({j["run_id"]: j for j in map(json.loads, open(jp))})
    ne = [g for g in C if not g["executed"]]
    ex["not_executed"]["judge_agreement_yes"] = sum(lab[g["run_id"]].get("agreement") == "yes" for g in ne)
    ex["not_executed"]["judge_agreement_no"] = len(ne) - ex["not_executed"]["judge_agreement_yes"]
    for tag, sub in (("executed", [g for g in C if g["executed"]]), ("not_executed", ne), ("no_channel", A)):
        ex.setdefault(tag, {}).update(mean_seller_price_sd=round(float(np.mean([g["price_sd"] for g in sub])), 2),
                                      share_rounds_price_change=round(float(np.mean([g["change_share"] for g in sub])), 2))
    ex["not_executed"]["pair_named"] = sum(g["named"] for g in ne)
    out["c_execution"] = ex
    a, w = out["a_pair_naming"], tim["windows_1_10_vs_11_20"]
    names_pair = a["wilson_ci"][0] > 1 / 6
    late_sig = w["late"]["ci"][0] > .5
    early_only = w["early"]["ci"][0] > .5 and not late_sig
    out["branches"] = dict(a_ci_includes_chance=not names_pair, b_early_only=early_only, late_ci_above_half=late_sig,
                           stronger=names_pair and late_sig)
    out["games"] = games
    (ROOT / "results" / "eval" / "e72_te_diag.json").write_text(json.dumps(out, indent=1))
    md = [f"E72 TE diagnostic (exploratory; {len(games)} E70 games, {len(C)} channel; {out['note']})",
          f"(a) TE names the assigned pair in {k}/{len(C)} = {a['share']:.2f} {a['wilson_ci']} channel games "
          f"(chance 1/6 = 0.17; binom p = {a['binom_p_greater']:.3g}); mean rank of assigned pair "
          f"{a['mean_rank_of_assigned_pair']} (chance 3.5); ranks {a['rank_counts']}; executed "
          f"{a['executed']['k']}/{a['executed']['n']}, not executed {a['not_executed']['k']}/{a['not_executed']['n']}; "
          f"context: highest-priced pair names it {a['context_level_names_pair']['k']}/{len(C)} "
          f"{a['context_level_names_pair']['wilson_ci']}; TE top = highest-priced pair in "
          f"{a['context_te_top_is_highest_priced_pair']}/{len(C)}"]
    for lab, v in tim.items():
        if lab == "primary":
            continue
        md.append(f"(b) {lab}: early {v['early']['auroc']:.2f} {v['early']['ci']}, late {v['late']['auroc']:.2f} "
                  f"{v['late']['ci']}, late − early {v['late_minus_early']['diff']:+.2f} {v['late_minus_early']['ci']} "
                  f"(full {v['full']['auroc']:.2f})")
    md.append("(c) " + "; ".join(f"{t} C (n={v['n_C']}) vs A: {v['auroc']:.2f} {v['ci']}" for t, v in ex.items() if 'n_C' in v)
              + f" (not executed: {ex['not_executed']['judge_agreement_yes']} judge agreement, "
                f"{ex['not_executed']['judge_agreement_no']} none); mean seller price SD executed / not executed / no-channel "
              + " / ".join(f"{ex[t]['mean_seller_price_sd']:.2f}" for t in ("executed", "not_executed", "no_channel")))
    md.append(f"branches: {out['branches']}")
    (ROOT / "results" / "eval" / "e72_te_diag.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
