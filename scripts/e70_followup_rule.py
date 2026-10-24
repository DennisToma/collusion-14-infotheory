"""E70 amendment 2 (c): decide the follow-up from results/eval/e70_grid.json by the declared rule (no other input).
Prints 'RUN <factor> <sign>' or 'SKIP <reason>' and records the decision (= the declared prediction) before generation."""
import json, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
me = json.loads((ROOT / "results/eval/e70_grid.json").read_text())["main_effects"]
f = max(me, key=lambda k: abs(me[k]["effect"]))
e, (lo, hi) = me[f]["effect"], me[f]["ci"]
now = datetime.now(timezone.utc)
if (lo > 0 or hi < 0) and abs(e) > 1:
    dec = f"SKIP E70 effect of {f} already excludes 0 with |effect| > 1 ({e:+.2f} [{lo}, {hi}])"
elif now > datetime(2026, 10, 25, 0, 30, tzinfo=timezone.utc):
    dec = f"SKIP E70 analysis finished after Sun 00:30 ({now:%H:%M})"
else:
    dec = f"RUN {f} {1 if e > 0 else -1}"
(ROOT / "results/eval/e70_followup_declared.json").write_text(json.dumps(dict(
    time_utc=f"{now:%Y-%m-%dT%H:%M}", decision=dec, factor=f, e70_effect=e, e70_ci=[lo, hi]), indent=1))
print(dec)
