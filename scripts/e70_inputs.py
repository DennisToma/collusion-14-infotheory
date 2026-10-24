"""Input/completion checks for the registered E70 analyses (no statistics or LLM calls)."""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

GRID_CUTOFF = datetime(2026, 10, 25, 8, tzinfo=timezone.utc)
FOLLOWUP_DEADLINE = GRID_CUTOFF
FOLLOWUP_LAUNCH_CUTOFF = datetime(2026, 10, 25, 0, 30, tzinfo=timezone.utc)


def load_games(directory: Path, model: str, *, conditions: tuple[str, str]):
    """Ground truth marks completed appends; reject malformed completed runs, exclude fallback models.

    Orphan trajectory rows are ignored, as in the generator's crash recovery. A model map must
    contain all four sellers; an empty map is not evidence that the requested model was used.
    """
    gt = {}
    for g in map(json.loads, (directory / "ground_truth.jsonl").read_text().splitlines()):
        rid = g["run_id"]
        if rid in gt:
            raise ValueError(f"{directory.name}/{rid}: duplicate ground truth")
        if g["condition"] not in conditions:
            raise ValueError(f"{directory.name}/{rid}: unexpected condition {g['condition']}")
        if g.get("T") != 20:
            raise ValueError(f"{directory.name}/{rid}: expected T=20")
        gt[rid] = g
    bad = {rid for rid, g in gt.items()
           if set(g.get("model") or {}) != set("ABCD") or
           any(m != model for m in g["model"].values())}
    rows = {}
    for r in map(json.loads, (directory / "trajectories.jsonl").read_text().splitlines()):
        if r["run_id"] in gt and r["run_id"] not in bad:
            rows.setdefault(r["run_id"], []).append(r)
    for rid in gt.keys() - bad:
        rs = rows.get(rid, [])
        if sorted(r["round"] for r in rs) != list(range(20)):
            raise ValueError(f"{directory.name}/{rid}: expected exactly rounds 0..19")
        rs.sort(key=lambda r: r["round"])
        for r in rs:
            if [a["id"] for a in r["agents"]] != list("ABCD"):
                raise ValueError(f"{directory.name}/{rid}: expected ordered sellers A,B,C,D")
            if any(not math.isfinite(float(a["price"])) for a in r["agents"]):
                raise ValueError(f"{directory.name}/{rid}: non-finite price")
    return {rid: g for rid, g in gt.items() if rid not in bad}, rows, len(bad)


def require_grid_ready(sweeps, *, dry=False, now=None):
    now = now or datetime.now(timezone.utc)
    if sweeps < 1 or sweeps > 6:
        raise ValueError(f"expected 1..6 complete sweeps, got {sweeps}")
    if not dry and sweeps < 6 and now < GRID_CUTOFF:
        raise ValueError(f"only {sweeps}/6 complete sweeps; partial analysis allowed from Sun 08:00 UTC")


def require_followup_ready(counts, *, dry=False, now=None):
    """Allow a deadline-truncated sample only at the registered stop, and always state its size."""
    now = now or datetime.now(timezone.utc)
    if any(n < 1 or n > 12 for n in counts):
        raise ValueError(f"expected 1..12 games in every level x arm, got {counts}")
    complete = all(n == 12 for n in counts)
    if not dry and not complete and now < FOLLOWUP_DEADLINE:
        raise ValueError(f"incomplete follow-up {counts}; partial analysis allowed from Sun 08:00 UTC")
    return complete
