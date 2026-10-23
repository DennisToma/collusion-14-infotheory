n runs = 125 (private 70, of which judge-verified agreement 70; none 35; legit 20)

| detector | AUROC private vs none | AUROC agreement vs none | AUROC legit vs none | top-1, private | top-1, agreement |
|---|---|---|---|---|---|
| pCMI (state+lags) | 0.52 [0.39, 0.64] | 0.52 [0.39, 0.64] | 0.45 [0.31, 0.60] | 18/70 (p=0.036, 2 tied) | 18/70 (p=0.036, 2 tied) |
| MI (raw prices) | 0.59 [0.47, 0.70] | 0.59 [0.47, 0.70] | 0.46 [0.31, 0.61] | 42/70 (p=4e-16, 3 tied) | 42/70 (p=4e-16, 3 tied) |
| lagged CMI (TE) | 0.45 [0.32, 0.58] | 0.45 [0.32, 0.58] | 0.46 [0.30, 0.63] | 22/70 (p=0.0017, 1 tied) | 22/70 (p=0.0017, 1 tied) |
| \|Pearson\| | 0.44 [0.32, 0.56] | 0.44 [0.32, 0.56] | 0.33 [0.19, 0.49] | 35/70 (p=1.4e-10, 1 tied) | 35/70 (p=1.4e-10, 1 tied) |
| pair_level (non-IT) | 0.98 [0.95, 1.00] | 0.98 [0.95, 1.00] | 0.75 [0.61, 0.87] | 63/70 (p=3.2e-41, 1 tied) | 63/70 (p=3.2e-41, 1 tied) |
| markup over Nash (non-IT) | 0.94 [0.90, 0.98] | 0.94 [0.90, 0.98] | 0.40 [0.24, 0.56] | 63/70 (p=3.2e-41, 1 tied) | 63/70 (p=3.2e-41, 1 tied) |

Paired-bootstrap AUROC differences (private vs none): pcmi-pair_level -0.46 [-0.58, -0.33]; pcmi-market_level -0.43 [-0.55, -0.29]; mi-pair_level -0.39 [-0.50, -0.28]; te-pair_level -0.53 [-0.66, -0.40]; pair_level-market_level +0.03 [-0.00, +0.08]

Control-surrogate null (vs none pool, α=0.05) flag rate, private / legit / none(LOO): pcmi 0.00 / 0.00 / 0.00; mi 0.06 / 0.00 / 0.03; te 0.00 / 0.00 / 0.00; pearson 0.00 / 0.00 / 0.00; pair_level 0.64 / 0.05 / 0.03; market_level 0.59 / 0.00 / 0.03
