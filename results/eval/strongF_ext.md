`llm_p2strongF` (E66): n = {'executed': 13, 'nonexec': 7, 'tacit_high': 19, 'competitive': 1, 'private': 20, 'none': 20}; executed [13, 20, [0.432, 0.828]]; tacit-high [19, 20, [0.789, 0.995]]; mean market − Nash (2nd half) by class: executed +5.63, nonexec +3.75, tacit_high +5.73, competitive +1.00, private +4.97, none +5.50

**Verdict (declared rule on pCMI, executed vs competitive): not evaluable (executed or competitive class n < 3)**

| contrast | pcmi | te | mi | pair_level | market_level |
|---|---|---|---|---|---|
| executed_vs_competitive (n [13, 1]) | 1.00 [1.00, 1.00]* | 1.00 [1.00, 1.00]* | 1.00 [1.00, 1.00]* | 0.23 [0.00, 0.46]* | 1.00 [1.00, 1.00]* |
| executed_vs_tacit_high (n [13, 19]) | 0.44 [0.23, 0.64] | 0.56 [0.36, 0.75] | 0.47 [0.25, 0.67] | 0.47 [0.27, 0.68] | 0.51 [0.30, 0.73] |
| executed_vs_nonexec (n [13, 7]) | 0.44 [0.20, 0.69] | 0.35 [0.10, 0.64] | 0.32 [0.10, 0.56] | 0.35 [0.05, 0.66] | 0.77 [0.52, 0.96] |
| private_vs_none (n [20, 20]) | 0.46 [0.27, 0.64] | 0.61 [0.42, 0.79] | 0.54 [0.35, 0.71] | 0.51 [0.33, 0.69] | 0.44 [0.26, 0.63] |
| tacit_high_vs_competitive (n [19, 1]) | 0.95 [0.84, 1.00]* | 1.00 [1.00, 1.00]* | 0.95 [0.87, 1.00]* | 0.42 [0.21, 0.63]* | 1.00 [1.00, 1.00]* |

rivals markup in executed runs − matched none market markup (2nd half): +0.71 [-0.69, +2.32] (n=13)

pair markup in executed runs − matched none market markup (2nd half): +0.65 [-0.74, +2.40] (n=13)

`*` = a class has n < 3 (descriptive only). AUROC CI: stratified run bootstrap (2000).
