"""Verify saved LLM run scores against trajectories, without null draws or LLM calls.

uv run python scripts/check_saved_scores.py

Fixed finalized datasets only; E68/E70 and judge-only memory pilots are excluded.
This checks computation with the frozen implementation, not independent validation
of the estimators. Confidence intervals and permutation flags are not recomputed.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from experiments.llm_eval import DETS, NASH, PAIR_NAMES, add_level_scores, arrays, score_run  # noqa: E402

DATASETS = ["llm_v1", "llm_long", "llm_ds_p2", "llm_long_p2_T60", "llm_qa_p2", "llm_qb_p2",
            "llm_g56l_p2", "llm_strong_qa", "llm_qa36_p2", "llm_qb36_p2", "llm_ds_p2pub",
            *[f"llm_p2_{v}" for v in ("v0", "para", "template", "order", "noreason")]]


def check(name, root=ROOT):
    saved = json.loads((root / "results/eval" / f"{name}.json").read_text())["run_scores"]
    assert saved, f"{name}: no saved horizons"
    rows = defaultdict(list)
    for line in (root / "data" / name / "trajectories.jsonl").read_text().splitlines():
        r = json.loads(line)
        rows[r["run_id"]].append(r)
    for rid, rs in rows.items():
        rs.sort(key=lambda r: r["round"])
        assert [r["round"] for r in rs] == list(range(len(rs))), f"{name}/{rid}: missing or duplicate rounds"
    cells = run_horizons = 0
    for horizon, scores in saved.items():
        T = int(horizon)
        assert set(scores) == set(DETS), f"{name}/T={T}: detector coverage differs"
        eligible = {rid for rid, rs in rows.items() if len(rs) >= T}
        assert eligible, f"{name}/T={T}: no eligible games"
        for det, values in scores.items():
            assert set(values) == eligible, f"{name}/T={T}/{det}: run coverage differs"
        for n, (rid, rs) in enumerate(sorted(rows.items())):
            if rid not in eligible:
                continue
            P, S, _ = arrays(rs[:T])
            result = score_run(P, S, B=0, seed=n)
            add_level_scores(result, P, np.array([NASH[r["market"]["cost"]] for r in rs[:T]], float))
            for det in DETS:
                actual = max(result[p]["score"][det] for p in PAIR_NAMES)
                assert actual == scores[det][rid], f"{name}/T={T}/{rid}/{det}: {actual} != {scores[det][rid]}"
                cells += 1
            run_horizons += 1
    return dict(dataset=name, horizons=len(saved), run_horizons=run_horizons, score_cells=cells)


if __name__ == "__main__":
    results = [check(name) for name in DATASETS]
    print(json.dumps(dict(passed=True, datasets=results, score_cells=sum(r["score_cells"] for r in results))))
