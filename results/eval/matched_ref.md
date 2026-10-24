# E54 matched reference pool (INTERIM) (T=20)

n: {"llm_v1_A": 21, "llm_v1_C": 16, "llm_long_p2_A": 0, "llm_p2_v0_A": 6, "llm_p2_para_A": 6, "llm_p2_template_A": 6, "llm_p2_order_A": 6, "llm_p2_noreason_A": 0, "pool_fresh_all": 24, "pool_fresh_v0": 6, "pool_mixed": 12}

| detector @ alpha | v1A|fresh_all | v1C|fresh_all | v1A|fresh_v0 | v1C|fresh_v0 | v1A|mixed | v1C|mixed | fresh_all|v1A | fresh_all|fresh_all_LOO |
|---|---|---|---|---|---|---|---|---|
| pair_markup@0.05 | 0/21 [0, 16] (pool 24) | 1/16 [1, 28] (pool 24) | 0/21 [0, 16] (pool 6) | 0/16 [0, 19] (pool 6) | 0/21 [0, 16] (pool 12) | 0/16 [0, 19] (pool 12) | 5/24 [9, 40] (pool 21) | 1/24 [1, 20] (pool 24) |
| pair_markup@0.1 | 0/21 [0, 16] (pool 24) | 1/16 [1, 28] (pool 24) | 0/21 [0, 16] (pool 6) | 0/16 [0, 19] (pool 6) | 4/21 [8, 40] (pool 12) | 15/16 [72, 99] (pool 12) | 7/24 [15, 49] (pool 21) | 2/24 [2, 26] (pool 24) |
| pair_level@0.05 | 0/21 [0, 16] (pool 24) | 4/16 [10, 50] (pool 24) | 0/21 [0, 16] (pool 6) | 0/16 [0, 19] (pool 6) | 0/21 [0, 16] (pool 12) | 0/16 [0, 19] (pool 12) | 3/24 [4, 31] (pool 21) | 1/24 [1, 20] (pool 24) |
| pair_level@0.1 | 0/21 [0, 16] (pool 24) | 6/16 [18, 61] (pool 24) | 0/21 [0, 16] (pool 6) | 0/16 [0, 19] (pool 6) | 0/21 [0, 16] (pool 12) | 7/16 [23, 67] (pool 12) | 4/24 [7, 36] (pool 21) | 2/24 [2, 26] (pool 24) |
| pcmi@0.05 | 0/21 [0, 16] (pool 24) | 0/16 [0, 19] (pool 24) | 0/21 [0, 16] (pool 6) | 0/16 [0, 19] (pool 6) | 0/21 [0, 16] (pool 12) | 0/16 [0, 19] (pool 12) | 0/24 [0, 14] (pool 21) | 1/24 [1, 20] (pool 24) |
| pcmi@0.1 | 2/21 [3, 29] (pool 24) | 1/16 [1, 28] (pool 24) | 0/21 [0, 16] (pool 6) | 0/16 [0, 19] (pool 6) | 11/21 [32, 72] (pool 12) | 8/16 [28, 72] (pool 12) | 1/24 [1, 20] (pool 21) | 2/24 [2, 26] (pool 24) |
| mi@0.05 | 0/21 [0, 16] (pool 24) | 0/16 [0, 19] (pool 24) | 0/21 [0, 16] (pool 6) | 0/16 [0, 19] (pool 6) | 0/21 [0, 16] (pool 12) | 0/16 [0, 19] (pool 12) | 1/24 [1, 20] (pool 21) | 1/24 [1, 20] (pool 24) |
| mi@0.1 | 1/21 [1, 23] (pool 24) | 1/16 [1, 28] (pool 24) | 0/21 [0, 16] (pool 6) | 0/16 [0, 19] (pool 6) | 2/21 [3, 29] (pool 12) | 1/16 [1, 28] (pool 12) | 4/24 [7, 36] (pool 21) | 2/24 [2, 26] (pool 24) |

rule (alpha .05, v1A vs fresh_all): {"pair_markup": {"fpr": 0.0, "wilson": [0.0, 0.155], "pool_n": 24, "restores": true}, "pair_level": {"fpr": 0.0, "wilson": [0.0, 0.155], "pool_n": 24, "restores": true}, "pcmi": {"fpr": 0.0, "wilson": [0.0, 0.155], "pool_n": 24, "restores": true}, "mi": {"fpr": 0.0, "wilson": [0.0, 0.155], "pool_n": 24, "restores": true}}

market mean markup over Nash:
- llm_v1 A: {"n": 21, "mean": 0.023, "ci": [-0.348, 0.398]}
- llm_v1 C: {"n": 16, "mean": 1.778, "ci": [1.415, 2.228]}
- mixed2 A: {"n": 12, "mean": 0.45, "ci": [0.268, 0.618]}
- fresh_all A: {"n": 24, "mean": 0.844, "ci": [0.358, 1.345]}
- fresh_v0 A: {"n": 6, "mean": 0.258, "ci": [-0.381, 0.873]}
- llm_p2_v0 A: {"n": 6, "mean": 0.258, "ci": [-0.381, 0.873]}
- llm_p2_para A: {"n": 6, "mean": 0.748, "ci": [0.598, 0.858]}
- llm_p2_template A: {"n": 6, "mean": 2.56, "ci": [2.075, 3.075]}
- llm_p2_order A: {"n": 6, "mean": -0.19, "ci": [-0.825, 0.579]}
