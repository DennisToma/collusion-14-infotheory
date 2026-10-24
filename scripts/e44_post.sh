#!/bin/bash
# E44 (gap 2) post-processing, declared analyses only (E55 + amendment, E54 final, E56). Run once llm_queue_p2.sh has
# finished llm_long_p2 (T=60); uses the frozen copy data/llm_long_p2_T60 because llm_queue_p2b.sh rewrites
# data/llm_long_p2 while extending it to T=80.   bash scripts/e44_post.sh   (judge calls are cached)
set -e
cd "$(dirname "$0")/.."
N=llm_long_p2_T60
[ -f data/$N/ground_truth.jsonl ] || { echo "data/$N missing: llm_queue_p2b.sh has not snapshotted T=60 yet"; exit 1; }
n=$(wc -l < data/$N/ground_truth.jsonl); [ "$n" -ge 40 ] || { echo "only $n/40 games"; exit 1; }
uv run python -m experiments.llm_eval label --name $N
uv run python -m experiments.llm_eval eval --name $N --Ts 10,20,30,40,50,60
uv run python scripts/long_power.py --name $N --Ts 10,20,30,40,50,60 --mde-Ts 20,40,60
uv run python scripts/premium_decay_fig.py --name $N
uv run python scripts/matched_ref.py
uv run python scripts/behaviour_split.py --names llm_v1,llm_long,llm_ds_p2,$N
uv run python scripts/spillover.py --name $N
uv run python scripts/spillover.py --name llm_ds_p2 --block 10
