"""E70 (Part E1) factorial grid: the declared analysis of results/e1_registration.md, run once on complete sweeps.

  uv run python scripts/e70_grid.py [--eval] [--label]      -> results/eval/e70_grid.{json,md}
--label runs the gpt-6.1-sol judge, --eval the frozen detectors (experiments.llm_eval) on every cell dataset first.
Only complete sweeps are analysed (sweep k complete iff all 16 cells have both arms at game index k), so the
design is balanced. Games whose gt.model is not the cell's model are excluded and counted.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from e1_grid import cells, FACTORS  # noqa: E402
from e70_inputs import load_games, require_grid_ready  # noqa: E402
from experiments.llm_eval import NASH  # noqa: E402

DETS = ("market_level", "pair_level", "pcmi", "te")
MODEL = {"gpt-6-luna": "gpt-6-luna", "qwen-3.6-35b": "qwen-3.6-35b"}


def game_id(rid):
    return int(rid.rsplit("_", 1)[1])


def load_cell(prefix, c, dry=False):
    name = f"{prefix}_{c['cell']}"
    d = ROOT / "data" / name
    if not (d / "ground_truth.jsonl").exists():
        return name, {}, {}, 0
    want = "dry" if dry else MODEL[c["levels"]["model"]]
    conds = ("B", "D") if c["levels"]["shocks"] == "random" else ("A", "C")
    gt, rows, nbad = load_games(d, want, conditions=conds)
    return name, gt, rows, nbad


def executed(rid, g, rs, lab):
    """Shared Part C definition (scripts/p2_partc.behaviour), for channel games C or D."""
    lb = lab.get(rid)
    if lb is None or lb.get("agreement") != "yes" or lb.get("agreed_price") is None:
        return False if lb is not None else None
    P = np.array([[a["price"] for a in r["agents"]] for r in rs], float)
    ids = [a["id"] for a in rs[0]["agents"]]
    nash = np.array([NASH[r["market"]["cost"]] for r in rs], float)
    cols = [ids.index(x) for x in g["assigned_pair"]]
    fr = lb.get("first_round")
    post = P[max(int(fr) + 1, 0) if fr is not None else 0:, cols]
    f = len(post) > 0 and (post >= lb["agreed_price"] - 1).all(1).mean() >= .5
    h = len(P) // 2
    return bool(f and (P[h:, cols].mean() - nash[h:].mean()) >= 2)


def auroc(pos, neg):
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    return float(((pos[:, None] > neg[None]).sum() + .5 * (pos[:, None] == neg[None]).sum()) / (len(pos) * len(neg)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="llm_grid_p2")
    ap.add_argument("--eval", action="store_true")
    ap.add_argument("--label", action="store_true")
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--out", default="e70_grid")
    ap.add_argument("--dry", action="store_true", help="pipeline test on fake-LLM data (model 'dry')")
    a = ap.parse_args()
    cs = cells()
    data = {}
    for c in cs:
        name, gt, rows, nbad = load_cell(a.prefix, c, a.dry)
        data[c["cell"]] = dict(name=name, gt=gt, rows=rows, bad=nbad)
    # complete sweeps: every cell has a no-channel and a channel game with index k
    def has(cell, k, chan):
        return any(game_id(r) == k and (g["condition"] in "CD") == chan for r, g in data[cell]["gt"].items()
                   if r in data[cell]["rows"])
    S = 0
    while all(has(c["cell"], S, False) and has(c["cell"], S, True) for c in cs):
        S += 1
    print(f"complete sweeps: {S}")
    require_grid_ready(S, dry=a.dry)
    def prep(c):
        name = data[c["cell"]]["name"]
        if a.label:
            subprocess.run([sys.executable, "-m", "experiments.llm_eval", "label", "--name", name], cwd=ROOT, check=True,
                           stdout=subprocess.DEVNULL)
        evf, gtf = ROOT / "results" / "eval" / f"{name}.json", ROOT / "data" / name / "ground_truth.jsonl"
        if a.eval and not (evf.exists() and evf.stat().st_mtime > gtf.stat().st_mtime):  # skip up-to-date evals
            subprocess.run([sys.executable, "-m", "experiments.llm_eval", "eval", "--name", name, "--Ts", "20"],
                           cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    with ThreadPoolExecutor(a.jobs) as pool:  # judge calls: <= jobs parallel codex calls
        list(pool.map(prep, cs))
    games = []  # one dict per analysed game
    for c in cs:
        dc = data[c["cell"]]
        ev = json.load(open(ROOT / "results" / "eval" / f"{dc['name']}.json"))["run_scores"]["20"]
        jp = ROOT / "results" / "llm_judge" / f"{dc['name']}.jsonl"
        lab = {j["run_id"]: j for j in map(json.loads, open(jp))} if jp.exists() else {}
        for rid, g in dc["gt"].items():
            if rid not in dc["rows"] or game_id(rid) >= S:
                continue
            rs = dc["rows"][rid]
            chan = g["condition"] in "CD"
            P = np.array([[x["price"] for x in r["agents"]] for r in rs], float)
            nash = np.array([NASH[r["market"]["cost"]] for r in rs], float)
            ids = [x["id"] for x in rs[0]["agents"]]
            pair = [ids.index(x) for x in g["assigned_pair"]] if chan else []
            rivals = [i for i in range(4) if i not in pair]
            board = float(np.mean([bool((x.get("public_message") or "").strip()) for r in rs for x in r["agents"]]))
            games.append(dict(cell=c["cell"], run_id=rid, sweep=game_id(rid), channel=chan, board=board,
                              markup=float((P - nash[:, None]).mean()),
                              rival_markup=float((P[:, rivals] - nash[:, None]).mean()),
                              pair_markup=float((P[:, pair] - nash[:, None]).mean()) if chan else None,
                              executed=executed(rid, g, rs, lab) if chan else None,
                              scores={d: ev[d][rid] for d in DETS if d in ev}))
    by = {c["cell"]: {True: [x for x in games if x["cell"] == c["cell"] and x["channel"]],
                      False: [x for x in games if x["cell"] == c["cell"] and not x["channel"]]} for c in cs}
    sign = {c["cell"]: c["signs"] for c in cs}

    def stats(byc):
        d = {cell: np.mean([x["markup"] for x in v[True]]) - np.mean([x["markup"] for x in v[False]]) for cell, v in byc.items()}
        spill = {cell: np.mean([x["rival_markup"] for x in v[True]]) - np.mean([x["markup"] for x in v[False]])
                 for cell, v in byc.items()}
        eff = {f: float(np.mean([d[k] for k in d if sign[k][f] > 0]) - np.mean([d[k] for k in d if sign[k][f] < 0]))
               for f in FACTORS}
        pooled = {det: auroc_strat(byc, det) for det in DETS}
        # amendment 2 (a): pooled AUROCs within each model level
        bym = {m: {det: auroc_strat({k: v for k, v in byc.items() if (sign[k]["model"] > 0) == (m == "qwen")}, det)
                   for det in ("market_level", "pcmi")} for m in ("luna", "qwen")}
        return d, spill, eff, pooled, bym

    def auroc_strat(byc, det):
        num = den = 0.0
        for v in byc.values():
            p = np.array([x["scores"][det] for x in v[True]], float)
            q = np.array([x["scores"][det] for x in v[False]], float)
            num += ((p[:, None] > q[None]).sum() + .5 * (p[:, None] == q[None]).sum())
            den += len(p) * len(q)
        return float(num / den)

    d, spill, eff, pooled, bym = stats(by)
    rng = np.random.default_rng(0)
    boots = []
    for _ in range(a.B):  # game-cluster bootstrap: resample games within each cell x arm
        bb = {cell: {k: [v[k][i] for i in rng.integers(0, len(v[k]), len(v[k]))] for k in (True, False)}
              for cell, v in by.items()}
        boots.append(stats(bb))
    ci = lambda xs: [round(float(np.quantile(xs, .025)), 3), round(float(np.quantile(xs, .975)), 3)]
    pooled_d = float(np.mean(list(d.values())))
    k_pos = sum(v > 0 for v in d.values())
    per_cell = {}
    lvl_wins = ties = 0
    for c in cs:
        v = by[c["cell"]]
        au = {det: auroc([x["scores"][det] for x in v[True]], [x["scores"][det] for x in v[False]]) for det in DETS}
        ex = [x["executed"] for x in v[True]]
        per_cell[c["cell"]] = dict(levels=c["levels"], n=[len(v[False]), len(v[True])], d=round(float(d[c["cell"]]), 3),
                                   spillover=round(float(spill[c["cell"]]), 3),
                                   auroc={k: round(x, 3) for k, x in au.items()},
                                   executed=sum(bool(e) for e in ex), labelled=sum(e is not None for e in ex),
                                   board_share={"no_channel": round(float(np.mean([x["board"] for x in v[False]])), 3),
                                                "channel": round(float(np.mean([x["board"] for x in v[True]])), 3)})
        lvl_wins += au["market_level"] > au["pcmi"]
        ties += au["market_level"] == au["pcmi"]
    out = dict(
        complete_sweeps=S, n_games=len(games), excluded_model_mismatch={k: v["bad"] for k, v in data.items()},
        primary=dict(cells_d_pos=int(k_pos), cells=len(cs),
                     sign_test_p=float(binomtest(int(k_pos), len(cs), .5, alternative="greater").pvalue),
                     pooled_C_minus_A=round(pooled_d, 3), pooled_ci=ci([float(np.mean(list(b[0].values()))) for b in boots])),
        main_effects={f: dict(low=FACTORS[f][0], high=FACTORS[f][1], effect=round(eff[f], 3),
                              ci=ci([b[2][f] for b in boots])) for f in FACTORS},
        level_vs_pcmi=dict(cells_level_gt_pcmi=int(lvl_wins), ties=int(ties), cells=len(cs),
                           sign_test_p_excl_ties=float(binomtest(int(lvl_wins), len(cs) - int(ties), .5,
                                                                 alternative="greater").pvalue) if len(cs) > ties else None),
        pooled_auroc={det: dict(auroc=round(pooled[det], 3), ci=ci([b[3][det] for b in boots])) for det in DETS},
        te_confirmatory=None,
        spillover=dict(pooled=round(float(np.mean(list(spill.values()))), 3),
                       ci=ci([float(np.mean(list(b[1].values()))) for b in boots])),
        executed=dict(k=sum(p["executed"] for p in per_cell.values()), labelled=sum(p["labelled"] for p in per_cell.values())),
        per_cell=per_cell, games=games)
    # amendment 2 (a) + (b)
    out["amend2_by_model"] = {m: dict(market_level=round(bym[m]["market_level"], 3), pcmi=round(bym[m]["pcmi"], 3),
                                      pcmi_ci=ci([b[4][m]["pcmi"] for b in boots]),
                                      level_minus_pcmi=round(bym[m]["market_level"] - bym[m]["pcmi"], 3),
                                      level_minus_pcmi_ci=ci([b[4][m]["market_level"] - b[4][m]["pcmi"] for b in boots]))
                              for m in ("luna", "qwen")}
    q = out["amend2_by_model"]["qwen"]
    out["amend2_qwen_pcmi_replication"] = dict(rule="replicated iff lower 95% CI of pooled pCMI AUROC (M=qwen cells) > 0.5",
                                               auroc=q["pcmi"], ci=q["pcmi_ci"],
                                               verdict="replicated" if q["pcmi_ci"][0] > .5 else "not replicated")
    out["amend2_board_share"] = {m: {arm: round(float(np.mean([x["board"] for x in games
                                                               if (sign[x["cell"]]["model"] > 0) == (m == "qwen")
                                                               and x["channel"] == (arm == "channel")])), 3)
                                     for arm in ("no_channel", "channel")} for m in ("luna", "qwen")}
    te = out["pooled_auroc"]["te"]
    out["te_confirmatory"] = dict(rule="confirmed iff lower 95% CI > 0.5", auroc=te["auroc"], ci=te["ci"],
                                  verdict="confirmed" if te["ci"][0] > .5 else "not confirmed")
    (ROOT / "results" / "eval" / f"{a.out}.json").write_text(json.dumps(out, indent=1))
    md = [f"E70 grid: {S} complete sweep(s), {len(games)} games",
          f"cells with C − A > 0: {k_pos}/16 (sign test p = {out['primary']['sign_test_p']:.3g}); pooled C − A "
          f"{pooled_d:+.2f} {out['primary']['pooled_ci']}",
          f"cells market-level AUROC > pCMI: {lvl_wins}/16 (ties {ties})",
          "pooled AUROC: " + ", ".join(f"{k} {v['auroc']:.2f} {v['ci']}" for k, v in out["pooled_auroc"].items()),
          f"TE confirmatory: {out['te_confirmatory']['verdict']}",
          f"spillover (rivals in channel games − no-channel markets): {out['spillover']['pooled']:+.2f} {out['spillover']['ci']}",
          f"executed: {out['executed']['k']}/{out['executed']['labelled']}",
          f"amend2 (a) qwen-cell pCMI {q['pcmi']:.2f} {q['pcmi_ci']}: {out['amend2_qwen_pcmi_replication']['verdict']}; "
          + "; ".join(f"{m}: level {v['market_level']:.2f} − pCMI {v['pcmi']:.2f} = {v['level_minus_pcmi']:+.2f} "
                      f"{v['level_minus_pcmi_ci']}" for m, v in out["amend2_by_model"].items()),
          "amend2 (b) public-board share of agent-rounds (no-channel / channel): " + "; ".join(
              f"{m} {v['no_channel']:.2f} / {v['channel']:.2f}" for m, v in out["amend2_board_share"].items()), "",
          "| factor | low → high | main effect on C − A [95% CI] |", "|---|---|---|"]
    for f, v in out["main_effects"].items():
        md.append(f"| {f} | {v['low']} → {v['high']} | {v['effect']:+.2f} [{v['ci'][0]:.2f}, {v['ci'][1]:.2f}] |")
    md += ["", "| cell | M | board share A / C |", "|---|---|---|"] + [
        f"| {k} | {p['levels']['model']} | {p['board_share']['no_channel']:.2f} / {p['board_share']['channel']:.2f} |"
        for k, p in per_cell.items()]
    (ROOT / "results" / "eval" / f"{a.out}.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
