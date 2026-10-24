| family (dataset) | n C/A | A markup | C markup | C − A markup [95% CI] | AUROC markup | AUROC pair_level | AUROC pCMI | seller price SD (median) |
|---|---|---|---|---|---|---|---|---|
| deepseek-v4.1-flash (`llm_ds_p2`) | 15/15 | -0.58 | +3.16 | 3.75 [2.77, 4.68] | 0.99 [0.96, 1.00] | 1.00 [0.97, 1.00] | 0.57 [0.36, 0.77] | 1.06 |
| gpt-6-luna (`llm_v1`) | 16/21 | +0.02 | +1.78 | 1.76 [1.22, 2.31] | 0.94 [0.86, 1.00] | 0.75 [0.55, 0.91] | 0.47 [0.28, 0.67] | 0.67 |

Family x condition interaction (C − A deepseek minus C − A luna): +1.99 [0.90, 3.07]

Degeneracy: deepseek {'n_sellers': 120, 'sd_median': 1.06, 'sd_min': 0.22, 'constant_sellers': 0, 'distinct_prices_median': 5.0}; luna {'n_sellers': 296, 'sd_median': 0.67, 'sd_min': 0.0, 'constant_sellers': 1, 'distinct_prices_median': 4.0}

Declared rule (E45): {'markup_ci_excludes_0': True, 'level_beats_pcmi': True, 'n_ok_for_auroc': True, 'verdict': 'HOLDS'}
