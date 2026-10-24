"""Phase-2 gap 7: market-model robustness of the scripted calibration and power results.

    uv run python -m experiments.p2_market            # DEV, seed0 230
    uv run python -m experiments.p2_market --test     # LOCKED test, seed0 2004 (data/SPLITS.md), run once

Markets (sim.market.run_game n_agents / mu): base N=4 mu=3 (the v1 market), N=2, N=6, more elastic
demand (mu=1.5) and less elastic demand (mu=4.5). Families A (constant state) and B (common demand and
cost shocks). Groups: control (all independent quantal best response) and pair (two sellers share the
private signal, s=0.6; for N=2 the pair is the whole market) and weak (same, s=0.15). Every run is scored
on the full T=100 game and on its first 30 rounds (amended after dev showed s=.3 / T=100 at ceiling). T=100, B=100, n=30 per group, frozen
detectors (score_run, lin design). Level screens use same-market controls as the surrogate reference
(leave-one-out), so they are calibrated per market by construction; the question is power.
"""
from __future__ import annotations

import argparse
import itertools
import json
import time
from math import comb
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from detectors.infotheory import score_run
from experiments.p2_scripted import auc, mean_score, rate
from sim.market import PRICES, profits, run_game

ROOT = Path(__file__).resolve().parent.parent
MARKETS = {'base': (4, 3.0), 'N2': (2, 3.0), 'N6': (6, 3.0), 'elastic': (4, 1.5), 'inelastic': (4, 4.5)}
ALPHA, T, DEV_SEED, TEST_SEED = 0.05, 100, 230, 2004
STRENGTH = {'control': 0.0, 'pair': 0.6, 'weak': 0.15}
HORIZONS = (100, 30)
POS = ('pair', 'weak')


def nash_price(n, mu, cost):
    """Lowest symmetric discrete Nash price at low demand (benchmark for the markup screen)."""
    for p in PRICES:
        br = PRICES[np.argmax([profits([q] + [p] * (n - 1), cost, 'low', mu)[0] for q in PRICES])]
        if br == p:
            return int(p)
    raise ValueError((n, mu, cost))


def _one(cfg):
    n, mu = MARKETS[cfg['market']]
    agents = [chr(65 + k) for k in range(n)]
    rng = np.random.default_rng(cfg['seed'])
    pair = sorted(rng.choice(agents, 2, replace=False).tolist()) if cfg['group'] != 'control' else None
    rows, _ = run_game(cfg['run_id'], cfg['seed'], T, cfg['family'], pair=pair, strength=cfg['strength'] if 'strength' in cfg else STRENGTH[cfg['group']],
                       collusion_type=cfg.get('ctype', 'signal'),
                       n_agents=n, mu=mu)
    P = np.array([[a['price'] for a in r['agents']] for r in rows], float)
    states = [json.dumps(r['market'], sort_keys=True) for r in rows]
    levels = sorted(set(states))
    S = np.array([levels.index(s) for s in states])
    nash_t = np.array([nash_price(n, mu, r['market']['cost']) for r in rows])
    out = {k: cfg[k] for k in ('run_id', 'seed', 'market', 'family', 'group')}
    out.update(pair=''.join(pair) if pair else None, mean_price=float(P.mean()), nash_mean=float(nash_t.mean()), h={})
    for H in HORIZONS:  # full game and its first-H-rounds prefix, same frozen statistics
        Ph, nash = P[:H], nash_t[:H]
        sc = score_run(Ph, S[:H], B=cfg['B'], seed=cfg['seed'])
        names = [k for k in sc if not k.startswith('_')]
        pair_level = {}
        for nm in names:
            i, j = ord(nm[0]) - 65, ord(nm[1]) - 65
            others = [k for k in range(n) if k not in (i, j)]
            if others:
                pair_level[nm] = float((Ph[:, [i, j]].mean(1) - Ph[:, others].mean(1)).mean())
        out['h'][str(H)] = {
            'mean_price': float(Ph.mean()), 'nash_mean': float(nash.mean()), 'n_null': sc['_n_null'], 'run_p': sc['_run_p'],
            'top_pcmi': max(names, key=lambda m: sc[m]['score']['pcmi']),
            'top_pair_level': max(pair_level, key=pair_level.get) if pair_level else None,
            'scores': {'pcmi': max(sc[m]['score']['pcmi'] for m in names),
                       'mi': max(sc[m]['score']['mi'] for m in names),
                       'pair_level': max(pair_level.values()) if pair_level else None,
                       'markup': float((Ph.mean(1) - nash).mean())}}
        if 'ctype' in cfg:  # p2_rotation: also lagged TE (not in the E52 outputs)
            out['h'][str(H)]['scores']['te'] = max(sc[m]['score']['te'] for m in names)
    return out


def surrogate_p(row, controls, key, H):
    null = [r['h'][H]['scores'][key] for r in controls if r['run_id'] != row['run_id']]
    obs = row['h'][H]['scores'][key]
    return float((1 + sum(s >= obs - 1e-12 for s in null)) / (1 + len(null)))


def summarize(rows):
    out = {}
    for market, family, H in itertools.product(MARKETS, ('A', 'B'), [str(h) for h in HORIZONS]):
        rr = [r for r in rows if r['market'] == market and r['family'] == family]
        ctl = [r for r in rr if r['group'] == 'control']
        n = MARKETS[market][0]
        keys = ['pcmi', 'mi', 'markup'] + (['pair_level'] if n > 2 else [])
        d = {'n_agents': n, 'mu': MARKETS[market][1], 'n_control': len(ctl),
             'nash_mean': float(np.mean([r['h'][H]['nash_mean'] for r in rr])),
             'mean_price': {g: mean_score(r['h'][H]['mean_price'] for r in rr if r['group'] == g) for g in ('control',) + POS},
             'n_null_range': [min(r['h'][H]['n_null'] for r in rr), max(r['h'][H]['n_null'] for r in rr)]}
        for g in ('control',) + POS:
            grp = [r for r in rr if r['group'] == g]
            d[g] = {'pcmi_flag': rate(r['h'][H]['run_p']['pcmi'] < ALPHA for r in grp),
                    'mi_flag': rate(r['h'][H]['run_p']['mi'] < ALPHA for r in grp)}
            for key in ('markup', 'pair_level'):
                if key in keys:
                    d[g][key + '_surrogate_flag'] = rate(surrogate_p(r, ctl, key, H) < ALPHA for r in grp)
            if g in POS:
                d[g]['top_pcmi_is_pair'] = rate(r['h'][H]['top_pcmi'] == r['pair'] for r in grp)
                if n > 2:
                    d[g]['top_pair_level_is_pair'] = rate(r['h'][H]['top_pair_level'] == r['pair'] for r in grp)
                d[g]['auroc'] = {key: auc([r['h'][H]['scores'][key] for r in grp], [r['h'][H]['scores'][key] for r in ctl]) for key in keys}
        d['chance_top_pair'] = 1 / comb(n, 2)
        out[f'{market}/{family}/T{H}'] = d
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--test', action='store_true')
    ap.add_argument('--n', type=int, default=30)
    ap.add_argument('--B', type=int, default=100)
    a = ap.parse_args()
    seed0 = TEST_SEED if a.test else DEV_SEED
    split = 'test' if a.test else 'dev'
    start = time.monotonic()
    cfgs = []
    for market, family, group, rep in itertools.product(MARKETS, ('A', 'B'), ('control',) + POS, range(a.n)):
        cfgs.append({'market': market, 'family': family, 'group': group, 'B': a.B,
                     'seed': seed0 * 1_000_000 + len(cfgs), 'run_id': f'p2m_{split}_{market}_{family}_{group}_{rep:03}'})
    rows = []
    with Pool(3) as pool:
        for r in pool.imap_unordered(_one, cfgs):
            rows.append(r)
            if len(rows) % 100 == 0:
                print(f'{len(rows)}/{len(cfgs)} ({time.monotonic() - start:.0f}s)', flush=True)
    rows.sort(key=lambda r: r['run_id'])
    summ = summarize(rows)
    res = {'experiment': 'market_robustness', 'split': split, 'seed0': seed0, 'n_per_group': a.n, 'T': T, 'B': a.B,
           'strength': STRENGTH, 'horizons': HORIZONS, 'alpha': ALPHA, 'markets': {k: {'n_agents': v[0], 'mu': v[1]} for k, v in MARKETS.items()},
           'ci_method': 'Wilson 95% for proportions; bootstrap for means and AUROC (stratified)',
           'runtime_seconds': time.monotonic() - start, 'summaries': summ, 'runs': rows}
    out = ROOT / 'results' / 'p2' / f'market_{split}.json'
    out.write_text(json.dumps(res, indent=2, allow_nan=False) + '\n')
    print('market/fam/T       group nash price  pCMI(ctl)->flag  MI(ctl)->flag  level(ctl)->flag  markup(ctl)->flag  AUROC pcmi/level/markup  top-pCMI (chance)')
    f = lambda g, key: f"{g[key]['rate']:.2f}" if key in g else '  - '
    for k, d in summ.items():
        c = d['control']
        for g in POS:
            p, au = d[g], d[g]['auroc']
            print(f"{k:17} {g:5} {d['nash_mean']:5.1f} {d['mean_price']['control']['mean']:5.2f}/{d['mean_price'][g]['mean']:5.2f} "
                  f"{f(c,'pcmi_flag')}->{f(p,'pcmi_flag')}   {f(c,'mi_flag')}->{f(p,'mi_flag')}  "
                  f"{f(c,'pair_level_surrogate_flag')}->{f(p,'pair_level_surrogate_flag')}   "
                  f"{f(c,'markup_surrogate_flag')}->{f(p,'markup_surrogate_flag')}   "
                  f"{au['pcmi']['auc']:.2f}/{au['pair_level']['auc'] if 'pair_level' in au else float('nan'):.2f}/{au['markup']['auc']:.2f}   "
                  f"{p['top_pcmi_is_pair']['rate']:.2f} ({d['chance_top_pair']:.2f})")
    print(f'wrote {out} ({res["runtime_seconds"]:.0f}s)')


if __name__ == '__main__':
    main()
