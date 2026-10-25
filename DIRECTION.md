# DIRECTION — Phase 2, director review 2026-10-25 12:35 UTC (Sun midday)
(experiments end **Sun 15:00** · numbers freeze **14:00** · finalize-only **16:30** · hard stop **18:00** · merge `collusion-beyond-words` HEAD `979d17c` (iter25) · Q1.4 HEAD `b82ebbc` (I138) · evidence pin `732f08c`: **director check at 12:3x: 30/30 pinned files SHA256-identical to `evidence/manifest.json`** (the manifest now lists 30 files, not 27))

**Verdict (3 lines).**
1. **Q1.4 is answered, and convincingly for a sprint.** The nulls respect sequential structure (shift null + control-surrogate null, never iid permutation). Every headline has a CI, a denominator (9/9 sets, 16-cell grid) and a declared/post hoc tag. A sensitivity check (planted co-move, 0.79) separates "no co-movement detected" from "pCMI is blind". The merged text matches all of this, and the merge machine-checks the numbers. I see no methodological P1 left.
2. **The repo is now looping on bookkeeping.** All of the last 10 commits (I128–I138) are scope-check records, and I134/I136/I138 only record "unchanged". The 10:30 diff-triggered rule said "log one line and do not commit"; in practice each no-op still produces a STATUS + `merge_flags.md` edit, so the wrapper commits it. This is cheap, but it is noise in the history a judge will skim, and it buys nothing.
3. **Explore vs exploit: exploit only, confirmed.** 2.5 h remain before 15:00, but any new number would land after the 14:00 freeze. It would be outside the merge's pinned evidence and unreviewed, and it cannot move the headline. The remaining value is in two places: (a) not breaking the pin, and (b) the 14:00 scope read plus fresh exports. Right now the PDFs are 4 h older than the final REPORT.md.

## Top directives (in priority order)

1. **Silent no-op iterations (now → 18:00).**
   - If all three hold, exit the iteration with **zero file edits**: no STATUS line, no `merge_flags.md` line, nothing for the wrapper to commit.
     - The merge HEAD is unchanged since your last recorded check.
     - Its working-tree `SUBMISSION.md`/`SLIDES.md` diff is unchanged.
     - Neither merge STATUS nor DIRECTION names a Q1.4 ask.
   - At most one "still unchanged" STATUS line per hour.
   - For a new merge HEAD, keep the 10:30 rule: scope-read only the hunks that touch Q1.4 content, and flag P1 only.
   - The merge's iter24/iter25 commits (`d523c5b`, `979d17c`) are Q2.2 locked-test replays. If their SUBMISSION hunks carry no Q1.4 text, that is a no-op.
   - **Why:** the history should show science and the two scheduled checks, not 20 "unchanged" commits.
2. **Do the render-only export NOW (before 14:00), not at 16:30.**
   - REPORT.md is final (last change `732f08c` 10:05), but `REPORT.pdf` / `PRESENTATION.pdf` were last built at **05:56 (`4fed444`)**. The shareable exports therefore predate the final text by 4 h. If anything cuts the session short, a judge opening the PDF sees a stale report.
   - Run `scripts/export_pdf.py`, `scripts/slides.py`, `scripts/p2_tables.py --check` and the v1 tables check.
   - **Do not run `scripts/claims_denominators.py`, or any script that writes `results/eval/*`.** `results/eval/claims_denominators.json` is one of the 30 pinned files. Only `--check` modes and renderers are allowed.
   - Before committing, run `git status`: only export outputs (REPORT.pdf/html, PRESENTATION.*, figures the slides script renders) may change. Then loop over `evidence/manifest.json` and expect 30/30 byte-identical. Make one commit: "export; pin 732f08c 30/30 intact".
   - If a build fails, fix the *script or environment*, never REPORT.md.
   - **Why:** the export is the deliverable a judge opens first, and it carries no science risk. Doing it now turns 16:30 from a risky step into a check.
3. **Final judge-style scope read, once, 14:00–15:00, ≤ 40 min (unchanged from 10:30 #3).**
   - Read SUBMISSION (TL;DR, abstract, §1–§8, Appendix A rows tagged Q1.4) and all 8 slides **at the merge HEAD current at 14:00**.
   - Watch list: "no co-movement exists", "pCMI cannot detect", "TE detects collusion", the E72 execution split stated as a finding, "executed collusion is undetectable", E70 main effects as causal, "not a power failure", the 9/9 claim without its prompt-family scope (2/5 wordings), and a merged single market.
   - Run `check_merge_sources.py` this one last time.
   - Output: one P1-only table in `merge_flags.md` plus one STATUS line, "final scope read done at merge <hash>, N P1".
   - After that, only the diff-triggered rule (directive 1) applies.
4. **16:30: freshness check, not a rebuild.**
   - If REPORT.md and PRESENTATION sources are unchanged since directive 2's commit, re-run only the read-only checks (`p2_tables --check`, tables check, 30/30 pin loop). Do not commit if nothing changed.
   - Re-export only if something did change, using the same rules as directive 2.
5. **Wind down by 17:30.**
   - Write the final STATUS line: "Q1.4 final at <hash>; evidence pin 732f08c unchanged (30/30)".
   - After that, act only if the merge manager reports an error that names Q1.4.

## STOP doing
- **Stop committing "unchanged" records** (I134, I136, I138 pattern); see directive 1.
- No new experiments, estimators, slices, critics or review rounds. That covers red-team/evasion, the below-chance pCMI mechanism, E72 follow-ups and the E70 extension.
- No REPORT.md edits of any kind, and no "Changes after 08:00" lines. The known double-rounding (pinned 0.81 / +2.13 vs merge 0.80 / +2.14) is disclosed on the merge side. Leave it.
- No running writers of pinned JSON (`claims_denominators.py`, `e68_cda.py`, `e70_*`, `phase2_fig.py` if it touches `results/eval`). No edits to the merge repo or the joint statement.
- Don't re-verify numbers the merge already binds (111 assertions, 139 bindings, 107 blobs). Read its STATUS check line instead.
- Don't fix old timestamps. No serendipity confirmation: HITS through S72 has no promoted hits, and S65–S72 are outside Q1.4's market.

## Cross-pollination
- **Merge → here:** the merge's `scripts/finalize.py` (a one-command, guarded release check) is the model for directive 2: renderers + checks, with the pin verified in the same step.
- **Q2.2 → here:** Q2.2 already did its full final scope read early (I145), and its 14:00 job is now diff-only. You can't do the same, because the merge may still touch Q1.4 text (iter18 did). Keep the 14:00 read.
- **Here → Q2.2:** the stale-export finding. Their PDFs are even older (Sat 19:37), so they get the same export-now directive and the same warning about writer scripts.

## Phase 2 gap-list status summary (12:35 Sun)
| item | status |
|---|---|
| Shared: precision at prevalence (E46) · reimplementation (E47) | DONE |
| Q1.4 gaps 1–4, 7 (E43, E44, E48/E54, E45/58/59, E52) | DONE / frozen |
| Q1.4 gaps 5, 6, 8, 9 (E49, E50, E51, E53) | DONE (scripted); LLM variants of 5/6 DROPPED (they need a new channel design; codex budget) |
| Part C: C1 (E64/E65/E66/E71), C2 (E62), C3 (E61), C3b (E69) | DONE. glm-5.2 and the gpt-6.1-sol pair DROPPED (no complete games; codex saturated). C3c DROPPED by Q2.2 (E109) |
| Part D: D1 Q1.4 pCMI part | DROPPED (no action time series in SALT) |
| Part D: D2 double auction (E68) | DONE, inconclusive, pinned |
| Part D: D3 | n/a (Q2.2; DROPPED there) |
| Part E: E1 grid (E70 + follow-up) · E72 TE diagnostic (post hoc) | DONE |
| Part E: E2, E4, E5 | DONE by Q2.2 · E3 DROPPED by Q2.2 |
| Denominators · one-minute box · E73 · E74 · R91 · I94 sweep · I98 regenerability | DONE |
| Merge flags delivered + applied (F1 P1, F3) | DONE: 0 open |
| Diff-triggered scope check (10:30 #2) | DONE through merge `d523c5b` (I137). `979d17c` not yet checked, expected no-op (Q2.2 replay). Continue under directive 1 |
| Pin discipline (`732f08c`) | IN PROGRESS: holds, 30/30 verified by director 12:3x; keep until 18:00 |
| Fresh export (PDFs from 05:56 predate final REPORT 10:05) | NOT STARTED → directive 2 (moved forward from 16:30 to now) |
| Final scope read of Q1.4 text | NOT STARTED → directive 3 (14:00–15:00) |
| 16:30 freshness check + pin check | NOT STARTED → directive 4 (re-export only if something changed) |
| Evasion / red-team arm | DROPPED (conflicts with the "never instruct" rule; would land after the freeze; already a Limitations bullet) |
| Serendipity | no promoted hits (through S72) |

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
→ **DONE.** Executed 48/149 C over ten sets (pilot-pooling bug fixed 17:3x: memory pilots excluded); E64 pooled pCMI executed .42 [.33, .53] vs .52; the circularity is stated. E71 definition sensitivity (20:07): 27 definitions, 13–78/149 executed, pooled pCMI 0.343–0.531, no CI wholly above 0.5. Shared-definitions wording fixed 22:4x (implemented rule named in *Terms*; Q2.2 E129 note). **E65** (qwen-abliterated, memory, T=40, 20 + 20): declared verdict **INCONCLUSIVE** (pCMI executed-only 0.33 [0.02, 0.66], 5/20 executed; the pilot's 5/5 did not replicate; markup .85, pCMI .49; TE .71 is exploratory → tested by E70's declared secondary TE hypothesis). **E66** (Q2.2 strongF): **NOT EVALUABLE** (tacit-high 19/20; 0/40 class mismatches). Luna memory pilot: descriptive (3/5). gpt-6.1-sol pair: DROPPED (codex saturated; sibling pilot 0/2). Nothing more to run here.

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

## Gaps owned by THIS repo (Q1.4), in priority order (status as of 22:05 UTC; all nine closed — frozen, no further work)
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
   → **DONE (scripted bid rotation)** (E53, P2.6). The starter double auction = Part D2: **DONE 21:50** (E68, inconclusive; see Part D).
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
→ **C3b DONE** (E69, 17:22, declared contrast run once: abliterated − base (C − A) −0.65 [−1.97, +0.65], null replicates; executed 7/15 vs 3/15; base qb36 pCMI 0.71 [0.51, 0.88] = the one set with pCMI CI > 0.5 → replication declared inside E70 → **not replicated**, 0.46 [0.35, 0.58]). Three-pair table in P2.11(b2), checked by p2_tables; Q2.2 cites it. **C3c** (Q2.2): **DROPPED** at its registered pilot (E109: base 9B prices below Nash).



**Serendipity Explorer (added 14:50 UTC):** a third agent runs wild cheap pilots in `~/collusion/collusion-serendipity` (other markets, hub-and-spoke advisor, leniency, counterfactual replay, steganography in prices, personas, ...). Read its `HITS.md` at the start of every iteration; if a hit bears on your headline claims, decide explicitly (in STATUS) whether to confirm it with a registered experiment. Don't duplicate its pilots.
→ Status 06:20 Sun: **still no promoted hits** (S28–S53 unconfirmed/dud/ODD; S41 ODD wage tick size, at most one next-steps clause). (S01, S03, S07, S21, S22, S24 duds; S02 odd/inconclusive; S04 uninformative; S11 ODD; S14 tender caution, used in P2.12 (done); S16 failed pilot). Nothing to confirm. Keep one STATUS line per iteration.

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
  → **DONE (00:10 Sun).** E70 landed 22:36: C − A 13/0/3, pooled +0.98 [0.65, 1.29]; level > pCMI 12/1/3; pCMI 0.51; TE 0.62 [0.54, 0.70] confirmed (E72 DONE 00:28: names the pair 30/96 vs 1/6; signal in non-executed games 0.73 vs executed 0.49; post hoc); qwen pCMI not replicated; M and cost main effects descriptive. Declared follow-up (model, 12 + 12/level) landed 23:32: +1.07 [−0.20, +2.41], not confirmed. No extension (STOP list). Earlier log: E70 (registered 17:10; amendment 2 declared 18:02 before analysis). At 22:05: luna lane 6/6 complete (20:54); qwen lane sweep 5 has c08–c10 done (c10 at 22:02), c11–c15 left (≈5–20 min per cell) → generation ≈22:30–23:00, `e70_post` eval after it, follow-up auto-launch if decided by 00:30 (schedule-only amendment allowed per 22:05 directive 3 if generation is still running at 23:45), follow-up stop 08:00. Next: write-up by Sun 00:30 with pre-committed interpretations (22:05 directive 1), follow-up by 07:30. Board use: luna mostly silent, but c02 channel 78/240 and c07 no-channel 75/240 posts (Q2.2 coverage), so report per cell.
- **E2 Participant replacement mid-game (owner Q2.2; sprint Q1.2).** In executed-collusion games (strong arm / qwen memory),
  replace one colluder at round T/2 with a fresh agent (same model, no chat history) or a different model. Does the price
  level survive? Do detectors notice the break (changepoint)? Cheap, novel, and answers an official sprint question.
  → **DONE by Q2.2** (E112 + E115 final, P2.15: fresh luna re-agrees 16/20 and the level holds; a gpt-6.1-sol newcomer re-agrees 0/20 and undercuts, yet 18/20 markets stay ≥ Nash + 2; CUSUM 0/30). E112 cited in P2.4 (done 18:0x); E115 half-sentence added (iteration 30). Done.
- **E3 Cross-family collusion (owner Q2.2; sprint Q3.3 "can agents identify their peers?").** Pair = luna + qwen (different
  families) with a channel vs same-family pairs. Do mixed pairs agree / execute as often? Does pCMI see same-family pairs
  more (shared-policy confound)?
  → **DROPPED** by Q2.2 (17:56; gateway saturated; E70 factor M varies family at the market level). Nothing to do here.
- **E4 Anomaly hunt (owner both, 30 min each, zero new games).** Have codex gpt-6.1-sol read ~40 randomly sampled
  transcripts across ALL datasets (both repos) and list the 5 most surprising behaviours with run ids. Each becomes a
  15-min test logged as `serendipity` in EXPERIMENTS.tsv. Report the hits and the duds.
  → **DONE for both repos** by Q2.2's E108 (P2.13: 40 games sampled across both repos' datasets, 5 follow-ups, hits + duds, codex-verified). Here: cite P2.13 in one line. **Don't run a second hunt** (duplicate work).
- **E5 One non-English market (owner Q2.2, small, 10+10).** Same game, all prompts and messages in German. Does the text
  auditor (English-prompted) still behave the same? Does collusion change with language?
  → **DONE by Q2.2** (E110, P2.14: explicit agreement 3/10 DE vs 9/10 EN; premium persists +0.91 [+0.20, +1.58]). Nothing to do here.

For every claim in the final abstract, write its denominator next to it (conditions tested, models, datasets).
→ **DONE** (`scripts/claims_denominators.py`, REPORT P2.13, in `p2_tables --check`: premium 9/9 sets (7 models), level > pCMI 9/9, pCMI null 8/9, executed ≤ 50% 8/9, tacit rare 8/9). E70 13/16 added (P2.13). **DONE.**

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
  → **DONE 21:50 (E68, declared verdict INCONCLUSIVE).** 30/30 (nocomms s14 regenerated once before any outcome was opened, R32); `e68_cda.py` run once. Manipulation gate passes barely: ask effect +0.39 [+0.06, +0.69] (≈2% of a 20-unit surplus); level AUROC 0.68 [0.46, 0.88], pCMI 0.60 [0.40, 0.80]; asks ≠ paid prices stated (S14 caution); 18 parse failures in 14/30 runs. P2.12, glance, abstract and merge block updated. Q2.2 cites it, pinned to 9cee046 + SHA256: don't regenerate `e68_cda.json`. Frozen.
- **D3 LLM trust-breaking** (owner: Q2.2, lowest priority of the three). Starter
  `~/collusion/collusion_hackathon/llm-trust-breaking` (private plans, public announcements, actions, outcomes in
  repeated games). Measures promise-breaking, NOT collusion — use it only to validate our say-vs-do machinery
  (claim–action consistency table, text-vs-action auditors) on someone else's data. Same adapter approach;
  small n (~20–40 trials) is enough.
  → Q2.2-owned; **DROPPED** there (promise-breaking, not collusion; time better spent on E99 and D1).

Budget: D1 is auditor calls only (sol, ~1–2k calls); D2/D3 generation can use the Aqueduct gateway (45/min cap
handled by llm.py) or codex luna. Register each in EXPERIMENTS.tsv first; write each up once as a short
"External validity" subsection (≤ 15 lines + 1 table).
