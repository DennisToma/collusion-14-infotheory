#!/bin/bash
# E63 strong-lever pilots on qwen (memory, T=40; abliterated + base together so both GPUs are warm), after E61 finishes.
cd "$(dirname "$0")/.."
L=/var/tmp/c14
while pgrep -f "llm_queue_partc.sh qwen" > /dev/null; do sleep 30; done
grep -q STOPPED ~/collusion/QWEN_BUDGET.txt && exit 1
uv run python -m sim.llm_market --name llm_strong_qa_pilot --conds A,C --n 5 --T 40 --seed 61 --memory --backend qwen --model qwen-abliterated --workers 6 >> $L/llm_strong_qa_pilot.log 2>&1 &
uv run python -m sim.llm_market --name llm_strong_qb_pilot --conds A,C --n 5 --T 40 --seed 61 --memory --backend qwen --model qwen-base --workers 6 >> $L/llm_strong_qb_pilot.log 2>&1 &
wait; echo "$(date -u) qwen E63 pilots done" >> $L/queue_partc.log
