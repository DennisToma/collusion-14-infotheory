#!/bin/bash
# D2 / E68 full set (declared): waits for the v1 smoke (seed 0) to finish, then runs seeds 1-14 interleaved
# comms/nocomms (balanced if cut short), one writer, resumable (completed run_ids are skipped).
cd "$(dirname "$0")/.."
L=/var/tmp/c14d2/full.log
while pgrep -f "[r]un_cda.py --cond nocomms --seeds 0 " >/dev/null; do sleep 30; done
echo "$(date -u) D2 full start" >> $L
for s in $(seq 1 14); do
  for c in comms nocomms; do uv run python external/cda/run_cda.py --cond $c --seeds $s --out data/ext_cda/ >> $L 2>&1; done
done
echo "$(date -u) D2 full done" >> $L
