No P0 found. E32’s reported numbers match the JSON; recomputing scores and statistics reproduced it exactly. All 15 seed/pair/state-path matches check out.

- **P1 — Invalid binomial inference for ties** ([script:88](/home/factory/collusion/collusion-14-infotheory/scripts/placebo_rep_ext.py:88)). Expected hits are fractional, but `round(h.sum())` feeds an integer binomial test: 13.5 becomes 14; 2.5 becomes 2. **Fix:** retain fractional estimates and compute a pair-label randomization null for that statistic; remove rounded-count p-values.

- **P1 — AUROC intervals ignore matching** ([script:102](/home/factory/collusion/collusion-14-infotheory/scripts/placebo_rep_ext.py:102)). `auroc_ci` independently resamples private/placebo arms despite shared seeds. **Fix:** bootstrap matched seed pairs jointly. My paired recalculation still leaves every interval covering 0.5.

- **P1 — Non-detection becomes equivalence/causal attribution.** §4.3.9 says levels are “just as high” and detect the offer, “not delivered coordination”; §4.4/§5 repeat “no difference.” The matched level-localization interval permits −17 to +23 percentage points. **Fix:** say “no statistically detected difference”; retain this uncertainty alongside the abstract’s similar observed counts. Establish equivalence before excluding delivery effects.

- **P2 — Global state leaks** ([script:34](/home/factory/collusion/collusion-14-infotheory/scripts/placebo_rep_ext.py:34)). `_design` is correctly restored; `ext.SRC` and `ext._Z["lev"]` are not. Later evaluations can read the placebo dataset. **Fix:** restore both in `finally`, or pass configuration explicitly.

- **P2 — Significance framing.** MI-difference sign-flip p=0.06543 is correct, conditional on within-pair exchangeability. Its positive bootstrap interval is not confirmatory; eight-test Bonferroni gives p≈0.523. Placebo Pearson-difference p=0.027 is also unadjusted. **Fix:** specify assumptions, test family and adjustment.

- **P2 — §7 scaling/power.** Enumerating `2^n` flips is infeasible at 50 seeds. **Fix:** use dynamic programming or Monte Carlo; power the proposed sample size.

- **P2 — E32 audit trail.** TSV remains `declared/pending`, specifies 200 sampled tie-breaks, and omits sign-flip testing. **Fix:** append completion, results and analysis deviations.
