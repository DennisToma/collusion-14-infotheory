# E54 matched reference pool (T=20)

n: {"llm_v1_A": 21, "llm_v1_C": 16, "llm_long_p2_A": 20, "llm_p2_v0_A": 6, "llm_p2_para_A": 6, "llm_p2_template_A": 6, "llm_p2_order_A": 6, "llm_p2_noreason_A": 6, "pool_fresh_all": 50, "pool_fresh_v0": 26, "pool_mixed": 12}

| detector @ alpha | v1A|fresh_all | v1C|fresh_all | v1A|fresh_v0 | v1C|fresh_v0 | v1A|mixed | v1C|mixed | fresh_all|v1A | fresh_all|fresh_all_LOO |
|---|---|---|---|---|---|---|---|---|
| pair_markup@0.05 | 0/21 [0, 16] (pool 50) | 1/16 [1, 28] (pool 50) | 2/21 [3, 29] (pool 26) | 13/16 [57, 93] (pool 26) | 0/21 [0, 16] (pool 12) | 0/16 [0, 19] (pool 12) | 10/50 [11, 33] (pool 21) | 2/50 [1, 14] (pool 50) |
| pair_markup@0.1 | 0/21 [0, 16] (pool 50) | 3/16 [7, 43] (pool 50) | 2/21 [3, 29] (pool 26) | 13/16 [57, 93] (pool 26) | 4/21 [8, 40] (pool 12) | 15/16 [72, 99] (pool 12) | 12/50 [14, 37] (pool 21) | 5/50 [4, 21] (pool 50) |
| pair_level@0.05 | 0/21 [0, 16] (pool 50) | 4/16 [10, 50] (pool 50) | 0/21 [0, 16] (pool 26) | 3/16 [7, 43] (pool 26) | 0/21 [0, 16] (pool 12) | 0/16 [0, 19] (pool 12) | 10/50 [11, 33] (pool 21) | 2/50 [1, 14] (pool 50) |
| pair_level@0.1 | 0/21 [0, 16] (pool 50) | 7/16 [23, 67] (pool 50) | 0/21 [0, 16] (pool 26) | 6/16 [18, 61] (pool 26) | 0/21 [0, 16] (pool 12) | 7/16 [23, 67] (pool 12) | 13/50 [16, 40] (pool 21) | 5/50 [4, 21] (pool 50) |
| pcmi@0.05 | 2/21 [3, 29] (pool 50) | 1/16 [1, 28] (pool 50) | 2/21 [3, 29] (pool 26) | 1/16 [1, 28] (pool 26) | 0/21 [0, 16] (pool 12) | 0/16 [0, 19] (pool 12) | 0/50 [0, 7] (pool 21) | 2/50 [1, 14] (pool 50) |
| pcmi@0.1 | 3/21 [5, 35] (pool 50) | 1/16 [1, 28] (pool 50) | 2/21 [3, 29] (pool 26) | 1/16 [1, 28] (pool 26) | 11/21 [32, 72] (pool 12) | 8/16 [28, 72] (pool 12) | 1/50 [0, 10] (pool 21) | 5/50 [4, 21] (pool 50) |
| mi@0.05 | 1/21 [1, 23] (pool 50) | 1/16 [1, 28] (pool 50) | 1/21 [1, 23] (pool 26) | 1/16 [1, 28] (pool 26) | 0/21 [0, 16] (pool 12) | 0/16 [0, 19] (pool 12) | 1/50 [0, 10] (pool 21) | 2/50 [1, 14] (pool 50) |
| mi@0.1 | 1/21 [1, 23] (pool 50) | 1/16 [1, 28] (pool 50) | 1/21 [1, 23] (pool 26) | 1/16 [1, 28] (pool 26) | 2/21 [3, 29] (pool 12) | 1/16 [1, 28] (pool 12) | 7/50 [7, 26] (pool 21) | 5/50 [4, 21] (pool 50) |

rule (alpha .05, v1A vs fresh_all): {"pair_markup": {"fpr": 0.0, "wilson": [0.0, 0.155], "pool_n": 50, "restores": true}, "pair_level": {"fpr": 0.0, "wilson": [0.0, 0.155], "pool_n": 50, "restores": true}, "pcmi": {"fpr": 0.095, "wilson": [0.027, 0.289], "pool_n": 50, "restores": true}, "mi": {"fpr": 0.048, "wilson": [0.008, 0.227], "pool_n": 50, "restores": true}}

market mean markup over Nash:
- llm_v1 A: {"n": 21, "mean": 0.023, "ci": [-0.348, 0.398]}
- llm_v1 C: {"n": 16, "mean": 1.778, "ci": [1.415, 2.228]}
- mixed2 A: {"n": 12, "mean": 0.45, "ci": [0.268, 0.618]}
- fresh_all A: {"n": 50, "mean": 0.73, "ci": [0.412, 1.046]}
- fresh_v0 A: {"n": 26, "mean": 0.23, "ci": [-0.063, 0.502]}
- llm_p2_v0 A: {"n": 6, "mean": 0.258, "ci": [-0.356, 0.869]}
- llm_p2_para A: {"n": 6, "mean": 0.748, "ci": [0.6, 0.858]}
- llm_p2_template A: {"n": 6, "mean": 2.56, "ci": [2.075, 3.052]}
- llm_p2_order A: {"n": 6, "mean": -0.19, "ci": [-0.825, 0.581]}
- llm_p2_noreason A: {"n": 6, "mean": 1.969, "ci": [1.25, 2.517]}
- llm_long_p2 A (T20): {"n": 20, "mean": 0.221, "ci": [-0.106, 0.526]}
