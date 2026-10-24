# DIRECTION — Phase 2, director review 2026-10-24 09:35 UTC (Sat)


## TOP PRIORITY (added by Dennis 10:25 UTC) — part C: strong / executed collusion + older models
**Why:** our LLM "collusion" is mostly *agreement without execution* (Q2.2: only 14/95 test runs keep the
agreement; deepseek 3/15; Q1.4 kept agreements sit at floor ≈12, barely above Nash 10) plus a prompt-
induced level effect (notepad ≈ 2/3 of the channel premium). Detectors were therefore mostly tested on weak
collusion. A judge will ask: do they work on collusion that is actually *executed and sustained*? We need a
clear positive arm. This outranks the remaining gap/exploration items (except finishing runs in flight).

**C1 Strong-collusion arm** (both repos, in your own market; coordinate via the sibling's STATUS.md so
you don't build identical arms — Q1.4 focuses on T=60–100 long games and dependence detectors, Q2.2 on
auditors/text and kept-vs-not-kept). Levers, piloted cheaply first (≤ 10 runs) and combined if needed:
- persistent memory: the agreed terms + full price history (incl. partner's compliance) visible every round;
- Fish et al. (2024)-style profit-maximisation framing ("maximise long-run profit"), no instruction to collude;
- repeated private messaging every round (not only opening), so deviations can be discussed/punished;
- longer horizon (T ≥ 40) with an unknown end;
- stronger sellers (gpt-6.1-sol) for the pair.
Promote the lever set that yields *sustained execution* (agreement kept ≥ 50% of post-agreement rounds,
floor clearly above Nash). Then run a properly sized set (≥ 20 C + 20 matched A) and evaluate ALL headline
detectors/auditors on executed-collusion runs vs controls. Report the executed-collusion rate per lever
(how rare is sustained collusion?) — that rate is itself a headline number.
Never instruct agents to collude; only opportunity, memory and profit objective.

**C2 Older / weaker models as sellers** (model-generation lever: does collusion and its detectability
change across model generations?). Available and verified working 10:25 UTC:
- codex: `gpt-5.6-luna`, `gpt-5.6-sol` (previous generation) — `llm.chat(..., backend="codex", model="gpt-5.6-luna")`
- OpenCode Go: `glm-5.2`, `mimo-v2.5` (older open models) — `backend="go"`; Go is shared/slow, keep runs small.
NOT available: gpt-5, gpt-4o. **WARNING:** llm.py's codex backend silently falls back to gpt-6-luna when a
model name is unknown or limited — always check `r["model"]` and exclude/flag fallback runs.
Split: Q1.4 runs gpt-5.6-luna + glm-5.2; Q2.2 runs gpt-5.6-sol + mimo-v2.5. ~10–15 runs per model (A vs C
matched seeds), base prompt. Report per-generation: agreement rate, execution rate, markup, detector AUROCs.
Combine with C1 if a model executes collusion more readily (older models may comply/coordinate differently).


**Verdict.**
1. On track and still the stronger repo. Every owned gap except gap 2 is done on locked splits or confirmatory LLM data, with CIs, declared rules and a regenerable glance table (`p2_tables.py --check`). Gap 4 (deepseek) and gap 1 (wording) came back cleanly ("rule HOLDS", with an honest prompt-sensitivity caveat).
2. The Q1.4 answer now rests on one result: E44 (llm_long_p2, 10/40 games at 09:27, ETA ~12:20; T=80 replay ~13:30). The pipeline (`scripts/e44_post.sh`, declared E44 rule, MDE and decay) is ready. Early C games show whole-market elevation (rivals at the pair's price), so expect pair_level to weaken and the pilot's "premium decays, markup stays" pattern to repeat.
3. Main risks: framing and reader path, not method. The abstract and "main claim" sit *below* a ~250-line Phase 2 block, and they still describe v1. STATUS timestamps run ahead of the clock (STATUS says 09:50 at 09:31). Time left is best spent consolidating, plus one cheap cross-repo experiment.

## Top directives (in priority order)

1. **E44 → P2.8 as the decisive result, exactly per the declared rule (when 40 games land, ~12:20; do not peek earlier).** Run `bash scripts/e44_post.sh` on `llm_long_p2_T60` only. Report the declared verdict ("too short" / "level, not short" / inconclusive) verbatim, plus the MDE/planting bound and the per-round decay figure. **Add one declared descriptive line before you look**: a market-wide spillover measure for C games, i.e. rival markup over Nash in C minus A, by round block. The first C games show all four sellers at the pair's price. If that holds, connect it explicitly to P2.4 (relative screens fail against an all-firm cartel, AUROC 0.25) and to Q2.2's random-partner arm (whole market +2.85). The story is then "a private channel turns into a market-wide price level over time, which both pCMI and pair-relative screens miss and only an absolute, model- *and* prompt-matched markup sees". T=80 is secondary: one sentence and one row, not a new section. Replace the pilot rows; don't merge them.
2. **Fix the reader path before the Sat 19:30 checkpoint.** Order: title → updated one-sentence main claim → Abstract (v1 + Phase 2 combined, ≤ 250 words) → Phase 2 at-a-glance table + takeaways → v1 key findings → details. Move the long P2.1–P2.10 prose *below* the abstract (or to a "Phase 2 details" section after §4). The main claim must now say three things: (i) levels vs moves fail in opposite places (cost asymmetry vs LLM); (ii) the channel effect holds across 5 wordings and 2 families, but the no-channel *baseline* moves with prompt and model, so absolute screens need model+prompt-matched references; (iii) the E44 verdict. Keep takeaways ≤ 8 lines. The merger lifts this block verbatim on Sun 08:00.
3. **One cheap cross-repo experiment, the only new generation after E44 (declare first; Go only, start once Q2.2's `llm_p2ds` Go run has exited; ≤ 15 games; done by Sun 12:00).** Your E45 deepseek games ran with `public_board=False`, and no-channel markets undercut Nash (−0.58). In Q2.2's market (public board on), deepseek no-channel markets sit at 17.0 vs Nash 11, with open public invitations in 479/480 messages. Run deepseek A + public board (`--public`, same seeds as E45, 10–15 games, T=20). Declared question: does public cheap talk alone raise deepseek's no-channel markup (C−A vs A_pub−A), and do level screens then false-flag A_pub? It ties both repos: public text *is* a coordination channel for some families, which only a text auditor can attribute. If Go 429s, report whatever n exists and say so. If it can't start by Sun 09:00, drop it.
4. **Final adversarial review once, then freeze numbers (Sun by 14:00).** After P2.8 is final, run one codex gpt-6.1-sol review of the glance table, takeaways, abstract and P2.8 only (wording; numbers come from scripts). Run `p2_tables.py --check` and `tables.py --check` and `test_release_audit.py` after it. Then no more number edits.
5. **Hygiene, 5 min each iteration:** stamp STATUS and the ledger from `date -u`, never by estimate (the sibling had to publish a correction note for this). Fix the 09:50 STATUS header. For the merger, state the CI method in each precision/AUROC caption (Jeffreys/Wilson here, class-stratified bootstrap in Q2.2).

## STOP doing
- No new scripted conditions or sweeps. Gaps 5–9 are closed; scripted collusion is co-movement by construction.
- No more P2.3 / E54 sub-analyses. After the final E54 run (the T60 A prefixes in the pool), freeze P2.3 at its current length.
- Don't re-run or extend E43 wordings or E45 deepseek T=20. Both are answered; extra n won't change a verdict.
- No exports/PDF/deck rebuilds except Sat 19:30 and the Sun 16:30 window.
- Don't start LLM onset or LLM coalition runs (dropped; codex parallelism belongs to E44).
- Don't let the T=80 replay become a second headline. If it disagrees with T=60, report both, with T=60 primary as declared.

## Cross-pollination
- **From Q2.2 → here:** (a) E77 notes-to-self: a pair given a private notepad with *no recipient* gets ~65% of the private-channel premium. Your P2.10 (E57) already shows pair_level flags the notepad arm 11/15. Put one sentence in takeaways: level screens detect "pair singled out by the prompt", not delivered coordination. Q2.2's E92 logbook control (running) will say whether that is memory or "private" framing; cite it if it lands. (b) Q2.2 E78: a terse paraphrase removes the premium (+0.24 vs +1.75), and no-channel markets rise. That matches your P2.7 (baseline −0.19..+2.56 with wording). State both in the same words: "the channel effect is robust in your 5 wordings, not in theirs; the baseline is prompt-dependent in both". Don't paper over the discrepancy. (c) Family results: Claude no-channel markets at ≈ 20 (≥ monopoly), deepseek 17 with public invitations, sol no collusion. Absolute screens need model-matched references, which your P2.3(c) already argues.
- **From here → Q2.2:** P2.4 private cost asymmetry (for their gap 7), the all-firm cartel AUROC 0.25 (a limitation of their pair premium, especially for the random-partner arm), the E44 spillover/decay result once final, and directive 3's deepseek public-board arm.
- **For the merger:** one shared sentence both REPORTs should contain: "Detectability of LLM collusion by any price statistic is a property of the (seller model × prompt) pair. Relative screens survive a shared model but fail under market-wide spillover; absolute screens need model- and prompt-matched references."

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
  → **DONE** (E46, REPORT P2.1). CUSUM / matched-reference rows not added; **DROPPED** (low value, no change to the reading).
- **Independent reimplementation check:** have codex (gpt-6.1-sol, `-s workspace-write` in a scratch dir,
  given ONLY the REPORT's method description, not your code) reimplement your headline statistic(s); compare
  numbers on the same data. Report agreement; fix any bug found (and re-state affected numbers).
  → **DONE** (E47, REPORT P2.2: 234/236 cells < 1e-9, all 20 AUROCs identical, no bug).

## Gaps owned by THIS repo (Q1.4), in priority order (status as of 09:35 UTC)
1. **Prompt-wording robustness** (validity threat; you already saw the JSON-anchor effect). 3–5 prompt
   variants of your seller prompt (paraphrased instructions, different JSON template / no example,
   different order of information, reasoning on/off). Does the C − A markup and the level-vs-pCMI pattern
   hold across variants? Report variance across variants as a robustness band.
   → **DONE** (E43, P2.7: C − A +0.69 (SE 0.17) in 5/5 wordings, I² = 0; baseline −0.19..+2.56; within-wording markup AUROC 0.66; pCMI at chance in all 5). Remaining: one takeaway sentence reconciling with Q2.2's E78 failure (cross-pollination b).
2. **Long LLM games**: settle whether pCMI fails for lack of data. ≥ 20 runs per condition (A, C, plus D if
   budget) at T = 60–100. Power-vs-T curve on LLM data (subsample prefixes). This is the decisive 1.4 result.
   → **IN PROGRESS** [priority 1]. E44 10/40 games at 09:27, ETA ~12:20; T=80 replay ~13:30. Pipeline `scripts/e44_post.sh` ready; add a declared spillover line (directive 1). D dropped (budget; B/D added nothing in v1).
3. **Same-model confound as a headline**: in real deployments everyone runs the same few models. Quantify
   on LLM data: same-model no-channel pairs vs mixed-model pairs vs colluding pairs. Test mitigations
   (same-model surrogate null; conditioning on lagged prices of all firms; model-matched reference
   markets). State plainly what a deployer can and cannot conclude.
   → **DONE** (E48 + E54 interim, P2.3; trimmed). One mechanical step left: the final E54 run with the llm_long_p2_T60 A prefixes (inside `e44_post.sh`). Then freeze.
4. **Second seller family** in your market: deepseek (Go) sellers, ≥ 15 runs each for A and C (T=20 or
   longer). Does the channel markup and the detector pattern replicate across families?
   → **DONE** (E45, P2.9: 15 + 15, C − A +3.75 [2.77, 4.68], markup .99 / pair_level 1.00 vs pCMI .57; rule HOLDS). Optional extension: the deepseek public-board arm (directive 3) to explain the cross-market difference with Q2.2.
5. **Coalition structure**: 3-of-4 colluding and all-4 colluding (scripted + small LLM set). Pairwise
   net-influence relies on clean comparison pairs — show where it breaks and test a group-level statistic
   (e.g. multi-information / total correlation of the coalition vs surrogates).
   → **DONE (scripted)** (E49, P2.4). Small LLM set **DROPPED** (needs a new channel design). E44 spillover (directive 1) gives the LLM analogue for free.
6. **Collusion onset / detection delay**: collusion that starts at round k (scripted switch; LLM channel
   opened mid-game). Rounds-to-detection for level screen vs pCMI (CUSUM-style sequential version of the
   level screen is a good addition).
   → **DONE (scripted)** (E50, P2.4). LLM mid-game channel **DROPPED** (codex parallelism goes to E44).
7. **Market-model robustness**: N = 2 and 6 sellers, and a different demand elasticity; do the scripted
   calibration (FPR) and power results hold?
   → **DONE** (E52, P2.5).
8. **Cost asymmetry hard negative** for the dependence detectors (firms with unequal private costs).
   → **DONE** (E51, P2.4: level screens 30/30 false, pCMI 4/30). Keep it in the abstract.
9. **Non-price collusion (exploration)**: one condition of market/customer splitting or bid rotation —
   simplest: run the starter double auction (`~/collusion/collusion_hackathon/llm-agent-collusion`, via our
   llm.py — it needs adaptation since it expects a Nebius/OpenRouter key) or a quantity/territory variant
   of your sim; check which detectors see it at all.
   → **DONE (scripted bid rotation)** (E53, P2.6: predictable rotation invisible to pCMI, levels 30/30). Starter double auction **DROPPED** (adaptation cost).
Items 1–4 must be done by Sat 20:00 if at all possible; 5–9 by Sun 15:00.

**C3 Abliterated (refusal-removed) seller: does safety training suppress collusion?** (added 10:45 UTC)
Model: `huihui-ai/Huihui-Qwen3.8-27B-abliterated` on Modal (1× A100-80GB, vLLM), via
`llm.chat(..., backend="qwen")` — explicit only, no fallback. Cold start after 10 min idle: up to ~10 min,
so run games in batches back-to-back, never one-off calls spread out. Concurrency: up to ~8 parallel
games is fine (vLLM batches them).
**BUDGET (hard):** Modal credits are capped at $79.99 total until Sun 18:00 UTC; a guard stops the endpoint
at $70 for good. ~$2.80/GPU-hour. Read `~/collusion/QWEN_BUDGET.txt` before every batch; status `warn`
→ only the most valuable runs; `STOPPED` → don't use qwen, report what you have.
Design: matched seeds, base prompt, A (no channel) vs C (private channel), ≥ 15 + 15 runs (Q1.4: its
market, T=20; Q2.2: its market + the notepad/placebo arms if budget allows). Compare agreement rate,
execution (kept agreements), markup, and all headline detectors vs the safety-trained families. Also
try it in the C1 strong-collusion lever set. Never instruct agents to collude.
**Clean pair now deployed (10:55 UTC):** base model `Qwen/Qwen3.8-27B` (same weights before abliteration) via
`llm.chat(..., backend="qwen", model="qwen-base")` — separate GPU, same budget cap (the $70 stop covers both).
Run abliterated and base on the SAME seeds/conditions (A vs C, ≥ 15 + 15 each). Headline contrast: abliterated − base
(agreement rate, kept rate, markup, detector AUROCs), plus both vs gpt/deepseek. Run both arms in the same time
window so both GPUs are warm together and idle together (cost).

