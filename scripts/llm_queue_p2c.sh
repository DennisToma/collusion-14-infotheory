#!/bin/bash
# Replaces llm_queue_p2b.sh (2026-10-24 11:2x UTC, DIRECTION part C outranks the secondary T=80 replay):
# waits for llm_queue_p2.sh (E44), snapshots data/llm_long_p2_T60, then codex stage: E62 gpt-5.6-luna -> E63 gpt-6-luna strong pilot -> T=80 replay.
cd "$(dirname "$0")/.."
L=/var/tmp/c14
run() { for i in 1 2 3; do uv run python -m sim.llm_market "$@" --backend codex --workers 5 && return 0; echo "$(date -u) retry $i: $*" >> $L/queue_p2.log; sleep 120; done; }
while pgrep -f "llm_queue_p2.sh" > /dev/null; do sleep 60; done
[ -d data/llm_long_p2_T60 ] || cp -r data/llm_long_p2 data/llm_long_p2_T60
echo "$(date -u) llm_long_p2_T60 snapshot" >> $L/queue_p2.log
run --name llm_g56l_p2 --conds A,C --n 10 --T 20 --seed 10 --model gpt-5.6-luna >> $L/llm_g56l_p2.log 2>&1
echo "$(date -u) E62 gpt-5.6-luna done" >> $L/queue_p2.log
run --name llm_strong_luna_pilot --conds A,C --n 5 --T 40 --seed 61 --memory >> $L/llm_strong_luna_pilot.log 2>&1
echo "$(date -u) E63 luna strong pilot done" >> $L/queue_p2.log
rm -f data/llm_long_p2/ground_truth.jsonl data/llm_long_p2/trajectories.jsonl
run --name llm_long_p2 --conds A,C --n 20 --T 80 --seed 50 >> $L/llm_long_p2_T80.log 2>&1
echo "$(date -u) llm_long_p2 extended to T=80" >> $L/queue_p2.log
