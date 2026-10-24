"""E70 follow-up (registration amendment 2 (c)): confirm the sign of E70's largest main effect, run once.

  uv run python scripts/e70_followup.py --factor F --sign {+1,-1}   -> results/eval/e70_followup.{json,md}
Data: data/llm_grid_p2_fu_f<F>{0,1} (scripts/e1_grid.py followup). d_level = mean markup(channel) − mean markup(no
channel) at each level; effect = d_high − d_low with a game bootstrap within level × arm. Confirmed iff the 95% CI
excludes 0 in the predicted direction. Fallback games (gt.model not the level's model) are excluded and counted.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from e1_grid import followup_cells  # noqa: E402
from experiments.llm_eval import NASH  # noqa: E402


def load(name, model):
    d = ROOT / "data" / name
    gt = {g["run_id"]: g for g in map(json.loads, open(d / "ground_truth.jsonl"))}
    bad = {r for r, g in gt.items() if model and not all(m == model for m in (g.get("model") or {}).values())}
    rows = {}
    for line in open(d / "trajectories.jsonl"):
        r = json.loads(line)
        if r["run_id"] in gt and r["run_id"] not in bad:
            rows.setdefault(r["run_id"], []).append(r)
    arms = {True: [], False: []}
    for rid, rs in rows.items():
        P = np.array([[a["price"] for a in r["agents"]] for r in rs], float)
        nash = np.array([NASH[r["market"]["cost"]] for r in rs], float)
        arms[gt[rid]["condition"] in "CD"].append(float((P - nash[:, None]).mean()))
    return arms, len(bad)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--factor", required=True)
    ap.add_argument("--sign", type=int, choices=(1, -1), required=True, help="declared: sign of E70's main effect")
    ap.add_argument("--prefix", default="llm_grid_p2_fu")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--B", type=int, default=4000)
    a = ap.parse_args()
    lv = []
    for c in followup_cells(a.factor):
        model = None if a.dry else c["levels"]["model"]
        arms, nbad = load(f"{a.prefix}_{c['cell']}", model)
        lv.append(dict(cell=c["cell"], level=c["levels"][a.factor], arms=arms, excluded=nbad))
    dd = lambda ar: np.mean(ar[True]) - np.mean(ar[False])
    eff = dd(lv[1]["arms"]) - dd(lv[0]["arms"])
    rng = np.random.default_rng(0)
    rs = lambda x: np.asarray(x)[rng.integers(0, len(x), len(x))]
    boot_d = lambda ar: np.mean(rs(ar[True])) - np.mean(rs(ar[False]))
    boots = [boot_d(lv[1]["arms"]) - boot_d(lv[0]["arms"]) for _ in range(a.B)]
    ci = [round(float(np.quantile(boots, .025)), 3), round(float(np.quantile(boots, .975)), 3)]
    ok = ci[0] > 0 if a.sign > 0 else ci[1] < 0
    out = dict(factor=a.factor, predicted_sign=a.sign, rule="confirmed iff 95% CI excludes 0 in the predicted direction",
               levels=[dict(cell=l["cell"], level=l["level"], n=[len(l["arms"][False]), len(l["arms"][True])],
                            C_minus_A=round(float(dd(l["arms"])), 3), excluded_fallback=l["excluded"]) for l in lv],
               effect=round(float(eff), 3), ci=ci, verdict="confirmed" if ok else "not confirmed")
    tag = "e70_followup_dry" if a.dry else "e70_followup"
    (ROOT / "results" / "eval" / f"{tag}.json").write_text(json.dumps(out, indent=1))
    md = (f"E70 follow-up, factor {a.factor} (predicted sign {a.sign:+d}): "
          + "; ".join(f"{l['level']}: C − A {l['C_minus_A']:+.2f} (n {l['n'][0]}+{l['n'][1]})" for l in out["levels"])
          + f"; effect {eff:+.2f} {ci} → {out['verdict']}")
    (ROOT / "results" / "eval" / f"{tag}.md").write_text(md + "\n")
    print(md)


if __name__ == "__main__":
    main()
