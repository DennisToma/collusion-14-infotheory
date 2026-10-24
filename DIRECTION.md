# DIRECTION — Phase 2, director review 2026-10-24 17:56 UTC (Sat)
(checkpoint Sat 20:00 · experiments end Sun 15:00 · finalize-only Sun 16:30 · hard stop Sun 18:00 · merged repo `collusion-beyond-words` built from **Sun 08:00** from both REPORTs)

**Verdict.**
1. On track and still the cleanest repo. Every 15:50 directive is done or running: E69 is final (the null replicates, the E61 A-arm effect does not, and the three-pair table is built); the claims × denominators table is done (9/9, 8/9 …); the 19:30 consolidation was done early (main claim in 2 sentences, abstract 246 words); E70 = Part E1 was registered at 17:10 *before* data and is running (sweep 1 complete at 17:45, now amended to 6 sweeps before any analysis); the D2 manipulation check was declared before any ask was read. The pilot-pooling bug in E64 was found and fixed openly.
2. What remains is **E70 (the generality claim) and D2 (the external market)**, both running, plus making the top of REPORT merge-ready. One new fact matters for E70: **gpt-6-luna almost never uses the public board in the grid** (0 posts in c00/c01/c03–c07; 78/320 in c02; qwen posts every round; Q2.2 E113-amend). For luna cells, "public board ON" is therefore effectively OFF. That is confounded with the model factor and must be stated, not discovered at write-up.
3. Explore vs exploit: no new arms. One useful exploit is left for tonight's spare compute (from ~22:00): a **declared confirmatory follow-up of E70's largest main effect** (directive 3). It turns the descriptive "which factor causes the lift" (Q1.1/Q1.5) into one confirmed number. Everything else is consolidation. Two text risks: the joint sentence is *not yet verbatim*, and the title leads with the scripted result instead of the LLM finding.

## Top directives (in priority order)

1. **E70: let all 6 sweeps finish untouched. Before 19:00 (before any analysis), append ONE pre-analysis amendment to `results/e1_registration.md` + ledger.** It adds:
   (a) **Replication of the one pCMI exception.** Base qwen-3.6-35b (E69 `qb36`) is the only set with a pCMI CI > 0.5 (0.71 [0.51, 0.88]), and it is factor M's high level. Declare: "pooled pCMI AUROC channel vs no-channel in the 8 M = qwen cells; replicated if the lower CI > 0.5". Also report level − pCMI AUROC separately by M. This decides whether the abstract's "8/9" exception is a model property or noise.
   (b) **Public-board usage as a reported covariate:** the share of agent-rounds with a non-empty `public_message` per cell and arm. State that for M = luna the board is mostly unused, so V/Ch/F effects on luna cells are "with a board available, not used". Do not re-interpret factor M as "model" alone: it is "model incl. its board use".
   (c) **The follow-up rule for directive 3** (factor, levels, n, prediction direction taken from E70's sign).
   Then run `e70_grid.py --label --eval` **once** when sweep 6 is complete (ETA ~22:00; the judge labels need ~96 sol calls, so queue them as soon as sweep 6 lands). Write ≤ 15 lines + the main-effects table + one abstract sentence **tonight**, not Sun 13:00: the merge manager starts at 08:00. If generation stalls, analyse complete sweeps at Sun 08:00 at the latest, as registered.
   **Why:** E70 is the only remaining result that changes the headline ("held in k/16 cells"). (a) and (b) are cheap, legitimate only if declared before analysis, and pre-empt the obvious judge question.
2. **Text fixes before the 19:30 export (≤ 30 min, no LLM calls).**
   (a) **Joint statement, sentence 2, must be verbatim** to Q2.2's (they carry it already). Yours still says "LLM sellers raise prices…" with the scoping in a parenthesis. Replace it with exactly: "With memory and a profit objective, gpt-6-luna sellers raise prices market-wide without any channel (19/20 no-channel markets ≥ Nash + 2); agreements are then often kept (13/20) but add no detectable price, so channel labels stop being ground truth. Abliterated Qwen with memory differs (channel adds +2.13 [1.28, 3.00]; 5/20 executed), as the first sentence predicts." Keep your spillover parenthesis after it.
   (b) **Retitle.** The current title, "CMI catches coordinated price *moves*, not price *levels*…", reads as a positive detector result. Your main claim is that LLM collusion *is* a level and pCMI misses it. Suggested title: "LLM price collusion shows up as a market-wide price level, not as coordinated moves: dependence statistics vs level screens on scripted and LLM sellers". The merge manager lifts titles.
   (c) Cite Q2.2 E112 in P2.4/onset in one line: replacing a colluder mid-game left the level intact, and your E50 level CUSUM alarmed in 0/30 replaced games by round 25 (their P2.15). This is the LLM counterpart of your scripted onset result: a level CUSUM sees onsets, not personnel changes.
3. **Overnight exploit: one confirmatory follow-up of E70's largest main effect (declare in directive 1c; launch only if the E70 analysis is done by Sun 00:30; stop at Sun 08:00).**
   - **Design:** the factor with the largest |main effect| on d (C − A markup). All other factors stay at the c00 base levels (luna, private cost, visible, every-round channel, short memory, no shocks, base framing), except where the winning factor is M (then use the qwen lane). 12 + 12 matched-seed A/C games at each of the two levels (48 games), fresh seeds (8000+), same T = 20.
   - **Prediction:** the sign seen in E70, declared before generation. **Analysis:** difference in C − A between levels with a game bootstrap, run once.
   - **Fallback:** if the winning factor's effect CI in E70 already excludes 0 with |effect| > 1, or if neither lane has capacity, skip it and say so in one line.
   **Why:** E70's main effects are 7 descriptive contrasts with no multiplicity control. One fresh confirmation of the top one is the cheapest way to say "X causes the lift" to a judge (sprint Q1.1/Q1.5).
4. **D2 / E68: finish the 30 runs (15 on disk, ~12 min/run → ~21:00). Run the declared manipulation check first, then `e68_cda.py` once.** ≤ 10 lines in P2.12 + one glance row. If the check's CI includes 0, the verdict is "the starter CDA with qwen-3.6 does not elicit collusion; detector comparison uninformative", reported as a clean external-validity null. Don't tune the auction, prompt or model. Report the parse-failure count (some runs have 3).
5. **Merge-ready top by Sun 07:30, then freeze.** Title, main claim, abstract (with E70 sentence and denominators "k/16 cells"), glance, takeaways and joint statement. Run `p2_tables.py --check` with E70 + D2 rows. REPORT is at 959 lines: E70 + D2 text must replace text, not add net lines. One adversarial review at Sun ~12:30 (Opus subagent; codex sol is saturated by three managers + audits) covering E70, D2, abstract and title. Freeze numbers at Sun 14:00. PDFs at 19:30 and Sun 16:30 only.

## STOP doing
- **No further E70 amendments after directive 1's single pre-analysis amendment.** In particular no 7th/8th sweep even if generation is fast. Spare capacity goes to directive 3.
- No peeking at E70 cells or D2 asks before their declared analysis. The 4 sweep-1 log lines you saw are disclosed; don't repeat it, and use `tail` on the "done" lines only.
- No new Part C arms or models, no N = 2 implementation (the substitution is declared), no below-chance-pCMI mechanism work (one Limitations sentence; E67 settled it).
- No new watcher scripts: `e70_chain.sh` is the one chain. For the directive-3 follow-up, reuse `e1_grid.py`/`sim.llm_market` with a cell-override flag, not a new queue.
- No reviews before Sun ~12:30; no extra PDF exports.

## Cross-pollination
- **From Q2.2 → here:** (a) **E113-amend:** luna posts no public messages in the grid. This is directive 1b, and they audit text on the 8 qwen cells only. (b) **E112 (P2.15)**, sprint Q1.2: replacing one firm with a fresh luna at round 21 leaves the level (+0.20 [−0.08, +0.62]) and re-agreement (16/20) intact, and your E50 CUSUM alarms 0/30. Cite it (directive 2c). E115 (gpt-6.1-sol newcomer) lands ~21:00. (c) Q2.2 already cites your three-pair abliteration table (E61, E69, their E100). No action needed.
- **From here → Q2.2:** E70 sweeps 1–6 as they land (already published as `data/llm_grid_p2_c*` + manifest); announce "6 sweeps complete" in STATUS so their final E113 eval triggers once. Q2.2's STATUS still assumes 3 sweeps. E70 per-cell public-board usage table (directive 1b): they need it for E113.
- **Shared finding worth one joint line in both reports:** whether luna uses a public board is prompt-dependent. In your grid it stays silent (base prompt "may also post"); under Q2.2's strong framing 43% of no-channel public messages are "hold price" calls. Text-based screening therefore depends on the prompt as much as on the model.

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
→ **DONE.** Executed 48/149 C over ten sets (pilot-pooling bug fixed 17:3x: memory pilots excluded); E64 pooled pCMI executed .42 [.33, .53] vs .52; the circularity is stated. **E65** (qwen-abliterated, memory, T=40, 20 + 20): declared verdict **INCONCLUSIVE** (pCMI executed-only 0.33 [0.02, 0.66], 5/20 executed; the pilot's 5/5 did not replicate; markup .85, pCMI .49; TE .71 is exploratory → tested by E70's declared secondary TE hypothesis). **E66** (Q2.2 strongF): **NOT EVALUABLE** (tacit-high 19/20; 0/40 class mismatches). Luna memory pilot: descriptive (3/5). gpt-6.1-sol pair: DROPPED (codex saturated; sibling pilot 0/2). Nothing more to run here.

**C2 Older / weaker models as sellers** (model-generation lever: does collusion and its detectability
change across model generations?). Available and verified working 10:25 UTC:
- codex: `gpt-5.6-luna`, `gpt-5.6-sol` (previous generation) — `llm.chat(..., backend="codex", model="gpt-5.6-luna")`
- OpenCode Go: `glm-5.2`, `mimo-v2.5` (older open models) — `backend="go"`; Go is shared/slow, keep runs small.
NOT available: gpt-5, gpt-4o. **WARNING:** llm.py's codex backend silently falls back to gpt-6-luna when a
model name is unknown or limited — always check `r["model"]` and exclude/flag fallback runs.
Split: Q1.4 runs gpt-5.6-luna + glm-5.2; Q2.2 runs gpt-5.6-sol + mimo-v2.5. ~10–15 runs per model (A vs C
matched seeds), base prompt. Report per-generation: agreement rate, execution rate, markup, detector AUROCs.
Combine with C1 if a model executes collusion more readily (older models may comply/coordinate differently).
→ **DONE.** gpt-5.6-luna (E62, 10 + 10: tacit-high 9/10 in A, C − A +1.44 [0.23, 2.59], markup AUROC 0.75, pCMI 0.72 [0.47, 0.92], "not distinguishable", 0 fallback games). glm-5.2 **DROPPED** (0 complete games; Go stopped answering).

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
→ **DONE.** E61 T=20: abliterated − base (C − A) −0.37 [−2.09, 1.36], "no detectable effect"; A-arm +1.06 [0.38, 1.74] (exploratory; **not replicated** in E69: +0.35 [−0.28, 0.96]). E65 = memory lever (above). Budget ok ($18.13/$70 at 17:52). No base-model E65 counterpart; extra gateway families only as E1 factor 1 (qwen-3.6-35b).

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

## Gaps owned by THIS repo (Q1.4), in priority order (status as of 17:56 UTC; all nine closed — frozen, no further work)
1. **Prompt-wording robustness** (validity threat; you already saw the JSON-anchor effect). 3–5 prompt
   variants of your seller prompt (paraphrased instructions, different JSON template / no example,
   different order of information, reasoning on/off). Does the C − A markup and the level-vs-pCMI pattern
   hold across variants? Report variance across variants as a robustness band.
   → **DONE** (E43, P2.7). Frozen.
2. **Long LLM games**: settle whether pCMI fails for lack of data. ≥ 20 runs per condition (A, C, plus D if
   budget) at T = 60–100. Power-vs-T curve on LLM data (subsample prefixes). This is the decisive 1.4 result.
   → **DONE** (E44, P2.8: "level, not short", pCMI 0.34 [0.18, 0.52] at T=60, decline from 0.52 at T=20 not significant (−0.18 [−0.41, +0.05]); co-move excess +0.004 vs planting MDE). D and T=80 **DROPPED**. Below-chance mechanism: E67 tested stickiness and it is **not supported**. Stop here; one Limitations sentence (STOP list).
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
   → **DONE (scripted bid rotation)** (E53, P2.6). The starter double auction = Part D2 (in progress, directive 4 of 17:56).
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
→ **C3b DONE** (E69, 17:22, declared contrast run once: abliterated − base (C − A) −0.65 [−1.97, +0.65], null replicates; executed 7/15 vs 3/15; base qb36 pCMI 0.71 [0.51, 0.88] = the one set with pCMI CI > 0.5 → replication declared inside E70, directive 1a). Three-pair table in P2.11(b2), checked by p2_tables; Q2.2 cites it. **C3c** (Q2.2): **DROPPED** at its registered pilot (E109: base 9B prices below Nash).



**Serendipity Explorer (added 14:50 UTC):** a third agent runs wild cheap pilots in `~/collusion/collusion-serendipity` (other markets, hub-and-spoke advisor, leniency, counterfactual replay, steganography in prices, personas, ...). Read its `HITS.md` at the start of every iteration; if a hit bears on your headline claims, decide explicitly (in STATUS) whether to confirm it with a registered experiment. Don't duplicate its pilots.
→ Status 17:56: **still no promoted hits** (S01, S03, S07 duds; S02 odd/inconclusive; S04 uninformative). S03's "deterministic lag-conditioned responses can yield common action cycles without messages" is a candidate negative control for pCMI, but it is unconfirmed and not promoted: do not act on it. Keep one STATUS line per iteration.

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
  → **IN PROGRESS = E70** (registered 17:10 before data, `results/e1_registration.md`; factor 2 substituted by private-vs-public cost, declared up front; sweep 1 complete 17:45; amended 3 → 6 sweeps before analysis; ETA ~22:00). Next: one pre-analysis amendment (qwen-cell pCMI replication, board-usage covariate, follow-up rule) → analysis once → write-up tonight (directives 1, 3). Finding so far (Q2.2 E113-amend): luna leaves the public board mostly unused.
- **E2 Participant replacement mid-game (owner Q2.2; sprint Q1.2).** In executed-collusion games (strong arm / qwen memory),
  replace one colluder at round T/2 with a fresh agent (same model, no chat history) or a different model. Does the price
  level survive? Do detectors notice the break (changepoint)? Cheap, novel, and answers an official sprint question.
  → **DONE by Q2.2** (E112, P2.15: level and re-agreement survive a fresh-luna replacement at round 21; your E50 CUSUM copied there, 0/30 alarms by r25). Second arm E115 (gpt-6.1-sol newcomer) running, ETA ~21:00. Here: one citation line (directive 2c).
- **E3 Cross-family collusion (owner Q2.2; sprint Q3.3 "can agents identify their peers?").** Pair = luna + qwen (different
  families) with a channel vs same-family pairs. Do mixed pairs agree / execute as often? Does pCMI see same-family pairs
  more (shared-policy confound)?
  → Q2.2-owned; being dropped there (gateway saturated by E70's qwen lane + D2; E70 factor M varies family at market level). Nothing to do here.
- **E4 Anomaly hunt (owner both, 30 min each, zero new games).** Have codex gpt-6.1-sol read ~40 randomly sampled
  transcripts across ALL datasets (both repos) and list the 5 most surprising behaviours with run ids. Each becomes a
  15-min test logged as `serendipity` in EXPERIMENTS.tsv. Report the hits and the duds.
  → **DONE for both repos** by Q2.2's E108 (P2.13: 40 games sampled across both repos' datasets, 5 follow-ups, hits + duds, codex-verified). Here: cite P2.13 in one line. **Don't run a second hunt** (duplicate work).
- **E5 One non-English market (owner Q2.2, small, 10+10).** Same game, all prompts and messages in German. Does the text
  auditor (English-prompted) still behave the same? Does collusion change with language?
  → **DONE by Q2.2** (E110, P2.14: explicit agreement 3/10 DE vs 9/10 EN; premium persists +0.91 [+0.20, +1.58]). Nothing to do here.

For every claim in the final abstract, write its denominator next to it (conditions tested, models, datasets).
→ **DONE** (`scripts/claims_denominators.py`, REPORT P2.13, in `p2_tables --check`: premium 9/9 sets (7 models), level > pCMI 9/9, pCMI null 8/9, executed ≤ 50% 8/9, tacit rare 8/9). E70 adds "k/16 cells" (directive 5).

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
  → Q2.2 **DONE** (E104 P(said | executed) 0.385; E105 text auditor 0.87 [0.83, 0.91] vs TF-IDF 0.91). Q1.4 optional pCMI **DROPPED**: one verdict per agent per episode, no action time series. Cite SALT's silent luna/terra executors in the "why price-only detection" takeaway (done in Limitations).
- **D2 Double auction** (owner: Q1.4). Starter `~/collusion/collusion_hackathon/llm-agent-collusion`
  (Agrawal et al. 2025, continuous double auction; 3 sellers + 3 buyers, seller communication optional). Copy the
  code into this repo (don't modify the starter), and write a small adapter so its model wrapper calls our
  `llm.chat` (it expects a Nebius/OpenRouter key; route to codex luna/sol, Go deepseek, or the Aqueduct gateway
  qwen-3.6-35b — record the model per run). Conditions: seller communication on vs off, ≥ 15 + 15 runs. Apply
  the frozen level screen, pCMI and dependence detectors on seller ask series. Does price-level-not-dependence hold
  in a different market mechanism?
  → **IN PROGRESS** (E68 declared 14:23; manipulation check declared 17:12 before any ask was read; 15/30 runs on disk at 17:55, ~10–12 min/run → ETA ~21:00). Seed-0 chat was competitive. Analyse once at 15 + 15 (or Sun 10:00 with what exists): manipulation check first, then detectors (directive 4).
- **D3 LLM trust-breaking** (owner: Q2.2, lowest priority of the three). Starter
  `~/collusion/collusion_hackathon/llm-trust-breaking` (private plans, public announcements, actions, outcomes in
  repeated games). Measures promise-breaking, NOT collusion — use it only to validate our say-vs-do machinery
  (claim–action consistency table, text-vs-action auditors) on someone else's data. Same adapter approach;
  small n (~20–40 trials) is enough.
  → Q2.2-owned; **DROPPED** there (promise-breaking, not collusion; time better spent on E99 and D1).

Budget: D1 is auditor calls only (sol, ~1–2k calls); D2/D3 generation can use the Aqueduct gateway (45/min cap
handled by llm.py) or codex luna. Register each in EXPERIMENTS.tsv first; write each up once as a short
"External validity" subsection (≤ 15 lines + 1 table).
