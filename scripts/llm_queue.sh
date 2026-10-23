#!/bin/bash
# Sequential LLM job queue (keeps codex parallelism at 4 from this repo). Logs in /var/tmp/c14/.
# Waits for the running llm_v1 generator, then: extend A/B controls to 21 games (surrogate pool >= 20),
# label + eval llm_v1, long-horizon run (T=50), mixed-model run.
cd "$(dirname "$0")/.."
L=/var/tmp/c14
while pgrep -f "sim.llm_market --name llm_v1 " >/dev/null; do sleep 30; done
echo "$(date -u) llm_v1 main done" >> $L/queue.log
uv run python -m sim.llm_market --name llm_v1 --conds A,B,C,D --n 16 --T 20 --workers 4 --seed 10 >> $L/llm_v1.log 2>&1  # resume any gaps
uv run python -m sim.llm_market --name llm_v1 --conds A,B --n 21 --T 20 --workers 4 --seed 10 >> $L/llm_v1.log 2>&1
echo "$(date -u) llm_v1 extended" >> $L/queue.log
uv run python -m experiments.llm_eval label --name llm_v1 > $L/llm_v1_label.log 2>&1
uv run python -m experiments.llm_eval eval --name llm_v1 > $L/llm_v1_eval.log 2>&1
echo "$(date -u) llm_v1 labelled+evaluated" >> $L/queue.log
uv run python -m sim.llm_market --name llm_long --conds A,C --n 8 --T 50 --workers 4 --seed 30 > $L/llm_long.log 2>&1
echo "$(date -u) llm_long done" >> $L/queue.log
uv run python -m sim.llm_market --name llm_mixed --conds A --n 12 --T 20 --workers 4 --seed 20 --mixed-tier big > $L/llm_mixed.log 2>&1
echo "$(date -u) llm_mixed done" >> $L/queue.log
uv run python -m experiments.llm_eval label --name llm_long > $L/llm_long_label.log 2>&1
uv run python -m experiments.llm_eval eval --name llm_long > $L/llm_long_eval.log 2>&1
uv run python -m experiments.llm_eval mixed --name llm_mixed > $L/llm_mixed_eval.log 2>&1
echo "$(date -u) queue finished" >> $L/queue.log
