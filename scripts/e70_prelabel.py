"""E70 judge-cache warmer: label finished channel games of the E70 grid cells now, so the declared
`e70_grid.py --label --eval` run after sweep 6 only has to judge the last sweep.

Uses the identical judge prompt/call as `experiments.llm_eval.label` and appends to the same cache
(results/llm_judge/<cell>.jsonl), which `label` reads first. Read-only on data/ (ground_truth.jsonl is
never rewritten here, so it is safe while the generator appends). Prints counts only, no labels or prices.
  uv run python scripts/e70_prelabel.py [--jobs 2] [--watch]   (--watch: rescan every 5 min until e70_chain.sh exits)
"""
import argparse
import json
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments.llm_eval import JUDGE  # noqa: E402
from llm import chat  # noqa: E402

lock = threading.Lock()


def todo(name):
    gtf = ROOT / "data" / name / "ground_truth.jsonl"
    cp = ROOT / "results" / "llm_judge" / f"{name}.jsonl"
    done = {json.loads(x)["run_id"] for x in open(cp)} if cp.exists() else set()
    out = []
    for line in open(gtf) if gtf.exists() else []:
        try:
            g = json.loads(line)
        except ValueError:  # line being written
            continue
        if g.get("private_channel_enabled") and g["run_id"] not in done:
            out.append((cp, g))
    return out


def judge(item):
    cp, g = item
    text = "\n".join(f"[round {m['round']}] {m['sender']}: {m['private_message']}" for m in g["private_chat"])
    r = chat(JUDGE.format(pair="".join(g["assigned_pair"]), chat=text), tier="big", temperature=0)
    m = re.search(r"\{.*\}", r["text"], re.S)
    try:
        j = json.loads(m.group(0))
    except Exception:
        j = {"agreement": "ambiguous", "agreed_price": None, "first_round": None, "evidence": r["text"][:200]}
    j.update(run_id=g["run_id"], judge_model=r["model"], judge_backend=r["backend"])
    with lock:
        cp.parent.mkdir(parents=True, exist_ok=True)
        with open(cp, "a") as f:
            f.write(json.dumps(j) + "\n")
    return r["model"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--watch", action="store_true")
    a = ap.parse_args()
    while True:
        chain = subprocess.run(["pgrep", "-f", "bash scripts/e70_chain.sh"], capture_output=True).returncode == 0
        items = [x for c in range(16) for x in todo(f"llm_grid_p2_c{c:02d}")]
        with ThreadPoolExecutor(a.jobs) as pool:
            models = list(pool.map(judge, items))
        print(time.strftime("%H:%M:%S"), "judged:", len(models), "models:", {m: models.count(m) for m in set(models)},
              flush=True)
        if not (a.watch and chain):
            break
        time.sleep(300)


if __name__ == "__main__":
    main()
