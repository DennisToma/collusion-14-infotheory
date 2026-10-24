#!/bin/bash
# E65 promoted strong arm (declared 13:38 UTC): qwen-abliterated + memory, T=40, seed 65, 20 + 20. One writer for data/llm_strong_qa.
cd "$(dirname "$0")/.."
L=/var/tmp/c14
for i in 1 2 3 4 5; do
  grep -q STOPPED ~/collusion/QWEN_BUDGET.txt && { echo "$(date -u) E65 budget STOPPED" >> $L/queue_partc.log; exit 1; }
  uv run python -m sim.llm_market --name llm_strong_qa --conds A,C --n 20 --T 40 --seed 65 --memory --backend qwen --model qwen-abliterated --workers 6 >> $L/llm_strong_qa.log 2>&1 && break
  echo "$(date -u) E65 retry $i" >> $L/queue_partc.log; sleep 120
done
echo "$(date -u) E65 llm_strong_qa done" >> $L/queue_partc.log
