#!/bin/bash
# E66 (declared 13:3x, stamp-corrected) watcher: waits until the sibling's llm_p2strongF generator has exited, its data has 40
# runs, AND its class file p2_strong_classes_llm_p2strongF.json covers 40 runs; then snapshot + frozen detectors once
# (strongF_ext.py, incl. run-by-run class check vs sibling) + E67 (stickiness, confirmatory on ext_llm_p2strongF).
cd "$(dirname "$0")/.."
L=/var/tmp/c14; S=../collusion-22-say-vs-do
ready() {
  pgrep -f "[d]s llm_p2strongF " > /dev/null && return 1
  [ "$(wc -l < $S/data/llm_p2strongF/ground_truth.jsonl 2>/dev/null || echo 0)" -ge 40 ] || return 1
  pgrep -f "[p]2_label.py --ds llm_p2strongF" > /dev/null && return 1      # sibling still labelling (iter 14 fix)
  [ "$(wc -l < $S/data/llm_p2strongF/labels.jsonl 2>/dev/null || echo 0)" -ge 40 ] || return 1
  # class file must be written after terms.jsonl (classes come from terms; otherwise it may be stale)
  [ $S/results/analysis/p2_strong_classes_llm_p2strongF.json -nt $S/data/llm_p2strongF/terms.jsonl ] || return 1
  python3 -c "import json,sys; sys.exit(0 if len(json.load(open('$S/results/analysis/p2_strong_classes_llm_p2strongF.json'))['runs'])>=40 else 1)" 2>/dev/null
}
until ready; do sleep 60; done
echo "$(date -u) E66 inputs ready" >> $L/queue_partc.log
uv run python scripts/strongF_ext.py --snapshot > $L/e66.log 2>&1 &&
uv run python scripts/strongF_ext.py >> $L/e66.log 2>&1 &&
uv run python scripts/e67_sticky.py >> $L/e66.log 2>&1 &&
echo "$(date -u) E66 done (+E67 rerun)" >> $L/queue_partc.log
