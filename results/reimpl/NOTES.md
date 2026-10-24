# Independent reimplementation

Only this directory's brief and data were consulted. No external implementation
was read. Run from this directory with:

```
/home/factory/collusion/collusion-14-infotheory/.venv/bin/python reimpl.py
```

Interpretation choices where the excerpt leaves details unspecified:

- **Scope and time windows:** Implement the four statistics explicitly requested
  in “What to compute.” `llm_long` denotes all 50 rounds;
  `llm_long_first20` denotes rounds 0–19 of the same runs. Prices are aligned by
  seller ID and round; assigned pairs are unused. Every statistic uses all six
  unordered pairs, and its run score is the maximum pair score.
- **pCMI regression:** Treat the public state as the joint categorical value
  `(demand_shock, cost)`, allowing an interaction. Regress each current price on
  an intercept, joint-state dummies (one reference level omitted), and the four
  sellers' prices one round earlier. Drop the first round; use ordinary least
  squares with an SVD projection, including when the design is rank deficient.
  State is contemporaneous; no additional lagged state or time trend is used.
- **pCMI numerics:** Use centered Pearson correlation of the two residual
  series, and natural logarithms. A zero-variance residual yields pair score 0.
  Residual norms at most `1e-10 * max(1, target norm)` are treated as exact fits;
  centered residual norms at most `1e-12` are treated as zero. Cap squared
  correlation at `1 - 1e-12` to produce finite JSON scores for perfect fits.
- **Miller–Madow MI:** Integer prices are discrete categories without binning.
  Compute corrected marginal entropies minus corrected joint entropy, with
  correction `(K - 1)/(2*n)` for the number of *observed* categories in each
  entropy. Thus `MI_MM = MI_plugin + (Kx + Ky - Kxy - 1)/(2*n)`, in nats.
  Do not substitute the full Cartesian support for observed joint support, or
  truncate a negative corrected estimate to zero.
- **Level scores:** Average prices over both pair members and all selected
  rounds. Subtract each round's Nash price (10 for cost 6, 12 for cost 8) for
  `market_level`. For `pair_level`, subtract the other two sellers' mean price;
  retain its sign before taking the maximum over pairs. No absolute value or
  assigned-pair selection is applied.
- **Shift construction:** Shift the already fitted pCMI residual sequences,
  whose length is 19 for a 20-round run. Offsets range from 0 through length−1;
  enforce circular distance at least 3 for every pair of sellers, including
  across the wrap boundary. A zero offset for an individual seller is allowed.
  Sample uniformly with replacement from admissible four-offset tuples.
  Enumerating relative configurations with A at zero and then adding a uniform
  common offset implements that sampling exactly. Count distinct *relative*
  configurations for the minimum-of-20 rule, so common rotations do not inflate
  the number of valid shifts. There are 720 such configurations at length 19;
  the fallback does not affect any requested run.
- **Null re-residualization:** Independently roll each seller's fitted residual
  vector, then regress all four shifted residuals on the *original, fixed*
  state-and-lagged-price design. Do not shift raw prices, refit the lagged-price
  design, or shift within state strata for this pCMI null. Each draw's null
  statistic is the maximum of its six pair scores, compared with the observed
  maximum. The state-stratified shifts mentioned for discrete CMI are not used
  because that statistic is not requested.
- **Monte Carlo convention:** Use 200 draws per run, NumPy `default_rng(0)`,
  processing run IDs in sorted order. Compute the inclusive upper-tail p-value
  as `(1 + exceedances)/(200 + 1)`; count null scores within `1e-12` below the
  observed score as ties. Flag only `p < 0.05`, not `p <= 0.05`.
- **AUROC:** Positive labels are C/D pooled against A/B, C against A, or D
  against B; higher scores indicate the positive class. Give each run equal
  weight and ties half credit. Use all available runs in the relevant families,
  with no assigned-pair filtering. Report the requested AUROCs and flag rates;
  no bootstrap interval or additional detector is requested in the output list.

`results.json` stores run maxima at `dataset -> statistic -> run_id`, with
`pCMI_pvalue` alongside the llm_v1 scores. `pair_scores` stores all six scores
for every run and statistic. `aurocs`, `flag_rates`, and null diagnostics are
separate top-level keys. All JSON numbers are finite.
