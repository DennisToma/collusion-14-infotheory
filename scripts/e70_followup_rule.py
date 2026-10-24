"""Decide amendment 2(c)'s follow-up once, record its prediction before generation, print RUN or SKIP."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from e70_inputs import FOLLOWUP_LAUNCH_CUTOFF, require_grid_ready

ROOT = Path(__file__).resolve().parent.parent


def decide(result, now):
    require_grid_ready(result["complete_sweeps"], now=now)
    me = result["main_effects"]
    f = max(me, key=lambda k: abs(me[k]["effect"]))
    e, (lo, hi) = me[f]["effect"], me[f]["ci"]
    if (lo > 0 or hi < 0) and abs(e) > 1:
        dec = f"SKIP E70 effect of {f} already excludes 0 with |effect| > 1 ({e:+.2f} [{lo}, {hi}])"
    elif now > FOLLOWUP_LAUNCH_CUTOFF:
        dec = f"SKIP E70 analysis finished after Sun 00:30 ({now:%H:%M})"
    else:
        dec = f"RUN {f} {1 if e > 0 else -1}"
    return dict(time_utc=f"{now:%Y-%m-%dT%H:%M}", decision=dec, factor=f,
                predicted_sign=1 if e > 0 else -1, e70_effect=e, e70_ci=[lo, hi])


def main():
    source = ROOT / "results/eval/e70_grid.json"
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    dest = ROOT / "results/eval/e70_followup_declared.json"
    if dest.exists():
        saved = json.loads(dest.read_text())
        if saved.get("e70_sha256") != digest:
            raise ValueError("E70 differs from the frozen follow-up declaration; refusing to overwrite")
        print(saved["decision"])
        return
    out = decide(json.loads(source.read_text()), datetime.now(timezone.utc))
    out["e70_sha256"] = digest
    # Exclusive creation preserves the first prediction, including on accidental re-invocation.
    with dest.open("x") as f:
        f.write(json.dumps(out, indent=1))
    print(out["decision"])


if __name__ == "__main__":
    main()
