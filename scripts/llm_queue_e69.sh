#!/bin/bash
# E69 (C3b, declared): Qwen3.6-35B abliterated (Modal) vs base (aqueduct gateway), one writer per dataset, resumable.
cd "$(dirname "$0")/.."
L=/var/tmp/c14
run() { for i in 1 2 3 4; do uv run python -m sim.llm_market "$@" && return 0; echo "$(date -u) E69 retry $i: $*" >> $L/queue_partc.log; sleep 300; done; }
run --name llm_qa36_p2 --conds A,C --n 15 --T 20 --seed 10 --backend qwen --model qwen36-abliterated --workers 6 >> $L/llm_qa36_p2.log 2>&1 &
run --name llm_qb36_p2 --conds A,C --n 15 --T 20 --seed 10 --backend aqueduct --model qwen-3.6-35b --workers 2 >> $L/llm_qb36_p2.log 2>&1 &
wait
echo "$(date -u) E69 generation done" >> $L/queue_partc.log
