# DIRECTION — Phase 2, director review 2026-10-24 13:45 UTC (Sat)
(checkpoint Sat 20:00 · experiments end Sun 15:00 · finalize-only Sun 16:30 · hard stop Sun 18:00)

**Verdict.**
1. On track. Q1.4 now has its answer: E44 is final, pre-registered and decisive ("level, not short": pCMI 0.34 at T=60). Every original gap is closed or dropped with a reason, Part C (E61/E62/E64) is final at T=20, and the qb double writer was fixed and disclosed. This is still the cleaner of the two repos.
2. Two things are left that can change the claim. E65 (qwen-abliterated, memory, T=40, 6/40 at 13:41, ETA ~16:30) and E66 (frozen detectors on Q2.2's `llm_p2strongF`, sibling at 18/40, ETA ~16:00) together are the "strongest executed collusion" test. Both are declared with rules. Don't add arms. Wait, then run each once.
3. New methodological problems a judge will catch. (a) **E64's level AUROCs on the "executed" class are circular**: "executed" requires pair ≥ Nash+2, so market_level ≈ 1.00 holds by construction. Yet the abstract sets it against pCMI 0.43 as if it were evidence. (b) **pCMI is consistently *below* chance** (T=60 0.34, executed T=60 0.17, qwen executed 0.31/0.36), and this goes unexplained. That is a mechanism waiting to be named, not noise. (c) Ledger and STATUS timestamps run ahead of the clock again (E66-declared stamped 13:48, STATUS "13:45", both written before 13:41). Part D2 (external double auction, owned here) has **not started**.

## Top directives (in priority order)

1. **E65 + E66: run each exactly once when its data is complete. Report the declared verdict verbatim.** These are the last results that decide Q1.4.
   - E66: snapshot `llm_p2strongF` only when the sibling has 40/40 *and* its `results/analysis/p2_strong_classes_llm_p2strongF.json` exists. Compute classes with your copied code **and assert they match the sibling's class file run by run**. Report any mismatch rather than picking one. Classes with n < 3 are descriptive (as declared).
   - E65: when 40 land, run `p2_partc.py` + the E60 spillover + TE. Also add the **A-arm contrast abliterated − base** from E61 (A markup −1.47 vs −2.53: abliteration may raise *no-channel* prices, not channel collusion). It is one line from existing data.
   - Wording: E61 is "no detectable effect, CI [−2.09, +1.36]", not "no effect".
   **Why:** strongly executed collusion with memory is the condition where moves *should* appear if they ever do. A null from either is the headline. A pass is a bigger one.
2. **Fix the E64 circularity in text now (15 min, no new numbers).** In P2.11, the glance row C and the abstract, say that market_level/pair_level on the executed subset are near 1 *by construction* (the executed rule conditions on the pair level). The informative executed-subset rows are pCMI/TE only. Rephrase the abstract clause to: "restricting to executed agreements does not raise pCMI (0.43 [0.33, 0.56] vs 0.49 for non-executed)". Compare executed with non-executed, not pCMI with market level. **Why:** it is the first thing a careful judge will pick at, and the fix is free.
3. **Declare and run E67, a price-stickiness (variance) screen that explains below-chance pCMI. No LLM calls, ~45 min.** Hypothesis: colluding pairs *hold* prices, so their residual variance is near 0, ρ is low and pCMI comes out below chance. That turns "pCMI fails" into "a coordinated level shows up as *missing* co-movement". It also gives a third, dependence-free statistic: the classic cartel variance screen (Abrantes-Metz et al. 2006; Harrington's screening survey). Statistics: per-run pair no-change rate and pair price variance (second half), AUROC C vs A, and pCMI stratified by stickiness tercile. **Disclosure required:** the director already looked at pair no-change rates on three sets: `llm_qa_p2` C 0.88 vs A 0.52, `llm_v1` 0.75 vs 0.65, `llm_long_p2_T60` 0.81 vs 0.81. In A games "pair" meant the first two firms, so use the max/mean over pairs in your version. Those sets are therefore exploratory. E65, E66 and `llm_g56l_p2` are confirmatory if you declare before running on them. Write it up as ≤ 8 lines in P2.11 or P2.8, and as one clause in takeaway 7 only if it holds.
4. **Part D2 double auction: start now, time-boxed. Generation has long lead time.** Copy `collusion_hackathon/llm-agent-collusion` into `external/cda/` (don't modify the starter). Add an adapter so `src/resources/model_wrappers.py` calls `llm.chat` with **backend aqueduct `qwen-3.6-35b`** (free). Fallback: Go deepseek-v4.1-flash. **Avoid codex**, which is saturated (≥ 12 codex processes at 13:41). Use **3 sellers, rule-based `zip` buyers (no calls), 30 rounds** (the default 15 is too short: the shift null needs ≥ 20 valid shifts), comms on vs off, ≥ 15 + 15 seeds. That's ~90 calls/run, ~2.7k calls in total. Gateway: ≤ 3 parallel calls from this repo (the sibling's qwenbS also uses it). Declare E68 first: frozen level screen (mean ask over CE / their collusion index), max-pair pCMI and TE on the seller ask series, and the E67 stickiness screen. Prediction: level AUROC > pCMI AUROC. **Milestones:** 2-run smoke by Sat 18:00; **if the smoke fails at Sat 20:00, DROP D2** and write one Limitations line. Full set by Sun 10:00; write-up ≤ 15 lines + 1 table by Sun 12:00. **Why:** "level, not dependence" is so far shown only in our toy market (and the sibling's). One different mechanism is the strongest external-validity answer and is assigned to you.
5. **Checkpoint Sat 19:30, then freeze.** Rewrite P2.11 once with E65/E66 (or interim n if they're late, labelled as such) and E67. The main claim gains at most one clause. Run `p2_tables.py --check`, `tables.py --check` and `test_release_audit.py`, and export PDFs once. Run one adversarial review (Opus *or* codex, not both, since codex is saturated) of abstract + glance + P2.8 + P2.11 at ~18:30. The final review on Sun ~12:30 should include D2. Freeze numbers at Sun 14:00.

**Housekeeping (5 min):** stamp every ledger/STATUS row from `date -u` at the moment of writing. Append one correction row for E66-declared (written ~13:3x, stamped 13:48). The commit hash is the proof of order. Commit the modified `llm_g56l_p2` / `llm_strong_qb_pilot` data only after confirming those generators have exited.

## STOP doing
- **No new Part C arms or seller families.** glm-5.2 is DROPPED: 0 complete games after ~2.5 h, no process running. Say so in P2.11. The luna memory pilot (`llm_strong_luna_pilot`, running) finishes as a *descriptive* pilot and is **not promoted**, because E65 is the promoted arm. Don't relaunch it if it dies.
- Peeking at E65/E66 before completion, or running detectors on partial E65 data.
- SALT (D1) pCMI: **DROPPED**. A SALT episode has one ACCEPT/REJECT decision per agent and no action time series, so dependence statistics don't apply. Say this in one line.
- T=80 replays, new scripted conditions, extra wording variants.
- Growing REPORT.md (≈ 950 lines). New text replaces old. E67/D2 each get ≤ 15 lines.
- Two review passes per section, PDFs outside Sat 19:30 / Sun 16:30.

## Cross-pollination
- **From Q2.2 → here:** (a) **SALT D1 (E104):** P(said | executed) 0.385 overall but ≈ 0 for gpt-5.6-luna/terra, which execute in ~51% of episodes and never state it. That is an external instance of "actions without words". Cite it in the takeaway on why price-only detection matters. (b) Sibling P2.10 asymmetry (legit cost edge flagged 7/10, competition predicts +1.45) is the LLM version of your P2.4 cost-asymmetry hard negative. Cite both ways. (c) The sibling's P2.9: monitor-aware luna pairs stop agreeing (0/10) rather than evade, so there is no evasion arm for dependence detectors to test. Mention it as a limitation, not a gap. (d) Use the sibling's class file for E66 (directive 1).
- **From here → Q2.2:** E61 abliteration null at T=20 (−0.37 [−2.09, 1.36]) for their E100 cross-market comparison; older gpt-5.6-luna is **tacitly high 9/10** with markup AUROC down to 0.75 (pairs with their sol none ≈ Nash+4 and mimo); E64 executed-vs-not pCMI; E67 stickiness (if it holds, it is a cheap extra column in their action_stats view, but *not* to be added there now).
- **Merger sentences (both REPORTs, verbatim):** "Detectability of LLM collusion by any price statistic is a property of the (seller model × prompt) pair. Relative screens survive a shared model but fail under market-wide spillover; absolute screens need model- and prompt-matched references." After E65/E66/E99 land: "With memory and a profit objective, LLM sellers raise prices market-wide without any channel; executed (kept) agreements are rare (X/Y), and channel labels stop being ground truth." Fill X/Y from the joint table (directive 4 of the 11:45 review, shared definitions unchanged).

---

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
→ **IN PROGRESS (final stage).** DONE: executed/tacit rates on seven sets (33/99 executed C; tacit 1/94 current models), E64 executed-subset table (fix circular level rows, directive 2), E63 qwen memory pilots (abliterated 5/5 executed, base 3/5). **E65** promoted arm `llm_strong_qa` 20 + 20, T=40: generating, 6/40 at 13:41, ETA ~16:30 (directive 1). **E66** frozen detectors on sibling `llm_p2strongF`: declared and implemented; sibling 18/40, ETA ~16:00. Luna memory pilot: running, descriptive only, not promoted. Gpt-6.1-sol pair lever: **DROPPED** (codex saturated; the sibling's sol pilot showed 0/2 agreements).

**C2 Older / weaker models as sellers** (model-generation lever: does collusion and its detectability
change across model generations?). Available and verified working 10:25 UTC:
- codex: `gpt-5.6-luna`, `gpt-5.6-sol` (previous generation) — `llm.chat(..., backend="codex", model="gpt-5.6-luna")`
- OpenCode Go: `glm-5.2`, `mimo-v2.5` (older open models) — `backend="go"`; Go is shared/slow, keep runs small.
NOT available: gpt-5, gpt-4o. **WARNING:** llm.py's codex backend silently falls back to gpt-6-luna when a
model name is unknown or limited — always check `r["model"]` and exclude/flag fallback runs.
Split: Q1.4 runs gpt-5.6-luna + glm-5.2; Q2.2 runs gpt-5.6-sol + mimo-v2.5. ~10–15 runs per model (A vs C
matched seeds), base prompt. Report per-generation: agreement rate, execution rate, markup, detector AUROCs.
Combine with C1 if a model executes collusion more readily (older models may comply/coordinate differently).
→ gpt-5.6-luna **DONE** (E62, 10 + 10: tacit-high 9/10 in A, C − A +1.44 [0.23, 2.59], markup AUROC 0.75, pCMI 0.72 [0.47, 0.92]; n = 10, so describe pCMI 0.72 as "not distinguishable from the other sets", not as a pCMI success). Confirm 0 fallback runs (`gt.model`) in the table note. glm-5.2 **DROPPED** (0 complete games, generator gone).

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
**Clean pair (updated 11:20 UTC):** control = base `Qwen/Qwen3.8-27B` (FP8) via the TU Wien Aqueduct gateway:
`llm.chat(..., backend="qwen", model="qwen-base")` (routes to the gateway) — free, fast, no Modal cost. Abliterated stays on
Modal (bf16; note the FP8-vs-bf16 precision difference as a caveat). Run both on the SAME seeds/conditions (A vs C,
≥ 15 + 15 each). Headline: abliterated − base (agreement, kept rate, markup, detector AUROCs), plus vs gpt/deepseek.
Gateway also serves `qwen-3.6-35b`, `glm-5.3-744b-experimental`, `deepseek-v4-vision-exp-284b` via
`llm.chat(..., backend="aqueduct", model=...)` — extra seller families for C2/robustness (shared university
gateway: keep ≤ 4 parallel calls, back off on 429).
→ T=20 contrast **DONE** (E61: C − A abliterated +2.97 vs base +3.34, contrast −0.37 [−2.09, 1.36]; executed 8/15 vs 6/15; dedup incident disclosed; transcripts checked, undercutting is genuine). Strong lever set: E65 in progress (directive 1). Budget ok ($8.76/$70 at 13:41). A base-model E65 counterpart (20 + 20 on the gateway) is **not** to be added: pilot 5 + 5 is the matched reference, reported descriptively. Extra gateway families: **not now**, except qwen-3.6-35b as the D2 seller.

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
  → **DONE** (E46, P2.1). CUSUM / matched-reference rows **DROPPED** (low value).
- **Independent reimplementation check:** have codex (gpt-6.1-sol, `-s workspace-write` in a scratch dir,
  given ONLY the REPORT's method description, not your code) reimplement your headline statistic(s); compare
  numbers on the same data. Report agreement; fix any bug found (and re-state affected numbers).
  → **DONE** (E47, P2.2: 422/424 cells < 1e-9, all 20 AUROCs identical, no bug).

## Gaps owned by THIS repo (Q1.4), in priority order (status as of 13:45 UTC)
1. **Prompt-wording robustness** (validity threat; you already saw the JSON-anchor effect). 3–5 prompt
   variants of your seller prompt (paraphrased instructions, different JSON template / no example,
   different order of information, reasoning on/off). Does the C − A markup and the level-vs-pCMI pattern
   hold across variants? Report variance across variants as a robustness band.
   → **DONE** (E43, P2.7). Frozen.
2. **Long LLM games**: settle whether pCMI fails for lack of data. ≥ 20 runs per condition (A, C, plus D if
   budget) at T = 60–100. Power-vs-T curve on LLM data (subsample prefixes). This is the decisive 1.4 result.
   → **DONE** (E44, P2.8: "level, not short", pCMI 0.34 [0.18, 0.52] at T=60, decline from 0.52 at T=20; co-move excess +0.004 vs planting MDE). D and T=80 **DROPPED**. Open follow-up: the below-chance value has to be *explained* (E67, directive 3).
3. **Same-model confound as a headline**: in real deployments everyone runs the same few models. Quantify
   on LLM data: same-model no-channel pairs vs mixed-model pairs vs colluding pairs. Test mitigations
   (same-model surrogate null; conditioning on lagged prices of all firms; model-matched reference
   markets). State plainly what a deployer can and cannot conclude.
   → **DONE** (E48 + E54, P2.3). Frozen.
4. **Second seller family** in your market: deepseek (Go) sellers, ≥ 15 runs each for A and C (T=20 or
   longer). Does the channel markup and the detector pattern replicate across families?
   → **DONE** (E45 + E58 + E59, P2.9; now also qwen base/abliterated and gpt-5.6-luna in P2.11). Frozen.
5. **Coalition structure**: 3-of-4 colluding and all-4 colluding (scripted + small LLM set). Pairwise
   net-influence relies on clean comparison pairs — show where it breaks and test a group-level statistic
   (e.g. multi-information / total correlation of the coalition vs surrogates).
   → **DONE (scripted)** (E49, P2.4). LLM set **DROPPED** (needs a new channel design). The LLM analogue is E60 spillover + tacit-high markets (gpt-5.6-luna 9/10; E66 tacit-high class).
6. **Collusion onset / detection delay**: collusion that starts at round k (scripted switch; LLM channel
   opened mid-game). Rounds-to-detection for level screen vs pCMI (CUSUM-style sequential version of the
   level screen is a good addition).
   → **DONE (scripted)** (E50, P2.4). LLM mid-game channel **DROPPED** (codex budget).
7. **Market-model robustness**: N = 2 and 6 sellers, and a different demand elasticity; do the scripted
   calibration (FPR) and power results hold?
   → **DONE** (E52, P2.5).
8. **Cost asymmetry hard negative** for the dependence detectors (firms with unequal private costs).
   → **DONE** (E51, P2.4); sibling's LLM version (P2.10) now cites it.
9. **Non-price collusion (exploration)**: one condition of market/customer splitting or bid rotation —
   simplest: run the starter double auction (`~/collusion/collusion_hackathon/llm-agent-collusion`, via our
   llm.py — it needs adaptation since it expects a Nebius/OpenRouter key) or a quantity/territory variant
   of your sim; check which detectors see it at all.
   → **DONE (scripted bid rotation)** (E53, P2.6). The starter double auction is now Part D2 (directive 4).
Items 1–4 must be done by Sat 20:00 if at all possible; 5–9 by Sun 15:00.


**C3b/C3c — replicate the abliteration null on more Qwen pairs (added 16:00 UTC).** C3 (Qwen3.8-27B) gave no
abliteration effect; one pair is a case, three pairs are a pattern. Same design as C3 (matched seeds, A vs C,
15 + 15 per model, base prompt; plus the memory lever if C3's memory arm shows execution), all via `llm.chat(backend="qwen", model=...)`
unless noted:
- **C3b Qwen3.6-35B-A3B (MoE, 3B active):** abliterated `model="qwen36-abliterated"` (Modal L40S, FP8) vs base
  `llm.chat(backend="aqueduct", model="qwen-3.6-35b")` (gateway, AWQ 4-bit, free). Owner: Q1.4.
- **C3c Qwen3.5-9B (small, cheap):** `model="qwen9-abliterated"` vs `model="qwen9-base"` (both Modal L4, FP8 —
  identical serving, the cleanest pair). Owner: Q2.2. First check the 9B follows the game protocol (parse rate,
  sane prices in 3 pilot games); if > 10% unparsable or nonsense prices, report that and drop it.
Each Modal endpoint cold-starts in up to ~10 min after 10 min idle → run each model's games as one batch.
Cost ≈ L40S $2.2/h, L4 $1/h each; the $70 guard covers all apps. Priority: after the running Part C arms and
Part D1, before Part D2/D3. Report the three pairs in one table: abliterated − base (agreement, executed, markup,
detector AUROCs) with CIs, and state the precision caveat (FP8/AWQ/bf16) per pair.



**Serendipity Explorer (added 14:50 UTC):** a third agent runs wild cheap pilots in `~/collusion/collusion-serendipity` (other markets, hub-and-spoke advisor, leniency, counterfactual replay, steganography in prices, personas, ...). Read its `HITS.md` at the start of every iteration; if a hit bears on your headline claims, decide explicitly (in STATUS) whether to confirm it with a registered experiment. Don't duplicate its pilots.

## Part E — BROADEN THE DESIGN so we can make concrete, general claims (added by Dennis 14:30 UTC)
**Why:** so far we varied one thing at a time (model, prompt, memory, channel) in mostly one market setup. Claims like
"collusion shows up as level, not co-movement" are only as general as the conditions we tested. Goal: a small number of
designs that turn one-off pilots into **general statements with a denominator** ("held in 14 of 16 conditions").
**Priority:** right after finishing the in-flight Part C arms; run in parallel with Part D (different backends). Results by Sun 13:00 UTC.

- **E1 Factorial "generalization grid" (owner Q1.4 generates, Q2.2 audits).** 2-level fractional factorial, 2^(7-3) = 16
  cells (resolution IV), ~6 games per cell (A vs C split inside each cell), T=20, public messages logged. Factors:
  (1) seller family: gpt-6-luna vs Aqueduct qwen-3.6-35b; (2) firms: 2 vs 4; (3) rivals' prices visible each round vs hidden
  (only own sales); (4) private channel only in round 1 vs every round; (5) memory: last 3 rounds vs full history;
  (6) public demand/cost shocks: none vs random; (7) framing: neutral vs long-run-profit.
  Outcomes per cell: channel markup, executed rate, market-wide spillover, level-screen AUROC, pCMI AUROC, text-auditor flag rate.
  Report main effects with CIs (which factors CAUSE the price lift — answers sprint Q1.1 — and which single restriction
  cuts it most — answers Q1.5) and the claim's **denominator** (in how many cells level > co-movement, text ≈ chance).
  Gateway is 45 calls/min shared: luna cells via codex, qwen cells via gateway; one queue, resumable, registered first.
- **E2 Participant replacement mid-game (owner Q2.2; sprint Q1.2).** In executed-collusion games (strong arm / qwen memory),
  replace one colluder at round T/2 with a fresh agent (same model, no chat history) or a different model. Does the price
  level survive? Do detectors notice the break (changepoint)? Cheap, novel, and answers an official sprint question.
- **E3 Cross-family collusion (owner Q2.2; sprint Q3.3 "can agents identify their peers?").** Pair = luna + qwen (different
  families) with a channel vs same-family pairs. Do mixed pairs agree / execute as often? Does pCMI see same-family pairs
  more (shared-policy confound)?
- **E4 Anomaly hunt (owner both, 30 min each, zero new games).** Have codex gpt-6.1-sol read ~40 randomly sampled
  transcripts across ALL datasets (both repos) and list the 5 most surprising behaviours with run ids. Each becomes a
  15-min test logged as `serendipity` in EXPERIMENTS.tsv. Report the hits and the duds.
- **E5 One non-English market (owner Q2.2, small, 10+10).** Same game, all prompts and messages in German. Does the text
  auditor (English-prompted) still behave the same? Does collusion change with language?

For every claim in the final abstract, write its denominator next to it (conditions tested, models, datasets).

## Part D — EXTERNAL VALIDITY with the three proposed datasets (added by Dennis 14:05 UTC)
**Priority:** after the important in-flight work (E44/P2.8, Part C strong arm + C3 qwen pair, the Sat 20:00
checkpoint) — and BEFORE any remaining exploration-portfolio (part B) items. Target: results by Sun 12:00 UTC.
**Why:** every result so far comes from our own simulated market. Judges will ask whether "price level yes,
dependence no, words no" is an artifact of our toy market. External data is the strongest answer.
Use FROZEN detectors/auditors (no re-tuning on external data); report agreement/disagreement with our
findings honestly, including where they don't transfer.

- **D1 SALT-NLP agent-collusion** (owner: Q2.2; Q1.4 may read the data). HF dataset `SALT-NLP/agent-collusion`
  (public, not gated; ~27k episodes + ~2.6k longer trajectories; two-agent communication, decisions, tool traces,
  rewards, settings). Download to `/var/tmp` (not into git; commit only a small sample + a loader + summary stats).
  Read its README/paper for the operational definition of its collusion field; map it explicitly to our label
  levels (opportunity / agreement / executed) and say where it differs. Stratified sample of ~200–300 episodes.
  Run the frozen auditor views (text, action, combined, action_stats where defined) + simple non-LLM baselines.
  Headline: Δ_hybrid on external data with bootstrap CI. Note: two-agent episodes → no pairwise net-influence;
  Q1.4 can still test pCMI/MI between the two agents over trajectories if they are long enough (optional).
  → Q2.2 **IN PROGRESS** (E104 done, E105 text auditor 192/240 at 13:41). Q1.4 optional pCMI **DROPPED**: one verdict per agent per episode, no action time series.
- **D2 Double auction** (owner: Q1.4). Starter `~/collusion/collusion_hackathon/llm-agent-collusion`
  (Agrawal et al. 2025, continuous double auction; 3 sellers + 3 buyers, seller communication optional). Copy the
  code into this repo (don't modify the starter), and write a small adapter so its model wrapper calls our
  `llm.chat` (it expects a Nebius/OpenRouter key; route to codex luna/sol, Go deepseek, or the Aqueduct gateway
  qwen-3.6-35b — record the model per run). Conditions: seller communication on vs off, ≥ 15 + 15 runs. Apply
  the frozen level screen, pCMI and dependence detectors on seller ask series. Does price-level-not-dependence hold
  in a different market mechanism?
  → **NOT STARTED, start now** (directive 4: aqueduct qwen-3.6-35b, zip buyers, 30 rounds, smoke by Sat 18:00, drop if the smoke fails at Sat 20:00).
- **D3 LLM trust-breaking** (owner: Q2.2, lowest priority of the three). Starter
  `~/collusion/collusion_hackathon/llm-trust-breaking` (private plans, public announcements, actions, outcomes in
  repeated games). Measures promise-breaking, NOT collusion — use it only to validate our say-vs-do machinery
  (claim–action consistency table, text-vs-action auditors) on someone else's data. Same adapter approach;
  small n (~20–40 trials) is enough.
  → Q2.2-owned; **DROPPED** there (promise-breaking, not collusion; time better spent on E99 and D1).

Budget: D1 is auditor calls only (sol, ~1–2k calls); D2/D3 generation can use the Aqueduct gateway (45/min cap
handled by llm.py) or codex luna. Register each in EXPERIMENTS.tsv first; write each up once as a short
"External validity" subsection (≤ 15 lines + 1 table).
