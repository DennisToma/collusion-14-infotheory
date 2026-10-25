"""Six-slide checkpoint deck from finalized saved results; no analysis or LLM calls.

uv run python scripts/phase2_fig.py
uv run python scripts/slides.py -> PRESENTATION.md
E68/E70 narrative lines quote their finalized registered analyses (e68_cda.json, e70_grid.json).
PDF export remains a separate, scheduled release action.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent


def load(name):
    return json.loads((ROOT / 'results/eval' / f'{name}.json').read_text())


def interval(value, bounds, signed=False):
    spec = '+.2f' if signed else '.2f'
    return f'{value:{spec}} [{bounds[0]:.2f}, {bounds[1]:.2f}]'.replace('-', '−')


def render():
    c = load('claims_denominators')
    claims = {r['claim']: r for r in c['claims'] if r['group'] == 'main'}
    main = [s for s in c['sets'] if s['group'] == 'main']
    count = lambda key: f"{claims[key]['k']}/{claims[key]['K']}"
    nmodels = len({m for s in main for m in s['models']})
    nmin = min(n for s in main for n in s['n'])
    nmax = max(n for s in main for n in s['n'])
    pc = load('p2_partc')
    long = load('long_power_llm_long_p2_T60')
    pooled = pc['E64_pooled']['all sets']
    strong = load('strongF_ext')
    gate = load('gate_test')['metrics']
    cost = json.loads((ROOT / 'results/p2/costasym_test.json').read_text())['summaries']['A/costasym']
    variants = load('p2_variants')['arms']
    # The baseline is the no-channel mean markup, not the C-A contrast.
    baselines = [v['A_markup'] for v in variants.values()]
    old = pc['llm_g56l_p2']
    ex = pooled['pcmi']['executed']
    en = pooled['n_executed'] + pooled['n_not_executed']
    p60, ml60 = long['prefix']['60']['pcmi'], long['prefix']['60']['pair_markup']
    qb = pc['llm_qb36_p2']
    f = lambda r, key: interval(r[key], r[f'{key}_ci'])
    # Short table labels keep the nine-set result readable on a projected slide.
    names = {'llm_v1': 'luna', 'llm_ds_p2': 'deepseek', 'llm_long_p2_T60': 'luna',
             'llm_qa_p2': 'Qwen3.8 abl.', 'llm_qb_p2': 'Qwen3.8 base', 'llm_g56l_p2': 'older luna',
             'llm_strong_qa': 'Qwen3.8 abl. + memory', 'llm_qa36_p2': 'Qwen3.6 abl.',
             'llm_qb36_p2': 'Qwen3.6 base'}
    auroc_rows = '\n'.join(f"| {names[r['set']]} (T={pc[r['set']]['T']}) | "
                           f"{f(pc[r['set']], 'auroc_market_level')} | {f(pc[r['set']], 'auroc_pcmi')} |"
                           for r in main)
    pct = lambda x: f'{x * 100:.0f}%'
    flagged = lambda d, k: round(d[k]['rate'] * d['n'])
    s = []
    s.append(f'''# LLM private pricing channels raise the price level, with no detected contemporaneous co-movement
Apart AI Collusion Sprint · Q1.4 · checkpoint, Phase 2

**Question.** Can prices and public market state reveal colluding sellers without accusing firms that share a shock or policy?

**Finding.** Channel prices rise in **{count('premium')} sets ({nmodels} seller models)**. Market-level markup beats pCMI in **{count('level_beats_pcmi')}**; pCMI is not above chance in **{count('pcmi_null')}**.

**Scope.** These scores distinguish channel assignment. A price rise alone does not verify an agreement; channel-free markets can also sustain high prices.

MI measures shared information; pCMI measures residual dependence after public state and all sellers' lagged prices. A level screen measures markup over the competitive Nash price.

Source: REPORT main claim; P2.13; `claims_denominators.json`.''')
    s.append(f'''## Validation: opposite failure modes
Four sellers, repeated differentiated-price market. Scripted sellers validate detectors; LLM sellers test the substantive claim. Frozen estimators, predeclared Phase 2 analyses.

| scripted condition | level-screen flags | pCMI flags |
|---|---|---|
| planted shared-signal coordination | see REPORT §4.1 | {pct(gate['pcmi']['C']['flag_rate'])} |
| unequal private costs, no channel | {flagged(cost, 'market_level_surrogate_flag')}/{cost['n']} | {flagged(cost, 'pcmi_flag')}/{cost['n']} |

**Conditioning helps but does not prove intent:** raw MI flags {pct(gate['mi']['B']['flag_rate'])} of common-shock markets; pCMI flags {pct(gate['pcmi']['B']['flag_rate'])} under the shift null (target 5%). Shared random seeds and legitimate leader-follower pricing remain confounds.

Sources: `gate_test.json`, `results/p2/costasym_test.json`; REPORT §4.1, P2.4. Flag counts use different registered nulls in these two experiments.''')
    s.append(f'''## Across {len(main)} sets: channel assignment is mostly a level
| seller | market-level AUROC [95% CI] | pCMI AUROC [95% CI] |
|---|---|---|
{auroc_rows}

{nmin}–{nmax} games per arm; CIs bootstrap games. The sets share designs/models. Base Qwen3.6 is the pCMI exception: {f(qb, 'auroc_pcmi')}.

Sources: `p2_partc.json`, P2.13 inclusion list. Non-channel benchmarks are model- and prompt-specific.''')
    s.append(f'''## Longer games and executed agreements do not rescue pCMI
| registered comparison | market-level AUROC [95% CI] | pCMI AUROC [95% CI] |
|---|---|---|
| E44, T=60, {long['n']['A']} + {long['n']['C']} games | {interval(*ml60)} | {interval(*p60)} |
| E65, Qwen memory, T=40 | {f(pc['llm_strong_qa'], 'auroc_market_level')} | {f(pc['llm_strong_qa'], 'auroc_pcmi')} |

**Executed only:** {pooled['n_executed']}/{en} channel games over {len(pooled['sets'])} sets; pooled pCMI {interval(ex['auroc'], ex['ci'])}. Execution uses agreement + kept floor + supra-Nash price. Selecting on high prices inflates the level screen; no such level AUROC is claimed here.

E65's declared executed-only test is **{pc['E65_verdict']['verdict']}** ({pc['E65_verdict']['pcmi_executed_vs_A']['n_pos']} executed); memory is not a confirmed rescue. E44's planting check establishes sensitivity to one shared-move alternative, not every form of collusion.

Sources: `long_power_llm_long_p2_T60.json`, `p2_partc.json`; REPORT P2.8, P2.11.''')
    s.append(f'''## The reference market determines what a flag means
| context | finalized evidence |
|---|---|
| five prompt wordings | no-channel mean markup {min(baselines):+.2f} … {max(baselines):+.2f} |
| older gpt-5.6-luna | {old['tacit_A']}/{old['n_A']} no-channel markets tacit-high |
| luna + memory + strong profit framing (Q2.2) | {strong['tacit_rate'][0]}/{strong['tacit_rate'][1]} tacit-high without a channel; {strong['executed_rate'][0]}/{strong['executed_rate'][1]} agreements executed with one |

Under strong framing the declared detector test is **not evaluable**: competitive no-channel markets are too rare. Channel labels stop being ground truth.

**Abliteration is no simple explanation.** The channel premium does not detectably increase in the Qwen pairs tested (REPORT P2.11b); serving precision is a caveat. E69 interaction, abliterated − base: {interval(*pc['E69_abliterated_minus_base_C_minus_A'], signed=True)}.

Sources: `p2_variants.json`, `p2_partc.json`, `strongF_ext.json`; REPORT P2.7, P2.11.''')
    s.append('''## Use screens to trigger an audit, not to deliver a verdict
* **Combine evidence.** Absolute levels need cost data; dependence misses sustained levels. Relative pair screens lose power when prices rise market-wide.
* **Match the reference.** Model, prompt, board availability and costs matter. At 1% collusion prevalence no tested frozen flag reaches point-estimate precision 0.25 (P2.1).
* **Validate execution separately.** Opportunity, agreement and kept pricing are different labels. High prices without a channel need their own label.
* **Generality and transfer:** registered 16-cell grid (E70, 192 games): C − A positive in 13/16 cells, level > pCMI in 12/16 (point estimates); lagged dependence (TE) weakly above chance, 0.62 [0.54, 0.70]; exploratory E72: TE names the channel pair 30/96 (chance 1/6), signal in non-executed channel games (0.73 vs executed 0.49; post hoc). External double auction (E68): inconclusive, chat raises asks only +0.39 [+0.06, +0.69]. The declared E70 follow-up (factor: model) was not confirmed: +1.07 [−0.20, +2.41].
* **Limitations:** one core market family, modest samples, unadjusted comparisons and estimator-specific blind spots. A combined screen-and-audit pipeline is a proposal, not a tested deployment.

Full evidence: `REPORT.md`; commands in §6; all experiments, corrections and duds in `EXPERIMENTS.tsv`. Markdown and figures reflect this checkpoint; PDFs retain the last scheduled export.''')
    return '<!-- generated by scripts/slides.py from finalized results; do not edit by hand -->\n\n' + '\n\n---\n\n'.join(s) + '\n'


def main():
    (ROOT / 'PRESENTATION.md').write_text(render())
    print('wrote PRESENTATION.md')


if __name__ == '__main__':
    main()
