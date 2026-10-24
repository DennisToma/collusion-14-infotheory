"""Claims x denominators (DIRECTION 2026-10-24 15:50, directive 3): for each abstract claim, in how many LLM sets
(and seller models) does it hold? Reads existing results only, no LLM calls.

  uv run python scripts/claims_denominators.py   -> results/eval/claims_denominators.{json,md}
Sets: every complete C-vs-A set in results/eval/p2_partc.json (pilots with n < 10 per arm excluded), the five
E43 wording arms (results/eval/p2_variants.json, counted as a separate group) and E66 (Q2.2 strong framing).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EV = ROOT / 'results' / 'eval'


def sets():
    out = []
    partc = json.loads((EV / 'p2_partc.json').read_text())
    for name, r in partc.items():
        if not isinstance(r, dict) or 'auroc_pcmi' not in r or min(r['n_A'], r['n_C']) < 10:
            continue
        b = r.get('behaviour', {})
        out.append(dict(set=name, group='main', models=sorted(set(r['models'])), n=(r['n_A'], r['n_C']),
                        d=r['C_minus_A_markup'], d_ci=r['C_minus_A_ci'], ml=r['auroc_market_level'],
                        pl=r['auroc_pair_level'], pcmi=r['auroc_pcmi'], pcmi_ci=r['auroc_pcmi_ci'],
                        executed=(b.get('executed'), b.get('n_C_labelled')), tacit=(r['tacit_A'], r['n_A'])))
    var = json.loads((EV / 'p2_variants.json').read_text())
    for name, r in var['arms'].items():
        out.append(dict(set=f'wording:{name}', group='wording', models=sorted(set(r['models'])),
                        n=(r['n_A'], r['n_C']), d=r['C_minus_A_markup'], d_ci=r['C_minus_A_ci'],
                        ml=r['auroc_market_level'], pl=r['auroc_pair_level'], pcmi=r['auroc_pcmi'],
                        pcmi_ci=r['auroc_pcmi_ci'], executed=(None, None), tacit=(None, None)))
    return out


CLAIMS = [  # (id, abstract claim, test on one set -> True/False/None (not evaluable))
    ('premium', 'channel raises markup (C - A CI > 0)', lambda s: s['d_ci'][0] > 0),
    ('pcmi_null', 'pCMI not above chance (AUROC CI includes 0.5 or lies below)', lambda s: s['pcmi_ci'][0] <= 0.5),
    ('level_beats_pcmi', 'market-level markup AUROC > pCMI AUROC', lambda s: s['ml'] > s['pcmi']),
    ('spill', 'pair_level AUROC <= market-level AUROC (spillover costs the relative screen)', lambda s: s['pl'] <= s['ml']),
    ('exec_minority', 'agreements executed in <= 50% of channel games',
     lambda s: None if s['executed'][0] is None else s['executed'][0] <= 0.5 * s['executed'][1]),
    ('no_tacit', 'no-channel markets rarely tacit-high (<= 10%)',
     lambda s: None if s['tacit'][0] is None else s['tacit'][0] <= 0.1 * s['tacit'][1]),
]


def main():
    ss = sets()
    rows = []
    for cid, text, test in CLAIMS:
        for group in ('main', 'wording'):
            g = [s for s in ss if s['group'] == group]
            res = [(s['set'], test(s)) for s in g]
            ev = [(n, v) for n, v in res if v is not None]
            if not ev:
                continue
            k = sum(v for _, v in ev)
            models = sorted({m for s in g for m in s['models'] if (s['set'], True) in ev})
            rows.append(dict(claim=cid, text=text, group=group, k=k, K=len(ev), models_where_holds=models,
                             fails=[n for n, v in ev if not v]))
    out = dict(sets=ss, claims=rows,
               note='E66 (Q2.2 strong framing) is not a C-vs-A set here: channel labels are not ground truth there '
                    '(tacit 19/20); see results/eval/strongF_ext.json')
    (EV / 'claims_denominators.json').write_text(json.dumps(out, indent=1))
    md = ['| claim | group | holds in | models where it holds | fails in |', '|---|---|---|---|---|']
    for r in rows:
        md.append(f"| {r['text']} | {r['group']} | {r['k']}/{r['K']} | {len(r['models_where_holds'])} | "
                  f"{', '.join(r['fails']) or '-'} |")
    (EV / 'claims_denominators.md').write_text('\n'.join(md) + '\n')
    print('\n'.join(md))
    print('main sets:', [s['set'] for s in ss if s['group'] == 'main'])


if __name__ == '__main__':
    main()
