#!/bin/bash
# Phase 2 Go queue: second seller family (deepseek-v4.1-flash); Go is serialised by llm.py's lock.
cd "$(dirname "$0")/.."
L=/var/tmp/c14
for i in 1 2 3 4 5 6; do
  uv run python -m sim.llm_market --name llm_ds_p2 --conds A,C --n 15 --T 20 --seed 10 --backend go --workers 2 >> $L/llm_ds_p2.log 2>&1 && break
  echo "$(date -u) go retry $i (cooldown?)" >> $L/queue_p2.log; sleep 1900
done
echo "$(date -u) llm_ds_p2 done" >> $L/queue_p2.log
