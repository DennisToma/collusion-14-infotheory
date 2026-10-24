# DIRECTION — Phase 2, director review 2026-10-24 07:40 UTC (Sat)

**Verdict.**
1. On track, and the most productive of the two repos: gaps 3, 5, 6, 7, 8 and both shared gaps are done on locked splits with CIs. The "levels vs co-movement fail in opposite places" synthesis (cost asymmetry ↔ LLM result) is the strongest Phase 2 result so far.
2. The research question still depends on two LLM results that are generating: gap 2 (long games, the decisive Q1.4 result) and gap 4 (second family; at risk, 2/30 games). Gap 1 at n=6 per arm can only give a sign-consistency band, not a precise one.
3. Main risk is not method but framing: a null pCMI on long games will only be convincing if it comes with a power bound. Scripted work has hit diminishing returns (scripted collusion is co-movement by construction), so stop adding scripted variants.

## Top directives (in priority order)

1. **Gap 2: make the long-game result decisive either way (needed by Sat 20:00 if E44 T=60 lands, ~13:00).** Run the declared prefix power-vs-T analysis. ALSO re-run the E30 injection-MDE (`scripts/injection_mde.py`) on the *new* llm_long_p2 A controls at T=20/40/60(/80). Then the report can say "pCMI would detect a planted co-movement of size q with power X at T=60; real channel pairs show excess Y [CI]". Without that bound, a null pCMI is just "underpowered again". Also plot per-round pair premium over rounds 1–60 for C games. The sibling (Q2.2 E84) found that 36/50 agreements are abandoned within a few rounds, so check whether collusion persists in long games at all. If it decays, longer T cannot help pCMI, and that is a finding in itself. Declare the MDE and decay analyses in the ledger before looking at E44 detector output.
2. **Gap 1: analyse as a robustness band, not 5 separate tests.** When the 5 arms are done (~09:00), report per-variant C − A markup and AUROCs (markup, pair_level, pCMI) with CIs. The headline is the pooled estimate plus a variant × condition heterogeneity test, and whether the sign/ordering (level > pCMI) holds in 5/5 arms. With 6 vs 6 games per arm, do NOT claim per-variant AUROC differences. → REPORT P2.6.
3. **Gap 4: protect the deepseek run and report what completes.** Go is shared with the sibling's glm run and with another service. Keep `llm_queue_go.sh` running until Sun 12:00, not just Sat 20:00. At the checkpoint, report the markup C − A with CI at whatever n exists (state n; no AUROC claims under 8 + 8). Check the first deepseek games for degenerate behaviour now (constant prices, parse failures). If deepseek sellers never vary prices, say so early: pCMI is undefined there, and that is reportable.
4. **Close the open hole in gap 3 with data you are already generating (cheap, no new calls).** P2.3(c) says "we cannot say how well a matched reference restores calibration out of sample". The 20 llm_long_p2 A games (first-20-round prefixes) and the E43 A arms are *fresh, independent* luna no-channel markets. Use them as a model-matched reference pool for llm_v1 A/C. That gives an out-of-sample FPR for matched-reference markup/pCMI at α=0.05 (pool ≥ 20). Declare first. This turns the weakest P2.3 paragraph into a confirmatory result.
5. **Checkpoint hygiene (by Sat 19:30).** Rewrite the short abstract so it states Phase 2 findings, not only v1. Keep the "Phase 2 takeaways" block as the merger's entry point: one row per gap with number, CI and source JSON, the way the v1 key-findings table does it. Make the P2 tables regenerable by `scripts/tables.py --check`, or by a single `scripts/p2_tables.py --check`. Fix the `scripts/test_release_audit.py` import failure (`report_tables` path) before Sun 16:30 so the reproducibility claim stays true.

Then (by Sun 15:00): gap 9 as a *scripted* market-split / bid-rotation condition only (≤ 2 h, codex). Then frozen detectors on the sibling's `llm_p2cue` (6 matched arms incl. notes-to-self and random partner) once they publish labels: one table, no new calls, the same pattern as E32/E35. Then codex adversarial review of P2.3–P2.8 text.

## STOP doing
- No more scripted sweeps or extra scripted conditions beyond gap 9. Scripted collusion is a shared signal (co-movement by design), so more scripted rows add nothing to the LLM question.
- No release-audit / PDF-export / deck polishing each iteration. Exports only at the Sat 19:30 checkpoint and in the Sun 16:30 finalize window.
- No more unadjusted exploratory sub-comparisons in P2.3 (sol–sol 0.72, α=0.10 post-hoc rows). Label what exists as exploratory and do not grow it. P2.3 is already the longest P2 section; cut it to ~60% before the checkpoint.
- Don't start the starter double-auction adaptation for gap 9 (needs llm.py adaptation and API rework; too costly for an exploration item).
- Don't let codex reviewers rewrite numbers. Reviews give wording fixes; numbers come from scripts.

## Cross-pollination
- **From Q2.2 → here:** (a) E84 behaviour labels (agreement *followed* vs *abandoned*, `p2_behaviour.py`). Apply the same split to your C games (llm_v1, llm_long, llm_long_p2) and check whether markup/pCMI differ between followed and abandoned pairs. It matters for directive 1. (b) Their round-1 / opening-burst finding is consistent with your E39 first-sender result; cite each other in the same terms. (c) `llm_p2cue` arms (see "Then").
- **From here → Q2.2:** (a) the deepseek `thinking: disabled` fix in `llm.py` (their deepseek attempt failed on hidden reasoning; they switched to slow glm). Directed to port it. (b) P2.4 private cost asymmetry: level screens 30/30 false, pCMI ~ control. This is the private-cost complement to their gap 7, which uses *public* costs plus a cost-adjusted markup. (c) The CUSUM onset screen as an online version of their premium.
- For the merger: both repos report precision@5%. Yours uses Jeffreys intervals, theirs class-stratified bootstrap. State the method in the table caption so the merged report doesn't compare them as if they were the same.

---

# Phase 2 gap list (set by Dennis, 2026-10-24 06:40 UTC) — overrides earlier "no new experiments"

v1 (overnight result) is frozen as git tag `v1-overnight`. Phase 2 = close every known gap. Research is
OPEN again: new experiments are wanted. Keep v1 numbers reproducible; new results go in new sections
/ new datasets (`*_p2`), registered in EXPERIMENTS.tsv before running, decided on dev, confirmed once on a
fresh locked split recorded in data/SPLITS.md.

**Timeline (UTC):** presentable checkpoint (REPORT.md updated with whatever is done) by **Sat 20:00**;
all experiments done by **Sun 15:00**; finalize-only from **Sun 16:30**; hard stop **Sun 18:00**.
Submission is Sun 23:59 AoE — Dennis submits Sunday evening from the merged repo
(`collusion-beyond-words`, built by a third manager from Sun 08:00 using BOTH repos' REPORTs).
Keep REPORT.md always presentable; put a "Phase 2 results" section near the top once results land.

**Ownership:** each gap below is owned by ONE repo (no duplicate work). The sibling may read your data.

**Budget / models:** GPT-family sellers via `llm.chat(tier="cheap")` (gpt-6-luna). For the **second seller
family** use OpenCode Go: `llm.chat(..., backend="go", model="deepseek-v4.1-flash")` (or glm-5.3-flash /
kimi-k3) — Go is serialised and shared with another service; if it 429s, llm.py cools down 30 min;
then continue with what you have. Claude Sonnet as a seller only on a small subset (≤ 10 runs) — the
Claude quota runs the managers. gpt-6.1-sol as a seller for a third family check is fine (codex quota).

**Gaps owned by BOTH repos (do in your own market):**
- **Precision at realistic prevalence** (15 min): for every headline detector, report precision / FPR-
  normalised alarm rates at 1%, 5%, 20% collusion prevalence at the frozen thresholds, with CIs.
  → **DONE** (E46, REPORT P2.1). Add rows for P2 detectors (CUSUM, matched-reference) only if cheap.
- **Independent reimplementation check:** have codex (gpt-6.1-sol, `-s workspace-write` in a scratch dir,
  given ONLY the REPORT's method description, not your code) reimplement your headline statistic(s); compare
  numbers on the same data. Report agreement; fix any bug found (and re-state affected numbers).
  → **DONE** (E47, REPORT P2.2: 234/236 cells < 1e-9, all 20 AUROCs identical, no bug).

## Gaps owned by THIS repo (Q1.4), in priority order (status as of 07:40 UTC; re-prioritised order in brackets)
1. **Prompt-wording robustness** (validity threat; you already saw the JSON-anchor effect). 3–5 prompt
   variants of your seller prompt (paraphrased instructions, different JSON template / no example,
   different order of information, reasoning on/off). Does the C − A markup and the level-vs-pCMI pattern
   hold across variants? Report variance across variants as a robustness band.
   → **IN PROGRESS** [priority 2]. E43 v0 12/12, para 12/12, template 5/12, order + noreason queued; ETA ~09:00. Analyse pooled + heterogeneity (directive 2).
2. **Long LLM games**: settle whether pCMI fails for lack of data. ≥ 20 runs per condition (A, C, plus D if
   budget) at T = 60–100. Power-vs-T curve on LLM data (subsample prefixes). This is the decisive 1.4 result.
   → **IN PROGRESS (queued behind E43)** [priority 1]. E44 A/C × 20 at T=60, ETA ~13:00; T=80 replay ~14:30. Add injection-MDE bound + premium-decay analysis (directive 1). D dropped: budget, and B/D added nothing in v1.
3. **Same-model confound as a headline**: in real deployments everyone runs the same few models. Quantify
   on LLM data: same-model no-channel pairs vs mixed-model pairs vs colluding pairs. Test mitigations
   (same-model surrogate null; conditioning on lagged prices of all firms; model-matched reference
   markets). State plainly what a deployer can and cannot conclude.
   → **DONE, one hole** [priority 4]. E48, REPORT P2.3. Out-of-sample matched-reference calibration is untested. Close it with the fresh luna A games (directive 4); then trim P2.3.
4. **Second seller family** in your market: deepseek (Go) sellers, ≥ 15 runs each for A and C (T=20 or
   longer). Does the channel markup and the detector pattern replicate across families?
   → **IN PROGRESS, AT RISK** [priority 3]. E45 2/30 at 07:27 (Go 429 cooldowns); keep running to Sun 12:00, report at whatever n (directive 3).
5. **Coalition structure**: 3-of-4 colluding and all-4 colluding (scripted + small LLM set). Pairwise
   net-influence relies on clean comparison pairs — show where it breaks and test a group-level statistic
   (e.g. multi-information / total correlation of the coalition vs surrogates).
   → **DONE (scripted)** (E49, P2.4: relative level AUROC 0.25 for all-4 cartel; TC adds nothing over pCMI). Small LLM set **DROPPED**: an LLM 4-way cartel needs a new channel design and the scripted result already makes the point.
6. **Collusion onset / detection delay**: collusion that starts at round k (scripted switch; LLM channel
   opened mid-game). Rounds-to-detection for level screen vs pCMI (CUSUM-style sequential version of the
   level screen is a good addition).
   → **DONE (scripted)** (E50, P2.4: CUSUM 0/30 FPR, delay ~7 rounds; repeated-look pCMI 17% FPR). LLM mid-game channel **DROPPED** (codex budget goes to gap 2).
7. **Market-model robustness**: N = 2 and 6 sellers, and a different demand elasticity; do the scripted
   calibration (FPR) and power results hold?
   → **DONE** (E52, P2.5: pooled pCMI FPR 6.0% [3.8, 9.3], 9/10 cells pass; inelastic demand hurts level screens).
8. **Cost asymmetry hard negative** for the dependence detectors (firms with unequal private costs).
   → **DONE** (E51, P2.4: level screens 30/30 false, pCMI 4/30). Strongest Phase 2 result; keep it in the abstract.
9. **Non-price collusion (exploration)**: one condition of market/customer splitting or bid rotation —
   simplest: run the starter double auction (`~/collusion/collusion_hackathon/llm-agent-collusion`, via our
   llm.py — it needs adaptation since it expects a Nebius/OpenRouter key) or a quantity/territory variant
   of your sim; check which detectors see it at all.
   → **NOT STARTED** [priority 5]. Scripted bid-rotation / market-split variant only, ≤ 2 h, after directives 1–4. Starter double auction **DROPPED** (adaptation cost).
Items 1–4 must be done by Sat 20:00 if at all possible; 5–9 by Sun 15:00.
