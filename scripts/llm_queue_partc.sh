#!/bin/bash
# Phase 2 part C (E61 qwen abliterated vs base, E62 glm-5.2 on Go). Logs in /var/tmp/c14/. Modal budget: ~/collusion/QWEN_BUDGET.txt
cd "$(dirname "$0")/.."
L=/var/tmp/c14; mkdir -p $L
run() { for i in 1 2 3; do grep -q STOPPED ~/collusion/QWEN_BUDGET.txt && [[ "$*" == *qwen* ]] && return 1
  uv run python -m sim.llm_market "$@" && return 0; echo "$(date -u) retry $i: $*" >> $L/queue_partc.log; sleep 60; done; }
case "$1" in
  qwen)  # both GPUs warm together
    run --name llm_qa_p2 --conds A,C --n 15 --T 20 --seed 10 --backend qwen --model qwen-abliterated --workers 6 >> $L/llm_qa_p2.log 2>&1 &
    run --name llm_qb_p2 --conds A,C --n 15 --T 20 --seed 10 --backend qwen --model qwen-base --workers 6 >> $L/llm_qb_p2.log 2>&1 &
    wait; echo "$(date -u) qwen E61 done" >> $L/queue_partc.log ;;
  glm)
    run --name llm_glm_p2 --conds A,C --n 10 --T 20 --seed 10 --backend go --model glm-5.2 --workers 2 >> $L/llm_glm_p2.log 2>&1
    echo "$(date -u) glm E62 done" >> $L/queue_partc.log ;;
esac
