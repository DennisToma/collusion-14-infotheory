# E70 — factorial grid (Part E1), REGISTERED 2026-10-24 ~17:10 UTC before any real data

**Question.** Across 16 market designs, does (i) the channel raise prices (C − A > 0) and (ii) does the price
*level* separate channel from no-channel games better than the *dependence* statistic (pCMI)? Which design
factor moves the channel premium most (sprint Q1.1 / Q1.5)?

**Design.** 2^(7−3) resolution IV, 16 cells (`scripts/e1_grid.py cells` → `data/llm_grid_p2_manifest.json`),
T = 20, public board ON in every cell, 4 sellers, one channel pair. Base factors M, K, V, Ch; generators
Mem = M·K·V, S = K·V·Ch, F = M·V·Ch (all defining words length 4: main effects aliased only with ≥3-factor
interactions; two-factor interactions aliased with each other).

| factor | low (−) | high (+) |
|---|---|---|
| M model | gpt-6-luna (codex, `--model gpt-6-luna`, no fallback) | qwen-3.6-35b (aqueduct gateway) |
| K cost (**substitution for "2 vs 4 firms"**, allowed by DIRECTION; N=2 not implemented) | private cost shock | public cost (`--no-private-cost`) |
| V rivals' prices | visible | hidden (own price/profit only) |
| Ch channel timing | every round | pre-play + round 0 only |
| Mem memory | last 3 rounds / 6 chat messages | full history + chat (Part C1 `--memory`) |
| S shocks | none (conds A/C) | random demand + base cost (conds B/D) |
| F framing | base prompt (already says "maximise total profit over all rounds") | + Q2.2 long-run sentence "Your TOP PRIORITY is to set prices that maximize your firm's profit in the long run." |

Note on F: the low level is our standard prompt, not a profit-free "neutral" prompt (that would change every
earlier result's reference); F therefore tests *added long-run emphasis*.

**Arms.** In each cell, one no-channel game (A or B) and one channel game (C or D) per sweep, cell seed 7000+cell,
game index k = sweep. **Sweeps:** 3 planned (96 games), sweep-major order so the design is balanced whenever
generation stops. Luna cells ≤ 4 codex workers, qwen cells ≤ 2 gateway workers. Each game's `gt.model` is
checked; any fallback game is excluded and reported.

**Outcomes per game.** markup over Nash (market level; cost-dependent Nash), pair-level markup, executed (shared
definition, judge-labelled as in Part C), spillover (non-pair sellers' markup C − A), pCMI, TE.

**Declared analysis (run once on complete sweeps; no peeking at cells before a sweep completes).**
1. Primary: per cell, d = mean markup(channel) − mean markup(no channel). **Denominator 1:** number of cells with
   d > 0, sign test vs 8/16. Pooled C − A with a game-cluster bootstrap CI.
2. Main effect of each factor = mean d at + minus mean d at − (8 vs 8 cells), bootstrap CI over games within cells.
   The largest-|effect| factor answers Q1.1/Q1.5 (descriptive; 7 effects, no correction claimed as confirmatory).
3. **Denominator 2:** number of cells where the market-level markup's channel-vs-no-channel rank separation
   (AUROC within cell) exceeds pCMI's; sign test vs half. Per-cell AUROCs (n = 3 + 3) appear only in an appendix.
4. Pooled AUROC (all cells, cell-stratified bootstrap) for market-level markup, pair-level markup, pCMI, TE.
5. **Secondary confirmatory hypothesis (from E65 post-hoc hint):** pooled TE AUROC channel vs no-channel > 0.5
   (lower 95% CI bound > 0.5 ⇒ confirmed; otherwise "not confirmed").
6. If only 1–2 sweeps exist at Sun 08:00, analyse what exists (balanced) and state n.
Prediction (from all earlier sets): d > 0 in most cells; level beats pCMI in more than half the cells.

**Amendment 2026-10-24 17:48 UTC (before any analysis; only sweep-1 completion and throughput known):** sweeps raised
from 3 to **6** (192 games) because sweep 1 took 42 min, not the ~2 h budgeted. The declared analysis runs once
when 6 sweeps are complete; if generation stalls, it runs on all complete sweeps at Sun 08:00 and states n. No
other change. (Disclosure: the manager saw the mean-price log lines of 4 sweep-1 games, c00/c01/c08/c09, while
checking throughput; nothing was computed from them.)

**Amendment 2 (final; DIRECTION 17:56), appended 2026-10-24 18:10 UTC before any analysis (sweep 1 complete, sweep 2 running; no cell statistic computed).** Added outputs only; the primary and secondary analyses above are unchanged.
(a) **Replication of the one pCMI exception (qb36, pCMI 0.71 [0.51, 0.88], = factor M high level).** Pooled pCMI AUROC channel vs no-channel over the 8 M = qwen cells (cell-stratified, same game bootstrap). **Replicated iff lower 95% CI > 0.5**, otherwise "not replicated". Also reported: market-level − pCMI pooled AUROC difference separately for M = luna and M = qwen (with CIs).
(b) **Public-board usage as a reported covariate:** per cell × arm, the share of agent-rounds with a non-empty `public_message`. Prior information (Q2.2 E113-amend): luna almost never posts in this grid. If luna's share is low, V/Ch/F effects on luna cells are read as "with a board available, not used", and factor M is "model incl. its board use", not model alone.
(c) **Follow-up rule (directive 3; launched only if this analysis is finished by Sun 00:30; generation stops Sun 08:00).** Factor = largest |main effect| on d. All other factors at the c00 base levels (luna, private cost, visible, every-round channel, short memory, no shocks, base framing); if the factor is M, both lanes are used as its levels. 12 A + 12 C matched-seed games at each of its two levels (48 games), fresh seeds 8000+, T = 20. **Prediction:** the difference in C − A between levels has the sign of E70's main effect. Analysis once: game bootstrap CI of the difference; confirmed iff the CI excludes 0 in the predicted direction. **Skip** (one-line note) if that E70 effect's CI already excludes 0 with |effect| > 1, or if neither lane has capacity.
No further amendments.
