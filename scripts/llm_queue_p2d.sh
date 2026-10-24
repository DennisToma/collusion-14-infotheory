#!/bin/bash
# Replaces llm_queue_p2c.sh (2026-10-24 13:0x UTC, DIRECTION 3a: T=80 replay cancelled). Waits for the running
# E62 gpt-5.6-luna generator, re-runs it once if incomplete (cache replay), then the E63 gpt-6-luna memory pilot. Nothing else.
cd "$(dirname "$0")/.."
L=/var/tmp/c14
run() { for i in 1 2 3; do uv run python -m sim.llm_market "$@" --backend codex --workers 5 && return 0; echo "$(date -u) retry $i: $*" >> $L/queue_p2.log; sleep 120; done; }
while pgrep -f "name llm_g56l_p2" > /dev/null; do sleep 30; done
n=$(wc -l < data/llm_g56l_p2/ground_truth.jsonl 2>/dev/null || echo 0)
[ "$n" -ge 20 ] || run --name llm_g56l_p2 --conds A,C --n 10 --T 20 --seed 10 --model gpt-5.6-luna >> $L/llm_g56l_p2.log 2>&1
echo "$(date -u) E62 gpt-5.6-luna done (p2d)" >> $L/queue_p2.log
run --name llm_strong_luna_pilot --conds A,C --n 5 --T 40 --seed 61 --memory >> $L/llm_strong_luna_pilot.log 2>&1
echo "$(date -u) E63 luna strong pilot done (p2d)" >> $L/queue_p2.log
