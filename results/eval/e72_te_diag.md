E72 TE diagnostic (exploratory; 192 E70 games, 96 channel; exploratory/post hoc; zero LLM calls; frozen TE estimator; reproduces E70 TE run scores (max abs dev 0.0e+00))
(a) TE names the assigned pair in 30/96 = 0.31 [0.229, 0.411] channel games (chance 1/6 = 0.17; binom p = 0.000315); mean rank of assigned pair 2.91 (chance 3.5); ranks {1: 30, 2: 13, 3: 18, 4: 15, 5: 11, 6: 9}; executed 8/44, not executed 22/52; context: highest-priced pair names it 57/96 [0.494, 0.687]; TE top = highest-priced pair in 24/96
(b) windows_1_10_vs_11_20: early 0.46 [0.389, 0.543], late 0.49 [0.415, 0.575], late − early +0.03 [-0.074, 0.135] (full 0.62)
(b) full_fit_residuals_split: early 0.57 [0.488, 0.649], late 0.54 [0.458, 0.612], late − early -0.03 [-0.141, 0.076] (full 0.62)
(c) executed C (n=44) vs A: 0.49 [0.381, 0.6]; not_executed C (n=52) vs A: 0.73 [0.638, 0.804] (not executed: 38 judge agreement, 14 none)
branches: {'a_ci_includes_chance': False, 'b_early_only': False, 'late_ci_above_half': False, 'stronger': False}
