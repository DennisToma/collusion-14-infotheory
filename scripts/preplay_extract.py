"""E39 step 1: recover each pair member's provisional pre-play price (round -1; only the first sender has not
read a partner message) by replaying llm_v1 / llm_long from the LLM cache. No LLM calls: a cache miss aborts. The replay must
reproduce every stored trajectory price exactly, otherwise the script fails.

    uv run python scripts/preplay_extract.py     # needs cache/llm_market/*.jsonl (gitignored)
                                                 # -> data/<name>/preplay.jsonl (committed; input to preplay_offer.py)
"""
from __future__ import annotations

import hashlib
import json
import sys
from argparse import Namespace
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import sim.llm_market as lm  # noqa: E402

RUNS = {"llm_v1": dict(conds="CD", n=16, T=20, seed=10), "llm_long": dict(conds="C", n=8, T=50, seed=30)}


class StrictCache(lm.Cache):
    """Look up a cached response under either backend key used when the dataset was generated; never call an LLM."""

    def __init__(self, path):
        super().__init__(path)
        self.log = []

    def call(self, system, prompt, tier, backend, run_id, t, agent, attempt):
        for b in (backend, None, "codex"):
            payload = [False, [system, prompt, tier, b, lm.TEMPERATURE, run_id, t, agent, attempt]]
            key = hashlib.sha256(json.dumps(payload).encode()).hexdigest()
            if key in self.entries:
                response = self.entries[key]
                self.log.append((run_id, t, agent, attempt, response))
                return response
        raise KeyError(f"cache miss {run_id} t={t} {agent} attempt={attempt}")


def main():
    for name, spec in RUNS.items():
        stored = {}
        for line in (ROOT / "data" / name / "trajectories.jsonl").read_text().splitlines():
            r = json.loads(line)
            stored[(r["run_id"], r["round"])] = [a["price"] for a in r["agents"]]
        cache = StrictCache(ROOT / "cache" / "llm_market" / f"{name}.jsonl")
        args = Namespace(name=name, T=spec["T"], seed=spec["seed"], hybrid=False, mixed_tier=None, models="cheap",
                         pair_tier=None, backend="codex", public=False, explore=False, private_cost=True, dry=False)
        out = []
        for c in spec["conds"]:
            for k in range(spec["n"]):
                cache.log.clear()
                rows, gt = lm.run_game(args, cache, c, k)
                for r in rows:
                    assert [a["price"] for a in r["agents"]] == stored[(r["run_id"], r["round"])], r["run_id"]
                pre = {}
                for run_id, t, agent, attempt, resp in cache.log:
                    if t == -1:
                        parsed = lm.parse(resp["text"])
                        if parsed is not None:
                            pre[agent] = parsed["price"]
                assert sorted(pre) == sorted(gt["assigned_pair"]), (gt["run_id"], pre)
                out.append(dict(run_id=gt["run_id"], condition=c, assigned_pair=gt["assigned_pair"],
                                provisional_price=pre))
        path = ROOT / "data" / name / "preplay.jsonl"
        path.write_text("".join(json.dumps(o) + "\n" for o in out))
        print(f"{name}: {len(out)} runs replayed exactly; wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
