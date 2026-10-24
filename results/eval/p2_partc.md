| seller (dataset) | T | n C/A (excl.) | A markup | C − A markup [95% CI] | AUROC markup | AUROC pair_level | AUROC pCMI | agreement (judge) | executed [Jeffreys 95%] |
|---|---|---|---|---|---|---|---|---|---|
| gpt-6-luna (v1 reference) (`llm_v1`) | 20 | 16/21 (0) | +0.02 | 1.76 [1.22, 2.31] | 0.94 [0.86, 1.00] | 0.75 [0.55, 0.91] | 0.47 [0.28, 0.67] | 14/16 | 6/16 [0.174, 0.617] |
| gpt-6-luna, T=50 (v1 llm_long) (`llm_long`) | 50 | 8/8 (0) | +0.18 | 2.28 [1.28, 3.35] | 0.95 [0.81, 1.00] | 0.84 [0.59, 0.98] | 0.45 [0.16, 0.75] | 8/8 | 3/8 [0.119, 0.705] |
| deepseek-v4.1-flash (`llm_ds_p2`) | 20 | 15/15 (0) | -0.58 | 3.75 [2.77, 4.68] | 0.99 [0.96, 1.00] | 1.00 [0.97, 1.00] | 0.57 [0.36, 0.77] | 15/15 | 2/15 [0.029, 0.363] |
| qwen3.8-27B base (`llm_qb_p2`) | 20 | 2/3 (0) | -1.97 | 1.32 [-0.36, 2.99] | – | – | – | – | – |

E64: frozen detectors on EXECUTED vs not-executed collusion (each vs all A games of the same set; game bootstrap 95% CI)

| seller (dataset) | executed n | market_level exec / not-exec | pair_level exec / not-exec | pcmi exec / not-exec |
|---|---|---|---|---|
| gpt-6-luna (v1 reference) | 6/16 | 0.98 [0.93, 1.00] / 0.92 [0.80, 1.00] | 0.76 [0.45, 1.00] / 0.74 [0.51, 0.94] | 0.52 [0.29, 0.75] / 0.45 [0.23, 0.68] |
| gpt-6-luna, T=50 (v1 llm_long) | 3/8 | 1.00 [1.00, 1.00] / 0.93 [0.75, 1.00] | 0.88 [0.58, 1.00] / 0.81 [0.53, 1.00] | 0.46 [0.12, 0.88] / 0.45 [0.12, 0.75] |
| deepseek-v4.1-flash | 2/15 | 1.00 [1.00, 1.00] / 0.99 [0.95, 1.00] | 1.00 [1.00, 1.00] / 0.99 [0.97, 1.00] | 0.97 [0.87, 1.00] / 0.51 [0.30, 0.74] |
