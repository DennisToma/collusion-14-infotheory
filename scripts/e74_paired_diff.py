"""E74 (robustness, declared; DIRECTION 2026-10-25 04:15 #1): paired AUROC difference, max-pair markup minus pCMI
(and minus TE), on the SAME channel-vs-control games. Zero LLM calls; saved run scores only.

  uv run python scripts/e74_paired_diff.py   -> results/eval/e74_paired_diff.json
Sets: the nine P2.13 main sets (claims_denominators.json, group 'main'; E44 T=60 = llm_long_p2_T60 is one of them),
scores from results/eval/<set>.json run_scores at the set's T; E70 pooled within cell (e70_grid.json games).
Bootstrap: paired, class-stratified (E70: stratified by cell x arm) game resampling, 2000 draws, seed 0; each draw
resamples games once and recomputes both AUROCs on that resample. Point AUROCs are asserted to match the saved ones.
"""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
EV = ROOT / 'results' / 'eval'
B, SEED = 2000, 0
LEVEL, OTHERS = 'market_level', ('pcmi', 'te')


def au(p, q):
    p, q = np.asarray(p, float), np.asarray(q, float)
    return float((p[:, None] > q[None]).mean() + .5 * (p[:, None] == q[None]).mean())


def strat_au(groups, key):
    """groups: list of (pos_rows, neg_rows); AUROC over within-group (pos, neg) pairs only."""
    num = den = 0.0
    for p, q in groups:
        a, b = np.array([g[key] for g in p], float), np.array([g[key] for g in q], float)
        if len(a) and len(b):
            num += (a[:, None] > b[None]).sum() + .5 * (a[:, None] == b[None]).sum()
            den += len(a) * len(b)
    return float(num / den)


def paired(groups):
    """Point estimates and paired bootstrap of level - other for each other detector."""
    rng = np.random.default_rng(SEED)
    dets = (LEVEL,) + OTHERS
    pt = {k: strat_au(groups, k) for k in dets}
    bs = {k: [] for k in dets}
    for _ in range(B):
        bg = [([p[i] for i in rng.integers(0, len(p), len(p))], [q[i] for i in rng.integers(0, len(q), len(q))])
              for p, q in groups]
        for k in dets:
            bs[k].append(strat_au(bg, k))
    out = {k: round(pt[k], 3) for k in dets}
    for k in OTHERS:
        d = np.array(bs[LEVEL]) - np.array(bs[k])
        out[f'level_minus_{k}'] = dict(delta=round(pt[LEVEL] - pt[k], 3),
                                       ci=[round(float(np.quantile(d, .025)), 3), round(float(np.quantile(d, .975)), 3)],
                                       p_boot_le0=round(float((d <= 0).mean()), 4))
    out['n'] = [sum(len(q) for _, q in groups), sum(len(p) for p, _ in groups)]  # [A, C]
    return out


def main_sets():
    cd = json.loads((EV / 'claims_denominators.json').read_text())
    partc = json.loads((EV / 'p2_partc.json').read_text())
    res = {}
    for s in cd['sets']:
        if s['group'] != 'main':
            continue
        name = s['set']
        T = partc[name]['T']
        sc = json.loads((EV / f'{name}.json').read_text())['run_scores'][str(T)]
        gt = {g['run_id']: g for g in map(json.loads, open(ROOT / 'data' / name / 'ground_truth.jsonl'))}
        rows = {c: [dict(**{k: sc[k][r] for k in (LEVEL,) + OTHERS}) for r in sorted(sc[LEVEL])
                    if gt[r]['condition'] == c] for c in 'AC'}
        r = paired([(rows['C'], rows['A'])])
        for k, saved in ((LEVEL, s['ml']), ('pcmi', s['pcmi'])):
            assert abs(r[k] - saved) < 1e-3, (name, k, r[k], saved)
        assert r['n'] == [partc[name]['n_A'], partc[name]['n_C']], (name, r['n'])
        r['models'] = s['models']
        res[name] = r
    return res


def e70():
    e = json.loads((EV / 'e70_grid.json').read_text())
    groups = []
    for cell in sorted({g['cell'] for g in e['games']}):
        gs = [dict(**{k: g['scores'][k] for k in (LEVEL,) + OTHERS}) for g in e['games'] if g['cell'] == cell]
        ch = [g['channel'] for g in e['games'] if g['cell'] == cell]
        groups.append(([x for x, c in zip(gs, ch) if c], [x for x, c in zip(gs, ch) if not c]))
    r = paired(groups)
    for k in (LEVEL,) + OTHERS:
        assert abs(r[k] - e['pooled_auroc'][k]['auroc']) < 1e-3, (k, r[k], e['pooled_auroc'][k])
    return r


def main():
    ms = main_sets()
    lo = {n: r['level_minus_pcmi']['ci'][0] for n, r in ms.items()}
    k = sum(v > 0 for v in lo.values())
    smallest = min(ms, key=lambda n: ms[n]['level_minus_pcmi']['delta'])
    from math import comb
    npos = sum(r['level_minus_pcmi']['delta'] > 0 for r in ms.values())
    sign_p = sum(comb(9, j) for j in range(npos, 10)) / 2 ** 9
    e = e70()
    out = dict(
        description=__doc__.strip().split('\n')[0], B=B, seed=SEED, main_sets=ms, E70_pooled=e,
        summary=dict(k_level_minus_pcmi_ci_above_0=k, K=len(ms),
                     unresolved=[n for n, v in lo.items() if v <= 0],
                     smallest_delta_set=smallest, smallest_delta=ms[smallest]['level_minus_pcmi'],
                     point_level_gt_pcmi=npos, sign_test_one_sided_p=round(sign_p, 4),
                     k_level_minus_te_ci_above_0=sum(r['level_minus_te']['ci'][0] > 0 for r in ms.values()),
                     E70_level_minus_pcmi=e['level_minus_pcmi'], E70_level_minus_te=e['level_minus_te'],
                     E70_te_branch='below level' if e['level_minus_te']['ci'][0] > 0 else 'not resolvably below level'))
    (EV / 'e74_paired_diff.json').write_text(json.dumps(out, indent=1))
    f = lambda d: f"{d['delta']:+.2f} [{d['ci'][0]:+.2f}, {d['ci'][1]:+.2f}]"
    print('| set | models | n (A, C) | level | pCMI | TE | Δ level − pCMI | Δ level − TE |')
    print('|---|---|---|---|---|---|---|---|')
    for n, r in list(ms.items()) + [('E70 pooled (within cell)', e)]:
        print(f"| {n} | {', '.join(r.get('models', ['grid']))} | {r['n'][0]}, {r['n'][1]} | {r[LEVEL]:.2f} | "
              f"{r['pcmi']:.2f} | {r['te']:.2f} | {f(r['level_minus_pcmi'])} | {f(r['level_minus_te'])} |")
    print(json.dumps(out['summary'], indent=1))


if __name__ == '__main__':
    main()
