#!/bin/bash
# E70 post (the one post script): when the 6-sweep chain has exited, run the declared analysis once.
cd "$(dirname "$0")/.."
while pgrep -f "bash scripts/e70_chain.sh" > /dev/null; do sleep 60; done
uv run python scripts/e70_grid.py --label --eval > /var/tmp/c14/e70_final.log 2>&1
echo "E70_EXIT=$?" >> /var/tmp/c14/e70_final.log
