"""Phase-2 gap 9 (exploration): non-price collusion = bid rotation in the scripted market.

    uv run python -m experiments.p2_rotation            # DEV, seed0 240
    uv run python -m experiments.p2_rotation --test     # LOCKED test, seed0 2005 (data/SPLITS.md), run once

Base market (N=4, mu=3), families A/B, T=100 (+ first-30-round prefix), n=30 per group, B=100, frozen detectors.
Groups: control; signal (shared-signal pair, s=0.6, reference); rot_alt (winner alternates deterministically,
s=0.6: the other member posts cover price 16); rot_rand (winner drawn privately each round, s=0.6).
Statistics: pCMI, MI, TE (lagged) shift-null flags; markup and pair_level against same-market LOO controls.
"""
from __future__ import annotations

import argparse
import itertools
import json
import time
from multiprocessing import Pool
from pathlib import Path

from experiments.p2_market import _one, auc, mean_score, rate, surrogate_p

ROOT = Path(__file__).resolve().parent.parent
GROUPS = {'control': ('signal', 0.0), 'signal': ('signal', 0.6), 'rot_alt': ('rotation_alt', 0.6), 'rot_rand': ('rotation_rand', 0.6)}
ALPHA, DEV_SEED, TEST_SEED = 0.05, 240, 2005


def summarize(rows):
    out = {}
    for fam, H in itertools.product(('A', 'B'), ('100', '30')):
        ctl = [r for r in rows if r['family'] == fam and r['group'] == 'control']
        for g in GROUPS:
            grp = [r for r in rows if r['family'] == fam and r['group'] == g]
            d = {'n': len(grp), 'mean_price': mean_score(r['h'][H]['mean_price'] for r in grp)}
            for key in ('pcmi', 'mi', 'te'):
                d[key + '_flag'] = rate(r['h'][H]['run_p'][key] < ALPHA for r in grp)
            for key in ('markup', 'pair_level'):
                d[key + '_surrogate_flag'] = rate(surrogate_p(r, ctl, key, H) < ALPHA for r in grp)
            if g != 'control':
                d['top_pcmi_is_pair'] = rate(r['h'][H]['top_pcmi'] == r['pair'] for r in grp)
                d['top_pair_level_is_pair'] = rate(r['h'][H]['top_pair_level'] == r['pair'] for r in grp)
                d['auroc'] = {k: auc([r['h'][H]['scores'][k] for r in grp], [r['h'][H]['scores'][k] for r in ctl])
                              for k in ('pcmi', 'mi', 'te', 'markup', 'pair_level')}
            out[f'{fam}/T{H}/{g}'] = d
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--test', action='store_true')
    ap.add_argument('--n', type=int, default=30)
    ap.add_argument('--B', type=int, default=100)
    a = ap.parse_args()
    seed0, split = (TEST_SEED, 'test') if a.test else (DEV_SEED, 'dev')
    start = time.monotonic()
    cfgs = []
    for fam, g, rep in itertools.product(('A', 'B'), GROUPS, range(a.n)):
        ctype, s = GROUPS[g]
        cfgs.append({'market': 'base', 'family': fam, 'group': g, 'ctype': ctype, 'strength': s, 'B': a.B,
                     'seed': seed0 * 1_000_000 + len(cfgs), 'run_id': f'p2r_{split}_{fam}_{g}_{rep:03}'})
    with Pool(3) as pool:
        rows = sorted(pool.map(_one, cfgs), key=lambda r: r['run_id'])
    summ = summarize(rows)
    res = {'experiment': 'rotation', 'split': split, 'seed0': seed0, 'n_per_group': a.n, 'T': 100, 'B': a.B, 'alpha': ALPHA,
           'groups': GROUPS, 'runtime_seconds': time.monotonic() - start, 'summaries': summ, 'runs': rows}
    out = ROOT / 'results' / 'p2' / f'rotation_{split}.json'
    out.write_text(json.dumps(res, indent=2, allow_nan=False) + '\n')
    print('fam/T/group        price  pCMI   MI    TE    markup level | AUROC pcmi/te/markup/level | top pCMI/level is pair')
    for k, d in summ.items():
        f = lambda m: f"{d[m]['rate']:.2f}"
        au = d.get('auroc')
        tail = (f"{au['pcmi']['auc']:.2f}/{au['te']['auc']:.2f}/{au['markup']['auc']:.2f}/{au['pair_level']['auc']:.2f} | "
                f"{d['top_pcmi_is_pair']['rate']:.2f}/{d['top_pair_level_is_pair']['rate']:.2f}") if au else ''
        print(f"{k:18} {d['mean_price']['mean']:5.2f}  {f('pcmi_flag')}  {f('mi_flag')}  {f('te_flag')}  "
              f"{f('markup_surrogate_flag')}  {f('pair_level_surrogate_flag')} | {tail}")
    print(f'wrote {out} ({res["runtime_seconds"]:.0f}s)')


if __name__ == '__main__':
    main()
