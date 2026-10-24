#!/bin/bash
# E65 final analyses (declared 13:38) after scripts/e65_post.sh has logged 'E65 label+eval done':
# P2.11 row + E64 pooled update + declared verdict, E60 spillover, premium decay. Then: p2_tables.py --check, edit REPORT.
set -e
cd "$(dirname "$0")/.."
grep -q "E65 label+eval done" /var/tmp/c14/queue_partc.log || { echo "E65 label/eval not done yet"; exit 1; }
uv run python scripts/p2_partc.py
uv run python scripts/spillover.py --name llm_strong_qa --block 10
uv run python scripts/premium_decay_fig.py --name llm_strong_qa
uv run python scripts/e67_sticky.py   # E67 confirmatory on llm_strong_qa
grep -A2 "E65 declared rule" results/eval/p2_partc.md
