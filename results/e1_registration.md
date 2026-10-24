# E1 — factorial grid (Part E1), REGISTERED 2026-10-24 ~17:10 UTC before any real data

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
