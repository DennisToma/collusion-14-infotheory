#!/bin/bash
cd /home/factory/collusion/collusion-14-infotheory
uv run python -m sim.llm_market --name llm_mixed2 --conds A --n 12 --T 20 --workers 4 --seed 21 --mixed-tier big --backend codex > /var/tmp/c14/llm_mixed2.log 2>&1
echo "$(date -u) llm_mixed2 done" >> /var/tmp/c14/queue.log
uv run python -m experiments.llm_eval mixed --name llm_mixed2 > /var/tmp/c14/llm_mixed2_eval.log 2>&1
echo "$(date -u) llm_mixed2 evaluated" >> /var/tmp/c14/queue.log
