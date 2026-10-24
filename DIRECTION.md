# DIRECTION — Phase 2, director review 2026-10-24 11:45 UTC (Sat)
(checkpoint Sat 20:00 · experiments end Sun 15:00 · finalize-only Sun 16:30 · hard stop Sun 18:00)

**Verdict.**
1. Still on track, and still the methodologically cleaner repo. Gaps 1 and 3–9 are closed with declared rules and CIs, and a regenerable glance table backs them. E44 (30/40 games at 11:36, ETA ~12:30–13:00) is the one result that decides Q1.4. Part C was declared properly (E61–E63) before generation.
2. Part C is spread thin and partly broken. **Two processes are writing `data/llm_qb_p2` at once**: `llm_qb_p2_A_000` exists twice with different prices (7.9 vs 9.25 mean; 40 trajectory rows). They also put ~12 workers on a shared gateway whose limit is ≤ 4 parallel calls. The abliterated endpoint hasn't answered since 11:00. Codex is oversubscribed across both repos (19 codex processes at 11:37).
3. Biggest new risk to the claim: Q2.2's strong-framing pilot shows a **no-channel market at 16.3** (Nash 10–13). With memory and a profit objective, LLM sellers collude *tacitly*, so a channel label is no longer a clean ground truth. Your Part C must label by behaviour (executed / tacit) and report the tacit rate in A, not only the executed rate in C.

## Top directives (in priority order)

1. **Fix the qwen-base double writer now (5 min), before any qwen number is computed.** Kill the stray manual loop (`bash -c for i in 1 2 3 4 5; do … llm_qb_p2 …`, PID 3549375 and its children). Keep the queue's own `llm_queue_partc.sh qwen` process. Then dedupe `data/llm_qb_p2` by run_id: drop *both* copies of `llm_qb_p2_A_000` and let the queue regenerate it, rather than picking the copy you like. Add an assert in `p2_partc.py` (and before any eval) that run_ids are unique per dataset. Keep total gateway concurrency ≤ 4 calls (DIRECTION C3), i.e. `--workers` ≤ 4 for all qwen-base/aqueduct runs combined. Log it as one ledger row (E61 data incident). **Why:** a duplicated, nondeterministic run inside a confirmatory set is exactly what a judge's reproducibility check catches.
2. **E44 → P2.8 exactly as declared (unchanged from the last review; when 40 land, do not peek earlier).** `bash scripts/e44_post.sh` on `llm_long_p2_T60`. Report the declared verdict verbatim, plus the MDE bound, decay and the E60 spillover line. Then fill main claim, abstract sentence, glance row 2 and takeaway 7. **Add, from the same data, the Part C classification (cheap, no new calls):** run `p2_partc.py`'s executed rule on E44 C games, and a *tacit* rule on E44 A games (market ≥ Nash + 2 over the second half, no channel). The T=60 games are your longest own-market positive arm. Executed rate and tacit rate at T=60 are both headline numbers.
3. **Part C: re-scope to what only this repo can do. Drop the codex-heavy duplicates.**
   (a) **Cancel the T=80 replay** (the last step of `llm_queue_p2c.sh`; don't edit the running script, kill it when it gets there, or replace the queue). It was already secondary, and codex is the bottleneck for both repos.
   (b) **Keep E62 gpt-5.6-luna** (10 + 10, T=20). It is your C2 assignment.
   (c) **Keep the E63 luna memory pilot (5 + 5, T=40)** as your own-market strong arm. Promote it to a full arm (≥ 20 + 20, new seeds, declared) **only if** the pilot meets the executed rule in ≥ 3/5 C games **and** that is known by Sat 17:00. Otherwise don't scale it.
   (d) **Instead, evaluate your frozen detectors on Q2.2's `llm_p2strongF`** (luna, strong framing, T=40, 20 private + 20 none, matched seeds; ETA ~17:00–19:00). Treat it like E57/p2cue: declare first, no tuning. Run pCMI, TE, max-pair markup, pair_level and E60 spillover, by *behaviour class*: executed private / non-executed private / tacit-high none / competitive none. The question only you can answer: when collusion is executed and sustained over 40 rounds with full memory, do coordinated *moves* finally show up (pCMI/TE above chance on executed vs competitive), or is it still a level? That is the Q1.4 answer at its strongest. A null here is also a headline.
   (e) **qwen (E61/E63):** qwen-base A games price at 7–8, *below* Nash 10. Before reporting anything, check 2–3 transcripts: does the model understand the payoff, is it parsing the right field, is a reasoning trace leaking into the price? Report it as a degenerate/undercutting family if that is what it is. **Abliterated deadline:** if `llm_qa_p2` has returned no game by Sat 14:00, stop the qa process. Report base-only in P2.11 and say why. Retry abliterated in one back-to-back batch only if Dennis reports the endpoint up (budget is fine: $3.27/$70 at 11:35). glm-5.2 on Go: report whatever n exists at Sun 12:00; don't chase it.
4. **Harmonise the executed-collusion definition with Q2.2 before writing P2.11 (both repos must use one for the merger).** Shared primary rule: *judged agreement* AND both pair firms within ±1 of the agreed price in ≥ 50% of post-agreement rounds AND pair mean ≥ Nash + 2 over those rounds (= your current rule, = Q2.2's "strict"). Shared *tacit* rule for no-channel markets: market mean ≥ Nash + 2 over the second half. Report Jeffreys CIs. One small table: rows = dataset/model/lever; columns = executed rate (C), tacit rate (A), C − A markup, AUROC markup, AUROC pCMI.
5. **Checkpoint (Sat 19:30): P2.8 final, P2.11 with whatever Part C exists, all checks green.** Keep P2.11 ≤ 20 lines + one table. The main claim gains at most one clause from Part C. Run `p2_tables.py --check`, `tables.py --check` and `test_release_audit.py`. Export PDFs once at 19:30. Final codex review of glance + abstract + P2.8 + P2.11 on Sun ~13:00, then freeze numbers by 14:00.

## STOP doing
- **Running two writers on one dataset, or any ad-hoc `for i in …` relaunch loop alongside a queue.** One queue owns each dataset.
- T=80 replay (dropped, directive 3a). New E43/E45/E54 work. New scripted conditions.
- More qwen/glm *variants* (other gateway models, extra lever combos) before E61 base/abliterated and E63 have each produced a clean, deduplicated set.
- Interim Part C write-ups per partial dataset. Write P2.11 once at the checkpoint from `p2_partc.py`, and once at the end.
- Growing REPORT.md (945 lines). New text replaces old text: when P2.8 lands, delete the pilot paragraph; don't append to it.
- Exports/PDF except Sat 19:30 and the Sun 16:30 window.

## Cross-pollination
- **From Q2.2 → here:** (a) **Strong-framing tacit collusion** (E97 pilot: luna none-arm market 16.3 vs Nash 10–13; pair premium ≈ 0 in every run; the high price is market-wide). It matches your E60 spillover and P2.4 all-firm cartel (pair_level AUROC 0.26). Cite it as the LLM instance of "relative screens miss market-wide elevation". (b) **E92 logbook:** a notepad with *weather* entries gives only +0.22, against +1.04 for a pricing notepad. Content, not structure, drives the level effect. Update takeaway 4 to say "pricing deliberation", not just "singled out by the prompt". (c) **mimo-v2.5 (older model, interim):** no-channel markets at 15–17 ≥ private 13–16, so older open models are also tacitly high. Cite this when you report glm/gpt-5.6-luna. (d) Q2.2's `llm_p2strongF` is your best executed-collusion dataset (directive 3d).
- **From here → Q2.2:** E59 deepseek public board (+0.70, does *not* reach their 17.0 → the market/framing differs); E60 spillover; P2.4 cost asymmetry (cited in their gap 7, `llm_p2asym`); E44 verdict + decay; your frozen-detector read of `llm_p2strongF` (directive 3d).
- **Merger sentence (both REPORTs, verbatim):** "Detectability of LLM collusion by any price statistic is a property of the (seller model × prompt) pair. Relative screens survive a shared model but fail under market-wide spillover; absolute screens need model- and prompt-matched references." Add a second shared sentence once Part C lands: "With memory and a profit objective, LLM sellers raise prices market-wide without any channel; executed (kept) agreements are rare (X/Y), and channel labels stop being ground truth."

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
→ **IN PROGRESS.** Executed rates on existing sets DONE (luna llm_v1 6/16, llm_long 3/8, deepseek 2/15; P2.11 stub). E63 luna memory pilot queued after E44 (keep, 5 + 5); qwen memory pilots queued after E61. **Re-scoped** (directive 3): full own-market arm only if the pilot meets the rule by Sat 17:00. Otherwise, the dependence-detector evaluation runs on Q2.2's `llm_p2strongF` (20 + 20, T=40) plus E44 T=60 by behaviour class. Add the tacit rate in A (directive 4).

**C2 Older / weaker models as sellers** (model-generation lever: does collusion and its detectability
change across model generations?). Available and verified working 10:25 UTC:
- codex: `gpt-5.6-luna`, `gpt-5.6-sol` (previous generation) — `llm.chat(..., backend="codex", model="gpt-5.6-luna")`
- OpenCode Go: `glm-5.2`, `mimo-v2.5` (older open models) — `backend="go"`; Go is shared/slow, keep runs small.
NOT available: gpt-5, gpt-4o. **WARNING:** llm.py's codex backend silently falls back to gpt-6-luna when a
model name is unknown or limited — always check `r["model"]` and exclude/flag fallback runs.
Split: Q1.4 runs gpt-5.6-luna + glm-5.2; Q2.2 runs gpt-5.6-sol + mimo-v2.5. ~10–15 runs per model (A vs C
matched seeds), base prompt. Report per-generation: agreement rate, execution rate, markup, detector AUROCs.
Combine with C1 if a model executes collusion more readily (older models may comply/coordinate differently).
→ **IN PROGRESS.** E62 declared. gpt-5.6-luna (10 + 10) queued after E44 in `llm_queue_p2c.sh`: keep. glm-5.2 on Go generating slowly (empty-reply retries, max_tokens 4000): report the n available at Sun 12:00. Check `gt.model` on every run (fallback guard).

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
→ **IN PROGRESS, partly blocked.** E61 declared. qwen-base `llm_qb_p2`: 4 unique games at 11:36, **corrupted by a double writer** (directive 1). Abliterated `llm_qa_p2`: 0 games, endpoint unreachable since 11:00; deadline Sat 14:00 (directive 3e). Extra gateway models: **not now** (STOP list).

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
  → **DONE** (E46, REPORT P2.1). CUSUM / matched-reference rows **DROPPED** (low value, no change to the reading).
- **Independent reimplementation check:** have codex (gpt-6.1-sol, `-s workspace-write` in a scratch dir,
  given ONLY the REPORT's method description, not your code) reimplement your headline statistic(s); compare
  numbers on the same data. Report agreement; fix any bug found (and re-state affected numbers).
  → **DONE** (E47, P2.2: 422/424 cells < 1e-9, all 20 AUROCs identical, no bug).

## Gaps owned by THIS repo (Q1.4), in priority order (status as of 11:45 UTC)
1. **Prompt-wording robustness** (validity threat; you already saw the JSON-anchor effect). 3–5 prompt
   variants of your seller prompt (paraphrased instructions, different JSON template / no example,
   different order of information, reasoning on/off). Does the C − A markup and the level-vs-pCMI pattern
   hold across variants? Report variance across variants as a robustness band.
   → **DONE** (E43, P2.7; takeaway 3 reconciles with Q2.2 E78). Frozen.
2. **Long LLM games**: settle whether pCMI fails for lack of data. ≥ 20 runs per condition (A, C, plus D if
   budget) at T = 60–100. Power-vs-T curve on LLM data (subsample prefixes). This is the decisive 1.4 result.
   → **IN PROGRESS** [priority 2, decisive]. E44 30/40 at 11:36, ETA ~12:30–13:00 → `scripts/e44_post.sh` + executed/tacit classification (directive 2). D dropped. **T=80 replay DROPPED** (codex is the bottleneck; T=60 is the declared primary).
3. **Same-model confound as a headline**: in real deployments everyone runs the same few models. Quantify
   on LLM data: same-model no-channel pairs vs mixed-model pairs vs colluding pairs. Test mitigations
   (same-model surrogate null; conditioning on lagged prices of all firms; model-matched reference
   markets). State plainly what a deployer can and cannot conclude.
   → **DONE** (E48 + E54, P2.3). One mechanical step left: final E54 pool with the E44 A prefixes (inside `e44_post.sh`). Then freeze.
4. **Second seller family** in your market: deepseek (Go) sellers, ≥ 15 runs each for A and C (T=20 or
   longer). Does the channel markup and the detector pattern replicate across families?
   → **DONE** (E45 + E58 judge + E59 public board, P2.9). Frozen.
5. **Coalition structure**: 3-of-4 colluding and all-4 colluding (scripted + small LLM set). Pairwise
   net-influence relies on clean comparison pairs — show where it breaks and test a group-level statistic
   (e.g. multi-information / total correlation of the coalition vs surrogates).
   → **DONE (scripted)** (E49, P2.4). Small LLM set **DROPPED** (needs a new channel design). LLM analogue = E60 spillover + strong-framing tacit markets (directive 3d).
6. **Collusion onset / detection delay**: collusion that starts at round k (scripted switch; LLM channel
   opened mid-game). Rounds-to-detection for level screen vs pCMI (CUSUM-style sequential version of the
   level screen is a good addition).
   → **DONE (scripted)** (E50, P2.4). LLM mid-game channel **DROPPED** (codex budget).
7. **Market-model robustness**: N = 2 and 6 sellers, and a different demand elasticity; do the scripted
   calibration (FPR) and power results hold?
   → **DONE** (E52, P2.5).
8. **Cost asymmetry hard negative** for the dependence detectors (firms with unequal private costs).
   → **DONE** (E51, P2.4). Keep it in the abstract; Q2.2's LLM version (`llm_p2asym`) cites it.
9. **Non-price collusion (exploration)**: one condition of market/customer splitting or bid rotation —
   simplest: run the starter double auction (`~/collusion/collusion_hackathon/llm-agent-collusion`, via our
   llm.py — it needs adaptation since it expects a Nebius/OpenRouter key) or a quantity/territory variant
   of your sim; check which detectors see it at all.
   → **DONE (scripted bid rotation)** (E53, P2.6). Starter double auction **DROPPED** (adaptation cost).
Items 1–4 must be done by Sat 20:00 if at all possible; 5–9 by Sun 15:00.

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
- **D2 Double auction** (owner: Q1.4). Starter `~/collusion/collusion_hackathon/llm-agent-collusion`
  (Agrawal et al. 2025, continuous double auction; 3 sellers + 3 buyers, seller communication optional). Copy the
  code into this repo (don't modify the starter), and write a small adapter so its model wrapper calls our
  `llm.chat` (it expects a Nebius/OpenRouter key; route to codex luna/sol, Go deepseek, or the Aqueduct gateway
  qwen-3.6-35b — record the model per run). Conditions: seller communication on vs off, ≥ 15 + 15 runs. Apply
  the frozen level screen, pCMI and dependence detectors on seller ask series. Does price-level-not-dependence hold
  in a different market mechanism?
- **D3 LLM trust-breaking** (owner: Q2.2, lowest priority of the three). Starter
  `~/collusion/collusion_hackathon/llm-trust-breaking` (private plans, public announcements, actions, outcomes in
  repeated games). Measures promise-breaking, NOT collusion — use it only to validate our say-vs-do machinery
  (claim–action consistency table, text-vs-action auditors) on someone else's data. Same adapter approach;
  small n (~20–40 trials) is enough.

Budget: D1 is auditor calls only (sol, ~1–2k calls); D2/D3 generation can use the Aqueduct gateway (45/min cap
handled by llm.py) or codex luna. Register each in EXPERIMENTS.tsv first; write each up once as a short
"External validity" subsection (≤ 15 lines + 1 table).

