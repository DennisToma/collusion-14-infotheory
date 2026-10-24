#!/bin/bash
# waits for e65_post.sh ('E65 label+eval done'), then runs e65_final.sh once -> /var/tmp/c14/e65_final.log
cd "$(dirname "$0")/.."
until grep -q "E65 label+eval done" /var/tmp/c14/queue_partc.log; do sleep 60; done
bash scripts/e65_final.sh > /var/tmp/c14/e65_final.log 2>&1; echo "$(date -u) e65_final exit $?" >> /var/tmp/c14/queue_partc.log
