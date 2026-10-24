"""Markdown table + pooled control FPR for REPORT P2.5 from results/p2/market_test.json (E52).
    uv run python scripts/p2_market_table.py [--split test]"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
from experiments.scripted import wilson

ap = argparse.ArgumentParser(); ap.add_argument('--split', default='test'); a = ap.parse_args()
R = json.loads((Path(__file__).resolve().parent.parent / 'results' / 'p2' / f'market_{a.split}.json').read_text())
S = R['summaries']
k = lambda d: round(d['rate'] * 30)
lines = ['| market (N, μ, Nash) | family | control pCMI false flags (T=100 / T=30) | s=0.6 T=100: pCMI / markup / pair_level TPR | '
         's=0.15 T=100: pCMI / markup / pair_level | s=0.15 T=30: pCMI / markup / pair_level | AUROC s=0.15 T=30 pCMI / markup |',
         '|---|---|---|---|---|---|---|']
pooled = {'100': [0, 0], '30': [0, 0]}
for key, d in S.items():
    market, fam, T = key.split('/')
    if T != 'T100':
        continue
    d30 = S[f'{market}/{fam}/T30']
    f = lambda g, m: f"{k(g[m])}" if m in g else '–'
    c100, c30 = k(d['control']['pcmi_flag']), k(d30['control']['pcmi_flag'])
    for h, c in (('100', c100), ('30', c30)):
        pooled[h][0] += c; pooled[h][1] += 30
    trip = lambda g: f"{f(g,'pcmi_flag')} / {f(g,'markup_surrogate_flag')} / {f(g,'pair_level_surrogate_flag')}"
    lines.append(f"| {market} ({d['n_agents']}, {d['mu']}, {d['nash_mean']:.0f}) | {fam} | {c100}/30, {c30}/30 | {trip(d['pair'])} | "
                 f"{trip(d['weak'])} | {trip(d30['weak'])} | {d30['weak']['auroc']['pcmi']['auc']:.2f} [{d30['weak']['auroc']['pcmi']['ci95'][0]:.2f}, {d30['weak']['auroc']['pcmi']['ci95'][1]:.2f}] / "
                 f"{d30['weak']['auroc']['markup']['auc']:.2f} |")
print('\n'.join(lines))
for h, (c, n) in pooled.items():
    lo, hi = wilson([1] * c + [0] * (n - c))
    print(f'pooled control pCMI false flags T={h}: {c}/{n} = {c/n:.3f} [{lo:.3f}, {hi:.3f}]')
