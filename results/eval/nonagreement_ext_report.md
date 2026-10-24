n = {'mon_private': 14, 'mon_none': 6, 'fp_private': 16}; decision (pair_level pooled, declared rule): contradicted

| detector | top-1 v3mon (monitor) | top-1 v3fp (firm) | top-1 pooled | AUROC v3mon private vs none |
|---|---|---|---|---|
| pCMI (state+lags) | 3.0/14 (p=0.42) | 1.5/16 (p=0.85) | 4.5/30 (p=0.6) | 0.56 [0.29, 0.82] |
| MI (raw prices) | 1.0/14 (p=0.93) | 2.5/16 (p=0.66) | 3.5/30 (p=0.85) | 0.54 [0.26, 0.79] |
| lagged CMI (TE) | 2.0/14 (p=0.66) | 1.5/16 (p=0.85) | 3.5/30 (p=0.81) | 0.81 [0.61, 0.98] |
| \|Pearson\| | 2.0/14 (p=0.7) | 2.7/16 (p=0.52) | 4.7/30 (p=0.58) | 0.52 [0.24, 0.82] |
| MI first differences | 4.0/14 (p=0.19) | 1.5/16 (p=0.9) | 5.5/30 (p=0.47) | 0.26 [0.02, 0.57] |
| \|Pearson\| first differences | 4.0/14 (p=0.19) | 3.8/16 (p=0.23) | 7.8/30 (p=0.092) | 0.48 [0.18, 0.79] |
| pair_level (non-IT) | 2.0/14 (p=0.71) | 1.3/16 (p=0.87) | 3.3/30 (p=0.82) | 0.42 [0.15, 0.69] |
| markup over Nash (non-IT) | 2.0/14 (p=0.71) | 1.3/16 (p=0.87) | 3.3/30 (p=0.82) | 0.48 [0.18, 0.79] |
