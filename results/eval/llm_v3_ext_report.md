n runs = 70 (private 42, of which judge-verified agreement 37; none 18; legit 10)

| detector | AUROC private vs none | AUROC agreement vs none | AUROC legit vs none | top-1, private | top-1, agreement |
|---|---|---|---|---|---|
| pCMI (state+lags) | 0.53 [0.35, 0.72] | 0.53 [0.34, 0.71] | 0.50 [0.29, 0.71] | 11/42 (p=0.079, 2 tied) | 10/37 (p=0.077, 2 tied) |
| MI (raw prices) | 0.55 [0.39, 0.70] | 0.56 [0.40, 0.71] | 0.43 [0.23, 0.66] | 25/42 (p=4.6e-10, 2 tied) | 22/37 (p=5.3e-09, 2 tied) |
| lagged CMI (TE) | 0.33 [0.17, 0.51] | 0.32 [0.16, 0.49] | 0.33 [0.14, 0.53] | 10/42 (p=0.15, 1 tied) | 10/37 (p=0.077) |
| \|Pearson\| | 0.40 [0.24, 0.56] | 0.39 [0.24, 0.55] | 0.36 [0.16, 0.59] | 21/42 (p=6.6e-07, 1 tied) | 17/37 (p=3.1e-05, 1 tied) |
| pair_level (non-IT) | 0.98 [0.94, 1.00] | 0.98 [0.93, 1.00] | 0.76 [0.56, 0.92] | 40/42 (p=4.5e-29) | 35/37 (p=2.7e-25) |
| markup over Nash (non-IT) | 0.93 [0.85, 0.98] | 0.93 [0.85, 0.98] | 0.28 [0.09, 0.51] | 40/42 (p=4.5e-29) | 35/37 (p=2.7e-25) |

Paired-bootstrap AUROC differences (private vs none): pcmi-pair_level -0.45 [-0.63, -0.26]; pcmi-market_level -0.40 [-0.59, -0.20]; mi-pair_level -0.43 [-0.60, -0.28]; te-pair_level -0.65 [-0.81, -0.48]; pair_level-market_level +0.05 [-0.00, +0.13]
