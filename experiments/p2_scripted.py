"""Phase-2 scripted experiments on DEV seeds only; no LLMs or held-out data.

    uv run python -m experiments.p2_scripted coalition
    uv run python -m experiments.p2_scripted onset
    uv run python -m experiments.p2_scripted costasym

Raw datasets default to /var/tmp/c14/p2s; --scratch can select another directory.
Every experiment uses Pool(3), 100 rounds, signal strength 0.6, and by default
30 independent runs per group and 100 shift draws. Run labels are used only
for evaluation; detector inputs are prices and public market state.
"""
from __future__ import annotations

import argparse
import itertools
import json
from multiprocessing import Pool
from pathlib import Path
import time

import numpy as np
from sklearn.metrics import roc_auc_score

from detectors.infotheory import PAIR_NAMES, score_groups, score_run
from experiments.scripted import boot_ci, wilson
from sim.market import AGENTS, run_game, write_dataset

ROOT = Path(__file__).resolve().parent.parent
SCRATCH = Path('/var/tmp/c14/p2_scratch')
PAIRS = list(itertools.combinations(range(4), 2))
TRIPLES = [''.join(g) for g in itertools.combinations(AGENTS, 3)]
ALPHA, T, STRENGTH = 0.05, 100, 0.6
DEFAULT_SEEDS = {'coalition': 200, 'onset': 210, 'costasym': 220}
LOCKED_SEEDS = {'coalition': 2001, 'onset': 2002, 'costasym': 2003}  # data/SPLITS.md; run once with frozen config


def rate(values):
    values = list(values)
    return {'rate': float(np.mean(values)), 'ci95': wilson(values)} if values else None


def mean_score(values):
    values = list(values)
    return {'mean': float(np.mean(values)), 'ci95': boot_ci(values)} if values else None


def auc(pos, neg, seed=0):
    """Run AUROC with a stratified bootstrap over both run populations."""
    pos, neg = np.asarray(pos), np.asarray(neg)
    y = [1] * len(pos) + [0] * len(neg)
    comparison = (pos[:, None] > neg).astype(float) + 0.5 * (pos[:, None] == neg)
    rng = np.random.default_rng(seed)
    draws = [comparison[np.ix_(rng.integers(len(pos), size=len(pos)),
                              rng.integers(len(neg), size=len(neg)))].mean() for _ in range(1000)]
    return {'auc': float(roc_auc_score(y, np.r_[pos, neg])),
            'ci95': [float(q) for q in np.percentile(draws, [2.5, 97.5])]}


def level_scores(P, public_cost):
    """Relative pair levels and absolute markups over the public-cost Nash."""
    nash = np.where(np.asarray(public_cost) == 8, 12, 10)
    pair_level, market_level = {}, {}
    for (i, j), name in zip(PAIRS, PAIR_NAMES):
        others = [k for k in range(4) if k not in (i, j)]
        pair_level[name] = float((P[:, [i, j]].mean(1) - P[:, others].mean(1)).mean())
        market_level[name] = float((P[:, [i, j]].mean(1) - nash).mean())
    return pair_level, market_level, float((P.mean(1) - nash).mean())


def cusum_path(P, kappa=0.5):
    """Max over six separately accumulated, one-sided pair-gap CUSUMs."""
    gaps = np.column_stack([P[:, [i, j]].mean(1) - P[:, [k for k in range(4) if k not in (i, j)]].mean(1)
                            for i, j in PAIRS])
    acc = np.zeros(6)
    path = []
    for gap in gaps:
        acc = np.maximum(0, acc + gap - kappa)
        path.append(float(acc.max()))
    return path


def _one(cfg):
    """One independent game and its scores; safe to run in a process pool."""
    rng = np.random.default_rng(cfg['seed'])
    group, exp = cfg['group'], cfg['experiment']
    assigned = sorted(rng.choice(AGENTS, 2, replace=False).tolist())
    kwargs, members, high_cost_pair = {}, [], None
    if group == 'pair' or group.startswith('onset'):
        members = assigned
        kwargs['pair'] = members
        if group.startswith('onset'):
            kwargs['onset'] = int(group.removeprefix('onset'))
    elif group.startswith('coalition'):
        members = sorted(rng.choice(AGENTS, int(group[-1]), replace=False).tolist())
        kwargs['coalition'] = members
    elif group == 'costasym':
        high_cost_pair = ''.join(assigned)
        kwargs['cost_offsets'] = {a: 2 for a in assigned}
    rows, gt = run_game(cfg['run_id'], cfg['seed'], T, cfg['family'], strength=STRENGTH, **kwargs)
    write_dataset(cfg['run_id'], [(rows, gt)], root=Path(cfg['scratch']))
    P = np.array([[a['price'] for a in row['agents']] for row in rows], float)
    states = [json.dumps(row['market'], sort_keys=True) for row in rows]
    levels = sorted(set(states))
    S = np.array([levels.index(s) for s in states])
    base = {k: cfg[k] for k in ('run_id', 'seed', 'group', 'family')}
    base.update(members=members, high_cost_pair=high_cost_pair)
    if exp == 'onset':
        # Reuse the same seed at each look so each look follows score_run's
        # exact null. Correlated repeated looks are deliberately unadjusted.
        looks = [{'n_rounds': end, 'p': score_run(P[:end], S[:end], B=cfg['B'], seed=cfg['seed'])['_run_p']['pcmi']}
                 for end in range(20, T + 1, 10)]
        base.update(onset=kwargs.get('onset'), cusum_path=cusum_path(P), pcmi_looks=looks)
        return base
    scores = score_run(P, S, B=cfg['B'], seed=cfg['seed'])
    pair_level, market_level, markup = level_scores(P, [r['market']['cost'] for r in rows])
    base.update(pairs={n: scores[n] for n in PAIR_NAMES}, run_p=scores['_run_p'],
                n_null=scores['_n_null'], pair_level=pair_level, market_level=market_level,
                top_pcmi=max(PAIR_NAMES, key=lambda n: scores[n]['score']['pcmi']),
                top_pair_level=max(PAIR_NAMES, key=pair_level.get),
                scores={'pcmi': max(scores[n]['score']['pcmi'] for n in PAIR_NAMES),
                        'mi': max(scores[n]['score']['mi'] for n in PAIR_NAMES),
                        'ni_pcmi': max(scores[n]['score']['ni_pcmi'] for n in PAIR_NAMES),
                        'pair_level': max(pair_level.values()),
                        'market_level': max(market_level.values()), 'market_mean_markup': markup})
    if exp == 'coalition':
        groups = score_groups(P, S, B=cfg['B'], seed=cfg['seed'])
        # Same draws imply equality of both pairwise and max-pair p-values.
        assert scores['_run_p']['pcmi'] == groups['_run_p']['tc2']
        for name in PAIR_NAMES:
            assert np.isclose(groups[name]['score'], scores[name]['score']['pcmi'])
            assert groups[name]['p'] == scores[name]['p']['pcmi']
        base.update(groups=groups, top_tc3=max(TRIPLES, key=lambda n: groups[n]['score']))
        base['run_p'].update(groups['_run_p'])
        base['scores'].update(tc3=max(groups[n]['score'] for n in TRIPLES), tc4=groups['ABCD']['score'])
    return base


def surrogate_p(row, controls, key):
    """Rank a max score against same-family controls, leaving self out."""
    null = [r['scores'][key] for r in controls if r['run_id'] != row['run_id']]
    return float((1 + sum(s >= row['scores'][key] - 1e-12 for s in null)) / (1 + len(null)))


def summarize_scores(rows, exp):
    summaries = {}
    for family in sorted({r['family'] for r in rows}):
        controls = [r for r in rows if r['family'] == family and r['group'] == 'control']
        for group in sorted({r['group'] for r in rows if r['family'] == family}):
            rr = [r for r in rows if r['family'] == family and r['group'] == group]
            out = {'n': len(rr), 'pcmi_flag': rate(r['run_p']['pcmi'] < ALPHA for r in rr)}
            for key in ('pair_level', 'market_level', 'market_mean_markup', 'ni_pcmi'):
                for r in rr:
                    r.setdefault('surrogate_p', {})[key] = surrogate_p(r, controls, key)
                out[key] = mean_score(r['scores'][key] for r in rr)
                out[key + '_surrogate_flag'] = rate(r['surrogate_p'][key] < ALPHA for r in rr)
            if rr[0]['members']:
                out['top_pcmi_inside_coalition'] = rate(set(r['top_pcmi']) <= set(r['members']) for r in rr)
                out['top_pair_level_inside_coalition'] = rate(set(r['top_pair_level']) <= set(r['members']) for r in rr)
            if exp == 'coalition':
                for key in ('tc3', 'tc4'):
                    out[key + '_flag'] = rate(r['run_p'][key] < ALPHA for r in rr)
                if group == 'coalition3':
                    out['top_tc3_exact'] = rate(r['top_tc3'] == ''.join(r['members']) for r in rr)
                out['synergy_by_subset'] = {g: mean_score(r['groups'][g]['synergy'] for r in rr) for g in TRIPLES}
                if group == 'coalition3':
                    out['true_coalition_synergy'] = mean_score(r['groups'][''.join(r['members'])]['synergy'] for r in rr)
                if group != 'control':
                    out['auroc_vs_control'] = {key: auc([r['scores'][key] for r in rr], [r['scores'][key] for r in controls])
                                               for key in ('pcmi', 'tc3', 'tc4', 'market_mean_markup',
                                                           'pair_level', 'market_level', 'ni_pcmi')}
            else:
                out['mi_flag'] = rate(r['run_p']['mi'] < ALPHA for r in rr)
                if group == 'costasym':
                    for key in ('pcmi', 'pair_level'):
                        out['high_cost_pair_top_' + key] = rate(r['top_' + key] == r['high_cost_pair'] for r in rr)
            summaries[f'{family}/{group}'] = out
    return summaries


def first_alarm(path, h):
    return next((t for t, value in enumerate(path) if value > h), None)


def summarize_onset(rows, h=None):
    controls = [r for r in rows if r['group'] == 'control']
    maxima = [max(r['cusum_path']) for r in controls]
    # A conservative nonrandomised empirical 95th percentile: n=30 cannot
    # represent exactly 5%; strict exceedance gives at most 1/30 alarms.
    # On the locked test split h is frozen from the dev run (out-of-sample calibration).
    in_sample = h is None
    if in_sample:
        h = float(np.quantile(maxima, 1 - ALPHA, method='higher'))
    for r in rows:
        r['alarms'] = {'cusum': first_alarm(r['cusum_path'], h),
                       'pcmi': next((look['n_rounds'] - 1 for look in r['pcmi_looks'] if look['p'] < ALPHA), None)}
    out = {}
    for group in ('control', 'onset25', 'onset50'):
        rr = [r for r in rows if r['group'] == group]
        methods = {}
        for method in ('cusum', 'pcmi'):
            alarms = [r['alarms'][method] for r in rr]
            result = {'any_alarm': rate(a is not None for a in alarms)}
            if group == 'control':
                result['false_alarm'] = result['any_alarm']
            else:
                onset = rr[0]['onset']
                delays = [a - onset for a in alarms if a is not None and a >= onset]
                result.update(pre_onset_alarm=rate(a is not None and a < onset for a in alarms),
                              detection=rate(a is not None and a >= onset for a in alarms),
                              n_delays=len(delays),
                              delay_median=float(np.median(delays)) if delays else None,
                              delay_iqr=[float(q) for q in np.percentile(delays, [25, 75])] if delays else None)
            methods[method] = result
        out[group] = methods
    return out, {'h': h, 'kappa': 0.5, 'target_fpr': ALPHA, 'n_control_calibration': len(controls),
                 'quantile_method': 'higher', 'alarm_rule': 'max pair CUSUM > h',
                 'calibration_is_in_sample': in_sample,
                 'delay_definition': 'zero-based first alarm index minus zero-based onset; exclude pre-onset alarms',
                 'pcmi_looks_round_counts': list(range(20, T + 1, 10)),
                 'pcmi_repeated_testing_adjustment': None}


def print_table(exp, summaries):
    if exp == 'onset':
        print('group     method  alarm  post-onset  pre-onset  delay median [IQR]')
        for group, methods in summaries.items():
            for method, d in methods.items():
                print(f"{group:9} {method:6} {d['any_alarm']['rate']:.3f}  "
                      f"{d.get('detection', {}).get('rate', '-')}  "
                      f"{d.get('pre_onset_alarm', {}).get('rate', '-')}  "
                      f"{d.get('delay_median', '-')} {d.get('delay_iqr', '')}")
    else:
        tail = 'tc3   tc4   top-pair-inside' if exp == 'coalition' else 'MI    high-pair top level/pCMI'
        print(f'group              pCMI  level-flag  {tail}')
        for group, d in summaries.items():
            suffix = (f"{d['tc3_flag']['rate']:.3f} {d['tc4_flag']['rate']:.3f} "
                      f"{d.get('top_pcmi_inside_coalition', {}).get('rate', '-')}" if exp == 'coalition' else
                      f"{d['mi_flag']['rate']:.3f} "
                      f"{d.get('high_cost_pair_top_pair_level', {}).get('rate', '-')} / "
                      f"{d.get('high_cost_pair_top_pcmi', {}).get('rate', '-')}")
            print(f"{group:18} {d['pcmi_flag']['rate']:.3f} {d['pair_level_surrogate_flag']['rate']:.3f}       {suffix}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='experiment', required=True)
    for exp in DEFAULT_SEEDS:
        sp = sub.add_parser(exp)
        sp.add_argument('--seed0', type=int, default=DEFAULT_SEEDS[exp])
        sp.add_argument('--n', type=int, default=30)
        sp.add_argument('--B', type=int, default=100)
        sp.add_argument('--scratch', type=Path, default=SCRATCH)
        sp.add_argument('--test', action='store_true',
                        help='LOCKED test split (data/SPLITS.md): seed0 fixed per experiment; onset uses h frozen from dev')
    args = ap.parse_args()
    if args.test:
        args.seed0 = LOCKED_SEEDS[args.experiment]
    elif not 200 <= args.seed0 <= 299:
        ap.error('DEV only: seed0 must be in 200..299')
    if args.n < 2 or args.B < 20:
        ap.error('n must be >= 2 and B >= 20')
    start = time.monotonic()
    exp = args.experiment
    groups = {'coalition': ['pair', 'coalition3', 'coalition4', 'control'],
              'onset': ['onset25', 'onset50', 'control'],
              'costasym': ['costasym', 'pair', 'control']}[exp]
    families = ['A', 'B'] if exp == 'coalition' else ['A']
    split = 'test' if args.test else 'dev'
    dataset_name = f'p2_{exp}_{split}_s{args.seed0}_n{args.n}_B{args.B}'
    scratch = args.scratch.resolve() / dataset_name
    scratch.mkdir(parents=True, exist_ok=True)
    cfgs = []
    for family, group, rep in itertools.product(families, groups, range(args.n)):
        k = len(cfgs)
        cfgs.append({'experiment': exp, 'family': family, 'group': group, 'seed': args.seed0 * 1_000_000 + k,
                     'run_id': f'{dataset_name}_{family}_{group}_{rep:03}', 'B': args.B, 'scratch': str(scratch)})
    rows = []
    with Pool(3) as pool:
        for row in pool.imap_unordered(_one, cfgs):
            rows.append(row)
            if len(rows) % 30 == 0 or len(rows) == len(cfgs):
                print(f'{exp}: {len(rows)}/{len(cfgs)} runs ({time.monotonic() - start:.1f}s)', flush=True)
    rows.sort(key=lambda r: r['run_id'])
    calibration = None
    if exp == 'onset':
        h = (json.loads((ROOT / 'results' / 'p2' / 'onset_dev.json').read_text())['calibration']['h']
             if args.test else None)
        summaries, calibration = summarize_onset(rows, h)
    else:
        summaries = summarize_scores(rows, exp)
    result = {'experiment': exp, 'split': split, 'seed0': args.seed0, 'n_per_group': args.n, 'T': T, 'B': args.B,
              'strength': STRENGTH, 'collusion_type': 'signal', 'workers': 3, 'alpha': ALPHA,
              'design': 'lin: state dummies plus all four lagged prices',
              'scratch': str(scratch), 'runtime_seconds': time.monotonic() - start,
              'ci_method': 'Wilson 95% for proportions; 1000-draw bootstrap for means; stratified bootstrap for AUROC',
              'summaries': summaries, 'runs': rows}
    if calibration is not None:
        result['calibration'] = calibration
    out = ROOT / 'results' / 'p2' / f'{exp}_{split}.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print_table(exp, summaries)
    print(f'Wrote {out}; runtime {result["runtime_seconds"]:.1f}s', flush=True)


if __name__ == '__main__':
    main()
