"""Part E1 factorial grid (registered in results/e1_registration.md before any data).

2^(7-3) resolution IV, 16 cells, T=20, public board ON everywhere, no-channel vs channel arm on the same cell seed.
Base factors M, K, V, Ch; generators Mem = M*K*V, S = K*V*Ch, F = M*V*Ch
(defining relation I = MKVMem = KVChS = MVChF; every word has length 4).

  uv run python scripts/e1_grid.py cells            # print + write the cell manifest
  uv run python scripts/e1_grid.py run --sweeps 3   # one sweep = 16 cells x (1 no-channel + 1 channel); resumable
  uv run python scripts/e1_grid.py run --sweeps 1 --dry --prefix llm_grid_dry   # pipeline smoke, fake LLM
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parent.parent
LOG = Path('/var/tmp/c14/e1_grid.log')
FACTORS = {  # name: (low level, high level)
    'model': ('gpt-6-luna', 'qwen-3.6-35b'),
    'cost': ('private', 'public'),
    'rivals': ('visible', 'hidden'),
    'channel': ('every', 'first'),
    'memory': ('short', 'full'),
    'shocks': ('none', 'random'),
    'framing': ('base', 'longrun'),
}


def cells():
    out = []
    for i, (m, k, v, ch) in enumerate(itertools.product([-1, 1], repeat=4)):
        x = dict(model=m, cost=k, rivals=v, channel=ch, memory=m * k * v, shocks=k * v * ch, framing=m * v * ch)
        out.append(dict(cell=f'c{i:02d}', signs=x, levels={f: FACTORS[f][(s + 1) // 2] for f, s in x.items()},
                        seed=7000 + i))
    return out


def command(c, sweep, prefix, dry):
    lv = c['levels']
    cmd = ['uv', 'run', 'python', '-m', 'sim.llm_market', '--name', f"{prefix}_{c['cell']}",
           '--conds', 'B,D' if lv['shocks'] == 'random' else 'A,C', '--n', str(sweep + 1), '--T', '20',
           '--seed', str(c['seed']), '--public', '--grid', c['cell'], '--channel', lv['channel'], '--workers', '2']
    cmd += ['--backend', 'codex', '--model', 'gpt-6-luna'] if lv['model'] == 'gpt-6-luna' else \
           ['--backend', 'aqueduct', '--model', 'qwen-3.6-35b']
    cmd += ['--no-private-cost'] if lv['cost'] == 'public' else []
    cmd += ['--hide-rivals'] if lv['rivals'] == 'hidden' else []
    cmd += ['--short-memory'] if lv['memory'] == 'short' else ['--memory']
    cmd += ['--longrun'] if lv['framing'] == 'longrun' else []
    return cmd + (['--dry'] if dry else [])


def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open('a') as f:
        f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime())} {msg}\n")


def run_one(c, sweep, prefix, dry):
    cmd = command(c, sweep, prefix, dry)
    for attempt in range(4):
        with open(f'/var/tmp/c14/{prefix}_{c["cell"]}.log', 'a') as out:
            r = subprocess.run(cmd, cwd=ROOT, stdout=out, stderr=subprocess.STDOUT)
        if r.returncode == 0:
            log(f'done {prefix} {c["cell"]} sweep {sweep}')
            return
        log(f'FAIL {prefix} {c["cell"]} sweep {sweep} attempt {attempt} rc={r.returncode}; retry in 300 s')
        time.sleep(0 if dry else 300)
    log(f'GAVE UP {prefix} {c["cell"]} sweep {sweep}')


def lane(cs, sweeps, prefix, dry, parallel):
    """Sweep-major order: every cell of sweep s finishes before sweep s+1 starts (balanced design at any stop)."""
    for s in range(sweeps):
        with ThreadPoolExecutor(parallel) as pool:
            list(pool.map(lambda c: run_one(c, s, prefix, dry), cs))
        log(f'lane {cs[0]["levels"]["model"]} {prefix} sweep {s} complete')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('what', choices=['cells', 'run'])
    ap.add_argument('--sweeps', type=int, default=3)
    ap.add_argument('--prefix', default='llm_grid_p2')
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    cs = cells()
    if a.what == 'cells':
        manifest = dict(design='2^(7-3) res IV; Mem=M*K*V, S=K*V*Ch, F=M*V*Ch', T=20, public_board=True,
                        arms='A/C (shocks none) or B/D (shocks random): first = no channel, second = channel',
                        datasets=f'data/{a.prefix}_<cell>', cells=cs,
                        commands={c['cell']: ' '.join(command(c, 0, a.prefix, False)) for c in cs})
        (ROOT / 'data' / f'{a.prefix}_manifest.json').write_text(json.dumps(manifest, indent=1))
        for c in cs:
            print(c['cell'], c['levels'])
        return
    luna = [c for c in cs if c['levels']['model'] == 'gpt-6-luna']
    qwen = [c for c in cs if c['levels']['model'] != 'gpt-6-luna']
    log(f'start {a.prefix} sweeps={a.sweeps} dry={a.dry}')
    threads = [threading.Thread(target=lane, args=(luna, a.sweeps, a.prefix, a.dry, 2)),   # 2 cells x 2 workers = 4 codex
               threading.Thread(target=lane, args=(qwen, a.sweeps, a.prefix, a.dry, 1))]   # 1 cell x 2 workers on gateway
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    log(f'all done {a.prefix}')


if __name__ == '__main__':
    main()
