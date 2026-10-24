#!/bin/bash
# E70 post (the one post script): when the 6-sweep chain has exited, run the declared analysis once, then the
# declared follow-up (registration amendment 2 (c)): launched only if decided by Sun 00:30, generation stops Sun 08:00.
cd "$(dirname "$0")/.."
while pgrep -f "bash scripts/e70_chain.sh" > /dev/null; do sleep 60; done
uv run python scripts/e70_grid.py --label --eval > /var/tmp/c14/e70_final.log 2>&1
echo "E70_EXIT=$?" >> /var/tmp/c14/e70_final.log
D=$(uv run python scripts/e70_followup_rule.py) || exit 1
echo "FOLLOWUP_DECISION=$D" >> /var/tmp/c14/e70_final.log
set -- $D
[ "$1" = RUN ] || exit 0
STOP=$(( $(date -u -d '2026-10-25 08:00' +%s) - $(date -u +%s) ))
timeout $STOP uv run python scripts/e1_grid.py followup --factor "$2" --n 12 >> /var/tmp/c14/e1_grid.out 2>&1
uv run python scripts/e70_followup.py --factor "$2" --sign "$3" > /var/tmp/c14/e70_followup.log 2>&1
echo "FOLLOWUP_EXIT=$?" >> /var/tmp/c14/e70_followup.log
