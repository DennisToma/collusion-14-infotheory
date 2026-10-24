#!/bin/bash
# E70: after the 3-sweep runner exits, continue to 6 sweeps (resumable; completed games are skipped).
cd "$(dirname "$0")/.."
while pgrep -f "scripts/e1_grid.py run --sweeps 3" > /dev/null; do sleep 60; done
uv run python scripts/e1_grid.py run --sweeps 6 >> /var/tmp/c14/e1_grid.out 2>&1
