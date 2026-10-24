#!/bin/bash
# E65 post-processing (declared 13:38): waits until data/llm_strong_qa has 40 games AND the generator has exited,
# then judge labels + frozen detectors at T=40. Does NOT print any result; the manager runs p2_partc.py afterwards.
cd "$(dirname "$0")/.."
L=/var/tmp/c14
while pgrep -f "[n]ame llm_strong_qa " > /dev/null || [ "$(wc -l < data/llm_strong_qa/ground_truth.jsonl 2>/dev/null || echo 0)" -lt 40 ]; do
  pgrep -f "[l]lm_queue_e65" > /dev/null || pgrep -f "[n]ame llm_strong_qa " > /dev/null || { echo "$(date -u) E65 generator gone with <40 games" >> $L/queue_partc.log; exit 1; }
  sleep 60
done
uv run python -m experiments.llm_eval label --name llm_strong_qa > $L/e65_label.log 2>&1 &&
uv run python -m experiments.llm_eval eval --name llm_strong_qa --Ts 40 > $L/e65_eval.log 2>&1 &&
echo "$(date -u) E65 label+eval done" >> $L/queue_partc.log
