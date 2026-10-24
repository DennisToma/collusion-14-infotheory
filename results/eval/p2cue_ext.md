n = {'private': 15, 'neutral': 15, 'notes': 15, 'placebo': 15, 'randpartner': 15, 'none': 15}; judge agreement (y=1 / labelled) = {'private': [14, 14], 'neutral': [14, 14], 'notes': [0, 14], 'placebo': [0, 13], 'randpartner': [14, 14], 'none': [0, 13]}

| detector | arm | top-1 assigned pair (chance 2.5/15; p) | AUROC max-pair score, arm vs none | AUROC private vs arm (matched seeds) |
|---|---|---|---|---|
| pCMI (state+lags) | private | 6.0/15 (p=0.028) | 0.49 [0.28, 0.71] | – |
| pCMI (state+lags) | neutral | 3.3/15 (p=0.31) | 0.38 [0.17, 0.59] | 0.66 [0.42, 0.88] |
| pCMI (state+lags) | notes | 3.2/15 (p=0.42) | 0.22 [0.06, 0.42] | 0.78 [0.56, 0.95] |
| pCMI (state+lags) | placebo | 3.0/15 (p=0.47) | 0.28 [0.11, 0.49] | 0.76 [0.56, 0.92] |
| pCMI (state+lags) | randpartner | 2.3/15 (p=0.59) | 0.58 [0.36, 0.79] | 0.41 [0.18, 0.65] |
| lagged CMI (TE) | private | 6.0/15 (p=0.019) | 0.76 [0.56, 0.92] | – |
| lagged CMI (TE) | neutral | 3.3/15 (p=0.31) | 0.52 [0.31, 0.73] | 0.78 [0.58, 0.96] |
| lagged CMI (TE) | notes | 4.0/15 (p=0.23) | 0.61 [0.40, 0.82] | 0.67 [0.49, 0.84] |
| lagged CMI (TE) | placebo | 6.3/15 (p=0.011) | 0.69 [0.48, 0.88] | 0.53 [0.30, 0.76] |
| lagged CMI (TE) | randpartner | 1.2/15 (p=0.89) | 0.67 [0.47, 0.86] | 0.59 [0.37, 0.79] |
| MI (raw prices) | private | 10.5/15 (p=5e-05) | 0.69 [0.49, 0.88] | – |
| MI (raw prices) | neutral | 8.0/15 (p=0.00075) | 0.49 [0.28, 0.71] | 0.69 [0.48, 0.88] |
| MI (raw prices) | notes | 6.0/15 (p=0.027) | 0.54 [0.32, 0.75] | 0.65 [0.45, 0.83] |
| MI (raw prices) | placebo | 7.0/15 (p=0.007) | 0.66 [0.44, 0.84] | 0.54 [0.36, 0.74] |
| MI (raw prices) | randpartner | 1.0/15 (p=0.91) | 0.79 [0.63, 0.94] | 0.40 [0.24, 0.55] |
| pair_level (non-IT) | private | 12.0/15 (p=5e-05) | 0.91 [0.78, 1.00] | – |
| pair_level (non-IT) | neutral | 14.0/15 (p=5e-05) | 0.87 [0.72, 0.98] | 0.59 [0.35, 0.83] |
| pair_level (non-IT) | notes | 11.0/15 (p=5e-05) | 0.89 [0.76, 0.98] | 0.66 [0.41, 0.86] |
| pair_level (non-IT) | placebo | 12.5/15 (p=5e-05) | 0.91 [0.79, 1.00] | 0.58 [0.38, 0.78] |
| pair_level (non-IT) | randpartner | 3.0/15 (p=0.41) | 0.70 [0.50, 0.87] | 0.82 [0.68, 0.95] |
| markup over Nash (non-IT) | private | 12.0/15 (p=5e-05) | 0.98 [0.92, 1.00] | – |
| markup over Nash (non-IT) | neutral | 14.0/15 (p=5e-05) | 0.88 [0.74, 0.99] | 0.74 [0.52, 0.94] |
| markup over Nash (non-IT) | notes | 11.0/15 (p=5e-05) | 0.91 [0.79, 0.99] | 0.69 [0.50, 0.86] |
| markup over Nash (non-IT) | placebo | 12.5/15 (p=5e-05) | 0.91 [0.80, 0.99] | 0.64 [0.46, 0.80] |
| markup over Nash (non-IT) | randpartner | 3.0/15 (p=0.41) | 0.97 [0.91, 1.00] | 0.48 [0.27, 0.69] |

Market markup over Nash, arm − none (matched seeds, seed bootstrap): private +2.02 [+1.36, +2.69]; neutral +1.00 [+0.48, +1.56]; notes +1.45 [+0.77, +2.25]; placebo +1.45 [+0.83, +2.05]; randpartner +2.74 [+1.99, +3.50]
