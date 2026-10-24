E70 grid: 6 complete sweep(s), 192 games
cells with C − A > 0: 13/16 (sign test p = 0.0106); pooled C − A +0.98 [0.652, 1.293]
cells market-level AUROC > pCMI: 12/16 (ties 1)
pooled AUROC: market_level 0.74 [0.661, 0.805], pair_level 0.72 [0.649, 0.795], pcmi 0.51 [0.429, 0.589], te 0.62 [0.543, 0.698]
TE confirmatory: confirmed
spillover (rivals in channel games − no-channel markets): +0.60 [0.297, 0.913]
executed: 44/96
amend2 (a) qwen-cell pCMI 0.46 [0.347, 0.576]: not replicated; luna: level 0.72 − pCMI 0.56 = +0.16 [0.007, 0.295]; qwen: level 0.76 − pCMI 0.46 = +0.29 [0.146, 0.441]
amend2 (b) public-board share of agent-rounds (no-channel / channel): luna 0.04 / 0.10; qwen 1.00 / 1.00

| factor | low → high | main effect on C − A [95% CI] |
|---|---|---|
| model | gpt-6-luna → qwen-3.6-35b | +0.79 [0.10, 1.44] |
| cost | private → public | +0.79 [0.12, 1.41] |
| rivals | visible → hidden | -0.50 [-1.11, 0.15] |
| channel | every → first | +0.33 [-0.28, 0.96] |
| memory | short → full | +0.38 [-0.24, 1.04] |
| shocks | none → random | -0.34 [-0.96, 0.28] |
| framing | base → longrun | -0.12 [-0.77, 0.52] |

| cell | M | board share A / C |
|---|---|---|
| c00 | gpt-6-luna | 0.00 / 0.00 |
| c01 | gpt-6-luna | 0.00 / 0.00 |
| c02 | gpt-6-luna | 0.00 / 0.16 |
| c03 | gpt-6-luna | 0.00 / 0.16 |
| c04 | gpt-6-luna | 0.01 / 0.16 |
| c05 | gpt-6-luna | 0.00 / 0.15 |
| c06 | gpt-6-luna | 0.00 / 0.00 |
| c07 | gpt-6-luna | 0.32 / 0.16 |
| c08 | qwen-3.6-35b | 1.00 / 1.00 |
| c09 | qwen-3.6-35b | 1.00 / 1.00 |
| c10 | qwen-3.6-35b | 1.00 / 1.00 |
| c11 | qwen-3.6-35b | 1.00 / 1.00 |
| c12 | qwen-3.6-35b | 1.00 / 1.00 |
| c13 | qwen-3.6-35b | 1.00 / 1.00 |
| c14 | qwen-3.6-35b | 1.00 / 1.00 |
| c15 | qwen-3.6-35b | 1.00 / 1.00 |
