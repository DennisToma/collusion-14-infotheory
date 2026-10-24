| family (dataset) | n C/A | A markup | C markup | C − A markup [95% CI] | AUROC markup | AUROC pair_level | AUROC pCMI | seller price SD (median) |
|---|---|---|---|---|---|---|---|---|
| deepseek-v4.1-flash (`llm_ds_p2`) | 8/9 | -0.61 | +3.17 | 3.78 [2.81, 4.75] | – | – | – | 1.1 |
| gpt-6-luna (`llm_v1`) | 16/21 | +0.02 | +1.78 | 1.76 [1.22, 2.31] | 0.94 [0.86, 1.00] | 0.75 [0.55, 0.91] | 0.47 [0.28, 0.67] | 0.67 |

Family x condition interaction (C − A deepseek minus C − A luna): +2.02 [0.90, 3.12]

Degeneracy: deepseek {'n_sellers': 68, 'sd_median': 1.1, 'sd_min': 0.22, 'constant_sellers': 0, 'distinct_prices_median': 5.0}; luna {'n_sellers': 296, 'sd_median': 0.67, 'sd_min': 0.0, 'constant_sellers': 1, 'distinct_prices_median': 4.0}
