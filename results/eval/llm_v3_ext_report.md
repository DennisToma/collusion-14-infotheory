n runs = 74 (private 45, of which judge-verified agreement 45; none 18; legit 11)

| detector | AUROC private vs none | AUROC agreement vs none | AUROC legit vs none | top-1, private | top-1, agreement |
|---|---|---|---|---|---|
| pCMI (state+lags) | 0.52 [0.32, 0.70] | 0.52 [0.32, 0.70] | 0.49 [0.28, 0.70] | 11/45 (p=0.12, 2 tied) | 11/45 (p=0.12, 2 tied) |
| MI (raw prices) | 0.56 [0.40, 0.70] | 0.56 [0.40, 0.70] | 0.40 [0.22, 0.62] | 27/45 (p=7.2e-11, 3 tied) | 27/45 (p=7.2e-11, 3 tied) |
| lagged CMI (TE) | 0.34 [0.18, 0.52] | 0.34 [0.18, 0.52] | 0.33 [0.14, 0.53] | 11/45 (p=0.12, 1 tied) | 11/45 (p=0.12, 1 tied) |
| \|Pearson\| | 0.41 [0.26, 0.57] | 0.41 [0.26, 0.57] | 0.34 [0.15, 0.58] | 23/45 (p=1.2e-07, 1 tied) | 23/45 (p=1.2e-07, 1 tied) |
| pair_level (non-IT) | 0.98 [0.94, 1.00] | 0.98 [0.94, 1.00] | 0.77 [0.59, 0.92] | 42/45 (p=1.7e-29) | 42/45 (p=1.7e-29) |
| markup over Nash (non-IT) | 0.92 [0.85, 0.98] | 0.92 [0.85, 0.98] | 0.35 [0.14, 0.58] | 42/45 (p=1.7e-29) | 42/45 (p=1.7e-29) |

Paired-bootstrap AUROC differences (private vs none): pcmi-pair_level -0.46 [-0.65, -0.29]; pcmi-market_level -0.41 [-0.60, -0.22]; mi-pair_level -0.42 [-0.57, -0.27]; te-pair_level -0.63 [-0.80, -0.46]; pair_level-market_level +0.05 [-0.00, +0.12]
