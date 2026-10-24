#!/bin/bash
# Phase 2 follow-up stage (E44 extension): waits for llm_queue_p2.sh, then extends llm_long_p2 from T=60 to T=80.
# The horizon is never shown to sellers, so rounds 0-59 replay exactly from the cache (cache key = prompts + run/round/agent/attempt);
# the T=60 dataset is preserved as data/llm_long_p2_T60 (primary analysis), the extended one is data/llm_long_p2 (T=80, secondary).
cd "$(dirname "$0")/.."
L=/var/tmp/c14
while pgrep -f "llm_queue_p2.sh" > /dev/null; do sleep 60; done
[ -d data/llm_long_p2_T60 ] || cp -r data/llm_long_p2 data/llm_long_p2_T60
rm -f data/llm_long_p2/ground_truth.jsonl data/llm_long_p2/trajectories.jsonl
for i in 1 2 3; do
  uv run python -m sim.llm_market --name llm_long_p2 --conds A,C --n 20 --T 80 --seed 50 --backend codex --workers 5 >> $L/llm_long_p2_T80.log 2>&1 && break
  sleep 120
done
echo "$(date -u) llm_long_p2 extended to T=80" >> $L/queue_p2.log
