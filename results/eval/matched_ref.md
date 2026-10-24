# E54 matched reference pool (INTERIM) (T=20)

n: {"llm_v1_A": 21, "llm_v1_C": 16, "llm_long_p2_A": 0, "llm_p2_v0_A": 6, "llm_p2_para_A": 6, "llm_p2_template_A": 6, "llm_p2_order_A": 3, "llm_p2_noreason_A": 0, "pool_fresh_all": 21, "pool_fresh_v0": 6, "pool_mixed": 12}

| detector @ alpha | v1A|fresh_all | v1C|fresh_all | v1A|fresh_v0 | v1C|fresh_v0 | v1A|mixed | v1C|mixed | fresh_all|v1A | fresh_all|fresh_all_LOO |
|---|---|---|---|---|---|---|---|---|
| pair_markup@0.05 | 0/21 [0, 16] (pool 21) | 1/16 [1, 28] (pool 21) | 0/21 [0, 16] (pool 6) | 0/16 [0, 19] (pool 6) | 0/21 [0, 16] (pool 12) | 0/16 [0, 19] (pool 12) | 5/21 [11, 45] (pool 21) | 1/21 [1, 23] (pool 21) |
| pair_markup@0.1 | 0/21 [0, 16] (pool 21) | 1/16 [1, 28] (pool 21) | 0/21 [0, 16] (pool 6) | 0/16 [0, 19] (pool 6) | 4/21 [8, 40] (pool 12) | 15/16 [72, 99] (pool 12) | 7/21 [17, 55] (pool 21) | 2/21 [3, 29] (pool 21) |
| pair_level@0.05 | 0/21 [0, 16] (pool 21) | 4/16 [10, 50] (pool 21) | 0/21 [0, 16] (pool 6) | 0/16 [0, 19] (pool 6) | 0/21 [0, 16] (pool 12) | 0/16 [0, 19] (pool 12) | 3/21 [5, 35] (pool 21) | 1/21 [1, 23] (pool 21) |
| pair_level@0.1 | 0/21 [0, 16] (pool 21) | 6/16 [18, 61] (pool 21) | 0/21 [0, 16] (pool 6) | 0/16 [0, 19] (pool 6) | 0/21 [0, 16] (pool 12) | 7/16 [23, 67] (pool 12) | 4/21 [8, 40] (pool 21) | 2/21 [3, 29] (pool 21) |
| pcmi@0.05 | 0/21 [0, 16] (pool 21) | 0/16 [0, 19] (pool 21) | 0/21 [0, 16] (pool 6) | 0/16 [0, 19] (pool 6) | 0/21 [0, 16] (pool 12) | 0/16 [0, 19] (pool 12) | 0/21 [0, 16] (pool 21) | 1/21 [1, 23] (pool 21) |
| pcmi@0.1 | 2/21 [3, 29] (pool 21) | 1/16 [1, 28] (pool 21) | 0/21 [0, 16] (pool 6) | 0/16 [0, 19] (pool 6) | 11/21 [32, 72] (pool 12) | 8/16 [28, 72] (pool 12) | 1/21 [1, 23] (pool 21) | 2/21 [3, 29] (pool 21) |
| mi@0.05 | 0/21 [0, 16] (pool 21) | 0/16 [0, 19] (pool 21) | 0/21 [0, 16] (pool 6) | 0/16 [0, 19] (pool 6) | 0/21 [0, 16] (pool 12) | 0/16 [0, 19] (pool 12) | 1/21 [1, 23] (pool 21) | 1/21 [1, 23] (pool 21) |
| mi@0.1 | 1/21 [1, 23] (pool 21) | 1/16 [1, 28] (pool 21) | 0/21 [0, 16] (pool 6) | 0/16 [0, 19] (pool 6) | 2/21 [3, 29] (pool 12) | 1/16 [1, 28] (pool 12) | 3/21 [5, 35] (pool 21) | 2/21 [3, 29] (pool 21) |

rule (alpha .05, v1A vs fresh_all): {"pair_markup": {"fpr": 0.0, "wilson": [0.0, 0.155], "pool_n": 21, "restores": true}, "pair_level": {"fpr": 0.0, "wilson": [0.0, 0.155], "pool_n": 21, "restores": true}, "pcmi": {"fpr": 0.0, "wilson": [0.0, 0.155], "pool_n": 21, "restores": true}, "mi": {"fpr": 0.0, "wilson": [0.0, 0.155], "pool_n": 21, "restores": true}}

market mean markup over Nash:
- llm_v1 A: {"n": 21, "mean": 0.023, "ci": [-0.348, 0.398]}
- llm_v1 C: {"n": 16, "mean": 1.778, "ci": [1.415, 2.228]}
- mixed2 A: {"n": 12, "mean": 0.45, "ci": [0.268, 0.618]}
- fresh_all A: {"n": 21, "mean": 1.09, "ci": [0.618, 1.585]}
- fresh_v0 A: {"n": 6, "mean": 0.258, "ci": [-0.356, 0.873]}
- llm_p2_v0 A: {"n": 6, "mean": 0.258, "ci": [-0.381, 0.873]}
- llm_p2_para A: {"n": 6, "mean": 0.748, "ci": [0.6, 0.858]}
- llm_p2_template A: {"n": 6, "mean": 2.56, "ci": [2.069, 3.052]}
- llm_p2_order A: {"n": 3, "mean": 0.5, "ci": [-0.275, 1.562]}
