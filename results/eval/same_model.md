# E48 same-model confound (T=20)

pairs per type: {"luna-luna": 186, "bystander": 120, "channel_realized": 17, "channel_all": 24, "channel_other": 7, "sol-sol": 12, "cross": 48}
runs per type: {"luna-luna": 41, "bystander": 24, "channel_realized": 17, "channel_all": 24, "channel_other": 7, "sol-sol": 12, "cross": 12}

## pair AUROC [95% CI, games resampled jointly]

| pos vs neg | pcmi | pcmi_ownlag | mi | te | pair_level | pair_markup |
|---|---|---|---|---|---|---|
| channel_all|luna-luna | 0.49 [0.38, 0.62] | 0.44 [0.31, 0.57] | 0.31 [0.18, 0.47] | 0.49 [0.36, 0.63] | 0.93 [0.88, 0.97] | 0.96 [0.90, 1.00] |
| channel_all|sol-sol | 0.72 [0.53, 0.89] | 0.65 [0.45, 0.83] | 0.27 [0.12, 0.45] | 0.43 [0.25, 0.63] | 0.89 [0.77, 0.98] | 1.00 [0.98, 1.00] |
| channel_all|cross | 0.58 [0.43, 0.74] | 0.57 [0.41, 0.72] | 0.36 [0.20, 0.54] | 0.55 [0.40, 0.70] | 0.93 [0.87, 0.97] | 1.00 [0.98, 1.00] |
| channel_all|bystander | 0.57 [0.44, 0.71] | 0.55 [0.41, 0.69] | 0.56 [0.46, 0.66] | 0.57 [0.43, 0.70] | 0.94 [0.91, 0.97] | 0.61 [0.58, 0.69] |
| channel_realized|luna-luna | 0.47 [0.32, 0.63] | 0.42 [0.27, 0.58] | 0.14 [0.05, 0.25] | 0.42 [0.27, 0.58] | 0.91 [0.84, 0.97] | 0.95 [0.89, 0.99] |
| channel_realized|sol-sol | 0.70 [0.49, 0.89] | 0.64 [0.41, 0.85] | 0.06 [0.00, 0.19] | 0.36 [0.16, 0.58] | 0.85 [0.69, 0.97] | 0.99 [0.97, 1.00] |
| channel_realized|cross | 0.57 [0.38, 0.76] | 0.56 [0.37, 0.73] | 0.16 [0.04, 0.31] | 0.46 [0.28, 0.66] | 0.91 [0.83, 0.97] | 1.00 [0.97, 1.00] |
| channel_realized|bystander | 0.56 [0.39, 0.72] | 0.54 [0.36, 0.70] | 0.42 [0.26, 0.57] | 0.50 [0.34, 0.64] | 0.92 [0.88, 0.96] | 0.57 [0.46, 0.71] |
| luna-luna|cross | 0.59 [0.51, 0.67] | 0.64 [0.54, 0.73] | 0.62 [0.48, 0.75] | 0.56 [0.46, 0.65] | 0.50 [0.48, 0.51] | 0.35 [0.20, 0.51] |
| sol-sol|cross | 0.33 [0.14, 0.55] | 0.37 [0.17, 0.60] | 0.65 [0.45, 0.84] | 0.67 [0.57, 0.77] | 0.56 [0.37, 0.73] | 0.51 [0.44, 0.59] |

## AUROC(channel vs same-model) - AUROC(channel vs cross) [joint game bootstrap]

| comparison | pcmi | pcmi_ownlag | mi | te | pair_level | pair_markup |
|---|---|---|---|---|---|---|
| channel_all: luna-luna - cross | -0.09 [-0.17, -0.01] | -0.13 [-0.23, -0.04] | -0.05 [-0.14, +0.04] | -0.05 [-0.14, +0.03] | +0.00 [-0.03, +0.04] | -0.04 [-0.10, -0.00] |
| channel_all: sol-sol - cross | +0.14 [-0.03, +0.31] | +0.08 [-0.11, +0.25] | -0.09 [-0.19, -0.01] | -0.12 [-0.22, -0.01] | -0.04 [-0.12, +0.03] | -0.00 [-0.00, +0.00] |
| channel_realized: luna-luna - cross | -0.10 [-0.18, -0.01] | -0.14 [-0.24, -0.04] | -0.02 [-0.12, +0.06] | -0.04 [-0.13, +0.05] | +0.01 [-0.04, +0.05] | -0.04 [-0.10, -0.00] |
| channel_realized: sol-sol - cross | +0.13 [-0.04, +0.30] | +0.08 [-0.12, +0.26] | -0.10 [-0.21, -0.02] | -0.11 [-0.21, -0.01] | -0.06 [-0.17, +0.04] | -0.00 [-0.00, +0.00] |

## seller price SD (no-channel A)

{"llm_v1:gpt-6-luna": {"n_sellers": 84, "mean_sd": 0.706, "n_sd_below_0.5": 19}, "llm_mixed2:gpt-6.1-sol": {"n_sellers": 24, "mean_sd": 0.955, "n_sd_below_0.5": 0}, "llm_mixed2:gpt-6-luna": {"n_sellers": 24, "mean_sd": 0.629, "n_sd_below_0.5": 6}, "llm_long:gpt-6-luna": {"n_sellers": 32, "mean_sd": 0.681, "n_sd_below_0.5": 9}}

## pCMI shift-null pair flags (p<0.05): flags, pairs, [rate, game-bootstrap CI]

{"luna-luna": [37, 186, [0.199, [0.133, 0.281]]], "bystander": [15, 120, [0.125, [0.075, 0.183]]], "channel_realized": [3, 17, [0.176, [0.0, 0.353]]], "channel_all": [5, 24, [0.208, [0.083, 0.375]]], "channel_other": [2, 7, [0.286, [0.0, 0.714]]], "sol-sol": [0, 12, [0.0, [0.0, 0.0]]], "cross": [4, 48, [0.083, [0.0, 0.167]]]}

## mean scores

- luna-luna: {"pcmi": 0.183, "pcmi_ownlag": 0.162, "mi": 0.328, "te": 0.126, "pair_level": -0.003, "pair_markup": 0.138}
- bystander: {"pcmi": 0.109, "pcmi_ownlag": 0.054, "mi": 0.156, "te": 0.089, "pair_level": -0.113, "pair_markup": 1.971}
- channel_realized: {"pcmi": 0.064, "pcmi_ownlag": 0.041, "mi": 0.099, "te": 0.089, "pair_level": 0.421, "pair_markup": 1.943}
- channel_all: {"pcmi": 0.074, "pcmi_ownlag": 0.051, "mi": 0.231, "te": 0.121, "pair_level": 0.566, "pair_markup": 2.31}
- channel_other: {"pcmi": 0.099, "pcmi_ownlag": 0.076, "mi": 0.553, "te": 0.198, "pair_level": 0.918, "pair_markup": 3.204}
- sol-sol: {"pcmi": 0.023, "pcmi_ownlag": 0.018, "mi": 0.32, "te": 0.15, "pair_level": 0.046, "pair_markup": 0.473}
- cross: {"pcmi": 0.037, "pcmi_ownlag": 0.023, "mi": 0.246, "te": 0.087, "pair_level": 0.0, "pair_markup": 0.45}

## reference-market (surrogate) null: flags/n (pool size, min attainable p)

- pair_markup alpha0.05: C_vs_lunaA(matched) 5/16 (pool 21, min p 0.045); C_vs_longA(matched,other batch) 0/16 (pool 8, min p 0.111); C_vs_mixed(mismatched) 0/16 (pool 12, min p 0.077); lunaA_LOO(matched) 1/21 (pool 21, min p 0.048); lunaA_vs_mixed(mismatched) 0/21 (pool 12, min p 0.077); mixed_vs_lunaA(mismatched) 0/12 (pool 21, min p 0.045); mixed_LOO(matched) 0/12 (pool 12, min p 0.083); longA_vs_lunaA(matched,other batch) 0/8 (pool 21, min p 0.045)
- pair_markup alpha0.1: C_vs_lunaA(matched) 13/16 (pool 21, min p 0.045); C_vs_longA(matched,other batch) 0/16 (pool 8, min p 0.111); C_vs_mixed(mismatched) 15/16 (pool 12, min p 0.077); lunaA_LOO(matched) 2/21 (pool 21, min p 0.048); lunaA_vs_mixed(mismatched) 4/21 (pool 12, min p 0.077); mixed_vs_lunaA(mismatched) 0/12 (pool 21, min p 0.045); mixed_LOO(matched) 1/12 (pool 12, min p 0.083); longA_vs_lunaA(matched,other batch) 1/8 (pool 21, min p 0.045)
- pair_level alpha0.05: C_vs_lunaA(matched) 9/16 (pool 21, min p 0.045); C_vs_longA(matched,other batch) 0/16 (pool 8, min p 0.111); C_vs_mixed(mismatched) 0/16 (pool 12, min p 0.077); lunaA_LOO(matched) 1/21 (pool 21, min p 0.048); lunaA_vs_mixed(mismatched) 0/21 (pool 12, min p 0.077); mixed_vs_lunaA(mismatched) 1/12 (pool 21, min p 0.045); mixed_LOO(matched) 0/12 (pool 12, min p 0.083); longA_vs_lunaA(matched,other batch) 2/8 (pool 21, min p 0.045)
- pair_level alpha0.1: C_vs_lunaA(matched) 10/16 (pool 21, min p 0.045); C_vs_longA(matched,other batch) 0/16 (pool 8, min p 0.111); C_vs_mixed(mismatched) 7/16 (pool 12, min p 0.077); lunaA_LOO(matched) 1/21 (pool 21, min p 0.048); lunaA_vs_mixed(mismatched) 0/21 (pool 12, min p 0.077); mixed_vs_lunaA(mismatched) 1/12 (pool 21, min p 0.045); mixed_LOO(matched) 1/12 (pool 12, min p 0.083); longA_vs_lunaA(matched,other batch) 2/8 (pool 21, min p 0.045)
- pcmi alpha0.05: C_vs_lunaA(matched) 0/16 (pool 21, min p 0.045); C_vs_longA(matched,other batch) 0/16 (pool 8, min p 0.111); C_vs_mixed(mismatched) 0/16 (pool 12, min p 0.077); lunaA_LOO(matched) 1/21 (pool 21, min p 0.048); lunaA_vs_mixed(mismatched) 0/21 (pool 12, min p 0.077); mixed_vs_lunaA(mismatched) 0/12 (pool 21, min p 0.045); mixed_LOO(matched) 0/12 (pool 12, min p 0.083); longA_vs_lunaA(matched,other batch) 0/8 (pool 21, min p 0.045)
- pcmi alpha0.1: C_vs_lunaA(matched) 1/16 (pool 21, min p 0.045); C_vs_longA(matched,other batch) 0/16 (pool 8, min p 0.111); C_vs_mixed(mismatched) 8/16 (pool 12, min p 0.077); lunaA_LOO(matched) 2/21 (pool 21, min p 0.048); lunaA_vs_mixed(mismatched) 11/21 (pool 12, min p 0.077); mixed_vs_lunaA(mismatched) 0/12 (pool 21, min p 0.045); mixed_LOO(matched) 1/12 (pool 12, min p 0.083); longA_vs_lunaA(matched,other batch) 0/8 (pool 21, min p 0.045)
- mi alpha0.05: C_vs_lunaA(matched) 1/16 (pool 21, min p 0.045); C_vs_longA(matched,other batch) 0/16 (pool 8, min p 0.111); C_vs_mixed(mismatched) 0/16 (pool 12, min p 0.077); lunaA_LOO(matched) 1/21 (pool 21, min p 0.048); lunaA_vs_mixed(mismatched) 0/21 (pool 12, min p 0.077); mixed_vs_lunaA(mismatched) 0/12 (pool 21, min p 0.045); mixed_LOO(matched) 0/12 (pool 12, min p 0.083); longA_vs_lunaA(matched,other batch) 0/8 (pool 21, min p 0.045)
- mi alpha0.1: C_vs_lunaA(matched) 1/16 (pool 21, min p 0.045); C_vs_longA(matched,other batch) 0/16 (pool 8, min p 0.111); C_vs_mixed(mismatched) 1/16 (pool 12, min p 0.077); lunaA_LOO(matched) 2/21 (pool 21, min p 0.048); lunaA_vs_mixed(mismatched) 2/21 (pool 12, min p 0.077); mixed_vs_lunaA(mismatched) 0/12 (pool 21, min p 0.045); mixed_LOO(matched) 1/12 (pool 12, min p 0.083); longA_vs_lunaA(matched,other batch) 1/8 (pool 21, min p 0.045)

## market mean markup over Nash

- llm_v1 A (luna): {"n": 21, "mean": 0.023, "ci": [-0.348, 0.398]}
- llm_v1 C (luna): {"n": 16, "mean": 1.778, "ci": [1.412, 2.213]}
- llm_mixed2 A (sol+luna): {"n": 12, "mean": 0.45, "ci": [0.269, 0.621]}
- llm_long A (luna, T=20 prefix): {"n": 8, "mean": 0.37, "ci": [-0.131, 0.921]}
