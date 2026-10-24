#!/bin/bash
# Phase 2 codex queue (5 parallel games = 5 concurrent codex calls; +1 Go = 6 total). Logs in /var/tmp/c14/.
cd "$(dirname "$0")/.."
L=/var/tmp/c14; mkdir -p $L
run() { for i in 1 2 3; do uv run python -m sim.llm_market "$@" --backend codex --workers 5 && return 0; echo "$(date -u) retry $i: $*" >> $L/queue_p2.log; sleep 120; done; }
for v in v0 para template order noreason; do
  run --name llm_p2_$v --variant $v --conds A,C --n 6 --T 20 --seed 43 >> $L/llm_p2_$v.log 2>&1
  echo "$(date -u) llm_p2_$v done" >> $L/queue_p2.log
done
run --name llm_long_p2 --conds A,C --n 10 --T 60 --seed 50 >> $L/llm_long_p2.log 2>&1
echo "$(date -u) llm_long_p2 n=10 done" >> $L/queue_p2.log
run --name llm_long_p2 --conds A,C --n 20 --T 60 --seed 50 >> $L/llm_long_p2.log 2>&1
echo "$(date -u) llm_long_p2 n=20 done" >> $L/queue_p2.log
