> **PHASE 2 STARTED 2026-10-24 06:45 UTC** - v1 frozen as tag v1-overnight. New experiments are OPEN again; work queue = DIRECTION.md gap list. Ignore older no-new-experiments / finalize notes below.

# STATUS (updated 2026-10-24 ~06:50 UTC, Phase 2 iteration 1)

**Phase 2 running** (DIRECTION.md gap list). v1 frozen at tag `v1-overnight`; REPORT now has a "Phase 2 results" section under the key-findings table.
**Generating (background, logs /var/tmp/c14/):** `scripts/llm_queue_p2.sh` (codex, 5 workers): E43 prompt variants llm_p2_{v0,para,template,order,noreason}
(A/C × 6, T=20) → E44 llm_long_p2 (A/C × 20, T=60, staged 10 then 20) → `scripts/llm_queue_p2b.sh` extends the same games to T=80 by cache replay (T=60 copy kept as data/llm_long_p2_T60 = primary). `scripts/llm_queue_go.sh`: E45 llm_ds_p2 deepseek-v4.1-flash (A/C × 15, T=20).
Throughput: codex ~0.4 calls/s → variants ≈ 3 h, long ≈ 6–7 h (done ≈ 16:30 if the rate holds); Go is shared with the sibling and slow.
**Fix:** deepseek-v4.1-flash on Go returns "" (reasoning > 4k tokens) unless `thinking: disabled` → llm.py patched. **The sibling's llm_p2ds run has the same bug (its Go calls show out_chars 0) — director, please tell it.**
**Done this iteration:** E46 precision at prevalence (REPORT P2.1): at 1% prevalence every flag has precision < 0.25; pCMI on LLM ≈ base rate.
**Done:** E47 independent reimplementation (codex, REPORT text only): 234/236 per-run scores identical (<1e-9; 2 = ρ² cap on perfect fits), 20/20 AUROCs identical, pCMI shift flags A 4/21 vs 5/21 (MC). No bug. REPORT P2.2.
**Running (codex gpt-6.1-sol, worktree /var/tmp/c14/wt_p2s, branch p2-scripted, spec /var/tmp/c14/p2s/TASK.md, log codex.log):** scripted gaps 5/6/8 on DEV seeds 200–299 —
coalition 3-of-4/4-of-4 + Gaussian total correlation (`score_groups`), onset k∈{25,50} + level CUSUM vs expanding-window pCMI, cost asymmetry hard negative;
defaults must stay byte-identical (compat check in its REPORT_codex.md). Nothing merged yet.
**Next:** (1) review codex's p2-scripted diff + REPORT_codex.md, merge, declare locked seeds (e.g. seed0 2001–2003) in SPLITS + ledger, run test once → REPORT P2.x;
(2) when all 5 arms are done: `uv run python scripts/p2_variants.py --run-eval` (frozen evaluator + per-arm C−A markup/AUROC + declared E43 verdict; script reproduces llm_v1 C−A +1.76 [1.22, 2.31]) → REPORT P2.3;
(3) llm_long_p2: `uv run python -m experiments.llm_eval eval --name llm_long_p2_T60 --Ts 10,20,30,40,50,60` (new --Ts flag); (4) gap 3 same-model mitigations on llm_mixed2/llm_v1; (5) gap 7 (N=2/6, elasticity: detectors hard-code 4 sellers);
(6) gap 9 non-price (exploration). ETAs at 0.83 codex calls/s: variants ≈ 08:20, long T=60 ≈ 11:35, T=80 ≈ 12:40; deepseek (Go ~0.08/s) ≈ 15:00.
**Risks:** codex throughput; Go contention; E44 may not finish 20+20 before 20:00 (n=10 stage first).

# STATUS (updated 2026-10-24 06:07 UTC, iteration 28)

**Current:** E42 core LLM reproducibility audit running; no new experiments, tuning, seller or judge calls. Scripted results frozen.
**Headline:** level AUROC 0.87/0.98 in the two LLM markets; pCMI 0.45/0.52. T=50 and same-model comparisons remain underpowered.
**Calibration:** scripted pCMI common-shock FPR 14% (shift null); 4% on held-out policy + shock (surrogate); shared-seed confound remains.
**Exploratory:** placebo/delivery mechanism unresolved; first sender already has a provisional premium (+0.94 [0.38,1.59], descriptive).
**E41:** table checking covers headers + 404 body cells of all 11 quantitative results tables; 22 late-analysis/render outputs reproduced.
**E42:** --core-eval adds frozen primary evaluators (v1/long/mixed2/external v3) and trend/incremental diagnostics, requiring seven additional byte-identical outputs.
**Verified:** llm_v1 evaluation JSON byte-identical (972 s); long/mixed/external/diagnostics pending. Eight tests pass; Codex static review found no material issues.
**Exports:** refresh after REPORT §6 and ledger updates; prior report/deck exports remain from E41.
**Next:** finish core audit, preserve evidence, regenerate exports, run final release check, commit and push. No new experiments.
**Finalization:** at 08:15 run tables.py --check, headline_fig.py, slides.py, export_pdf.py LAST; verify_release.py --export checks a disposable copy.
**Risks:** small LLM n, OpenAI-family sellers only, no own-market placebo; surplus dependence is not proof of an agreement.

## Log
- P2 iter 1 06:27–06:55: prompt-variant switch in sim/llm_market.py (v0 byte-identical, 96 combos checked); E43–E45 declared then amended (throughput) before any result; queues launched; deepseek empty-output fix; E46 prevalence; reimpl check launched.
- 20:24 smoke test ok.
- iter 1 (~20:25): built sim/market.py, detectors, experiments/scripted.py, gate dataset (no STATUS update).
- iter 2 20:28–21:16: fixed null calibration (old Bonferroni with B=100 could never reject); gate passes; sweeps
  + figures; codex built sim/llm_market.py; pilots showed gpt-6-luna stuck at 12 → wide grid, private costs,
  reasoning, hybrid mode, explore hint (none helped) → found JSON-example anchor, removed → collusion appears.
  Codex methods review (/var/tmp/c14/review_methods.md, key points in STATUS next-steps) → revised null,
  realistic shared policy, Wilson CIs, held-out gate v2. Launched llm_v1.
- iter 3 21:15–21:50: SPLITS + ledger; dev pCMI design test (inter discarded); control-surrogate null added to
  scripted + llm eval; locked test gate run; hard-negatives figure with both nulls; llm_eval: msg-timing fix,
  CD_ambiguous, dev/test groups, pair_level/market_level baselines, mixed-model analysis; sim --mixed-tier.
- iter 3 21:50–22:00: locked test sweep, Opus review + fixes, LLM analysis plan declared in REPORT §4.3, queue script.
- iter 4 21:54–22:15: queue healthy (20/64). Wrote experiments/llm_report.py (tables+figures for §4.3), verified on llm_pilot4; no llm_v1 detector peeking. Codex REPORT-claims review deferred until LLM results land.
- iter 5 21:57–22:30: E12 baseline fix + within-family/paired AUROC in llm_eval/llm_report (before llm_v1 eval); E13 ext_llm_v3 provisional; ledger hashes; §5 n fix; codex review → E14 fixes; ext rerun at n=70; experiments/llm_fig.py (figures/llm_auroc_both.png).
- iter 7 22:49–00:00: E16 mixed-eval CI; found backend drift (E17) → killed queue, queue2 with codex pinned; llm_v3 final n=125 → REPORT §4.3, figure.
- iter 6 22:34–22:52: scripts/tables.py (sonnet worker; verified), ext_llm_v3 rerun n=74 → REPORT, T=10 scripted top-1 as nearest positive control, E15 co-movement diag.
- iter 8 00:04–00:45: waited for queue2; llm_v1 label+eval done 00:26 → llm_report, llm_fig, REPORT §4.3 llm_v1 results + abstract LLM sentence (E18); ledger hashes filled; codex review of the new text started.
- iter 8 00:45–01:15: codex review of llm_v1 text (numbers all OK; P0s on inference: incremental-value untested, surrogate pool per family not pooled, 'flat vs T' false) → E19 diag_llm_v1 (incremental logistic + detrend/diff) → §4.3 + abstract rewritten accordingly.
- iter 9 01:02–01:10: E20 declared; §4.4 umbrella; Opus claims review applied (P0s + limitations).
- iter 9 01:10–02:15: llm_long label+eval (I accidentally pkilled the queue's eval and reran it) → E20 final in §4.3 (v); found E21 mixed-tier bug, fixed, llm_mixed2 launched.
- iter 10 02:17–02:26: llm_mixed2 finished + evaluated → §4.3 (iv), abstract sentence; scripts/mixed_price_by_model.py; codex claims review → E23 edits.
- iter 10 02:26–02:29: tables.py mixed(); Opus coherence review → E24 edits.
- iter 10 02:29: §4.3 restructured into subsections (no number changes).
- iter 11 02:58–03:12: figures/llm_mixed2_same_vs_cross.png (scripts/mixed_fig.py) → §4.3.5 + §6; table lint OK; no new LLM batch (directive 4); E25 number audit + fixes.
- iter 12 03:01–03:40: E26 clean-clone regeneration (all byte-identical), data/ext_llm_v3 snapshot, README.md, §6 note.
- iter 13 03:37–04:00: E27 headline Figure 1 + codex judge-clarity edits (no number changes).
- iter 14 03:39–04:20: E28 Opus judge-read + final codex claims review applied (no number changes; figures relabelled).
- iter 15 04:12–04:22: E29 talk deck (scripts/slides.py → PRESENTATION.md), codex deck review + Opus judge-read applied, §4.4 sibling replication number.
- iter 16 04:18–04:50: E30 injection MDE (scripts/injection_mde.py → results/eval/injection_mde.json), REPORT §4.3.8 + abstract clause; codex review of §4.3.8 → single-planting AUROC + game-cluster bootstrap, wording softened.
- iter 17 04:26–04:30: regen check clean; slides.py E30 bullet + computed binomial p; Opus judge-read (results/reviews/opus_judge_read_iter17.md) → abstract/§4.3.8/deck wording fixes (E31).
- iter 18 04:30–04:40: E32 sibling replication+placebo with frozen detectors (scripts/placebo_rep_ext.py, data/ext_llm_v3{rep,plc} snapshots) → REPORT §4.3.9, §7, abstract clause, deck bullet; codex review (results/reviews/review_e32_codex.md) applied: randomisation p for tie-averaged hits, paired AUROC CI, no-equivalence wording, module state restored.
- iter 19 04:40–04:52: E33 regen check + codex final claims review + Opus consistency review → wording fixes in REPORT/README/deck (slides.py).
- iter 20 04:52–05:10: E34 REPORT §8 related work/references; codex citation review applied; tables.py still runs.
- iter 21 04:55–05:00 (VM clock): hygiene (ledger hashes, figures exist, tracked 37 MB); E35 declared (8b2e726) then computed; §4.3.10; codex review applied.
- iter 22 05:00–05:15: E36 key-findings table in REPORT, numbers verified vs JSON; README snapshot list; regen check clean.
- iter 23 05:05: E37 offline exports (scripts/export_pdf.py -> REPORT.pdf/.html, PRESENTATION.pdf); no results changed.
- iter 24 05:05–05:27: E38 consistency review + fixes; PDFs re-exported.
- iter 26 05:43–05:58: E40 short abstract + codex check; PDFs re-exported.

### 2026-10-24 — archived iteration-26 current-state summary

**All declared analyses DONE** (§4.3 (i)–(v) filled). Scripted half done; LLM: llm_v1 (E18/E19), llm_v3 ext (E13), llm_long (E20), llm_mixed2 (E22).
Level stats run AUROC 0.87/0.98/0.95; pCMI 0.45/0.52/0.45. pCMI adds nothing detectable to markup. T=50 does not meet rescue rule (CI wide).
llm_mixed2: same − cross pCMI +0.003 [−0.025, +0.032] → no detectable same-model excess.
Reviews applied: E23–E28 (codex claims ×2, Opus coherence + judge-read, number audit, clean-clone regen, Fig 1).
**E29 (iter 15):** 6-slide talk deck `PRESENTATION.md`, generated by `scripts/slides.py` from results/eval JSON (no hand-typed
numbers); codex deck review + Opus judge-read applied; linked from README + REPORT §6; §4.4 now quotes the sibling replication (premium 0.92, n=30).
**E30 (iter 16, exploratory, no LLM calls):** planted shared ±1 price offsets into real LLM controls → pCMI single-planting AUROC 0.93 at q=0.2, T=50 (top-1 0.99; T=20 only 0.64),
real channel pairs' co-move excess −0.008 [−0.023,+0.009] (llm_long) → consistent with level reading, not settling; REPORT §4.3.8 (codex review applied: paired cluster bootstrap, softened).
Deviation from DIRECTION ("stop scripted runs"): this is not a scripted sweep; it is analysis on existing LLM data that addresses the one open question in the abstract.
**E31 (iter 17):** regen check clean (tables/slides/headline_fig); deck gets E30 bullet from JSON; Opus judge-read applied to abstract/§4.3.8/deck (all numbers matched JSON; title kept).
**E32 (iter 18, exploratory, no LLM calls):** frozen detectors on sibling llm_v3rep (30) + llm_v3plc placebo (15, matched seeds, msgs undelivered) →
replication holds (pair_level .88, pCMI .50); pair_level localises placebo pair 13.5/15 vs 14/15 → level screen is offer-driven; MI first-diff 10/15 vs 3/15
(sign-flip p=.065, Bonf ~.52) suggestive only. REPORT §4.3.9 + new §7 "What to do next"; codex review applied. Addresses the "no placebo" risk (sibling market only).
**E33 (iter 19):** regen check clean; codex final claims review + Opus consistency review after E32 applied (one numeric typo 0.64→0.63; title/§4.1/§4.3.7/§4.3.9/§4.4/§5 softened or scoped; deck + README synced with placebo results).
**E34 (iter 20):** REPORT §8 related work + references (15, from starter literature list; codex citation review applied, 7 P1 wording fixes).
**E35 (iter 21, exploratory, no LLM calls):** frozen detectors on sibling llm_v3mon (monitor) + llm_v3fp (firm framing): channel offered, 0/30 agreements →
pair_level localises 3.3/30 (chance 5.0) vs placebo 13.5/15 → declared rule "contradicted" for the mere-offer reading; consistent with "level premium needs
attempted coordination", framing confounded. REPORT §4.3.10 + abstract/README/deck one sentence; §7 item; codex review applied (wording only).
**E36 (iter 22):** judge-facing 'Key findings at a glance' table (7 rows) under Fig 1 in REPORT; every number copied from abstract and re-checked against results/eval (llm_v1_report, llm_v3_ext_report, llm_long_report, llm_mixed2_mixed.json, placebo_rep_ext_report); README data row lists all 5 sibling snapshots; tables.py + slides.py regen clean (deck unchanged).
**E37 (iter 23):** offline exports for the talk: `REPORT.pdf` (18 pp), `REPORT.html` (self-contained), `PRESENTATION.pdf` (6 slides) via
`uv run --group export python scripts/export_pdf.py` (checks headings/table cells/slide titles survive into PDF text; pages inspected). README + REPORT §6 link them.
**E38 (iter 24):** codex whole-document consistency review after E35–E37 (results/reviews/codex_consistency_iter24.md): 3 P0 (offer-vs-agreement contradiction §4.3.9/§4.4, shared-seed range 44–100%, MI C-vs-A inverse), 4 P1, 1 P2, all applied; tables.py unchanged; slides + PDFs regenerated.
**E39 (iter 25, exploratory, no LLM calls):** sibling found round-1 prices alone give AUROC .90 → our analogue: cache-only replay (40/40 exact)
recovers pre-play provisional prices (`data/*/preplay.jsonl`). First sender (no partner msg read) − rivals r0: +0.94 [0.38,1.59] (llm_v1) vs whole-game +0.45;
llm_long +2.19 [0.56,3.94]. Codex P0 (pre-play sequential → first-sender split) + Opus review (first sender's price = its own proposal → fits willingness-to-coordinate, §4.3.10 reconciled) applied; descriptive, not causal. REPORT §4.3.11 + abstract/table row 8/§5/§7.
**E40 (iter 26):** new short judge-facing abstract (~300 words) in REPORT; the old 700-word abstract kept verbatim as '### Detailed summary'. Numbers copied from it; codex review (results/reviews/codex_short_abstract_iter26.md) 3 P1 applied (14% is the common-shock set; +1.8 is llm_v1 only; 'at chance' → 'not distinguishable', mechanism unresolved). tables.py clean; PDFs re-exported (REPORT 20 pp).
(Note: iter-20 header timestamp 05:10 was ahead of the VM clock; real ~04:50.)
**Next:** no new experiments (E39 was the last; nothing else worth starting before the 06:30 cutoff). At 08:15: re-run tables.py, headline_fig.py, slides.py,
then export_pdf.py LAST (PDFs must match final REPORT/PRESENTATION .md); check README renders; push.
**Risks:** low n everywhere on LLM; only OpenAI-family sellers; no placebo arm in llm_v1 (placebo only in sibling market, n=15).

- iter 27 (2026-10-24 05:57 UTC): E41 reproducibility audit (DIRECTION directive 5, no experiments/tuning/LLM calls). Added exact quantitative-result-table render/check, saved-data disposable-copy release check, and six failure-path tests. Initial audit caught stale deck ledger range E39 vs E40; retained results/release_audit_initial_iter27.json, refreshed deck to E41. Later E30/E32/E35/E39/descriptive JSON and figures reproduce byte-identically (21 outputs); REPORT/README reproduction instructions now include E39, stored preplay input, and the cache-only provenance boundary. Fixed three display discrepancies only; escaped Pearson pipes in generated supporting tables. Codex review results/reviews/codex_repro_iter27.md: no remaining material issues (sweep constant check strengthened during review). PDF exporter now fails on missing text/page count/overflow; refreshed report/deck exports, inspected report p18 and slide 6. Final rerun also checks HTML bytes and horizontal slide overflow. Previous current-state summary moved below the append-only log to restore the <=15-line top-section rule.

- iter 27 completion (2026-10-24 06:00 UTC): final committed-code release audit PASS (results/release_audit.json, source 5952bdb): 22 files byte-identical, 15 snapshot checksums, 14 local links, all 11 result-table headers/404 body cells, REPORT HTML byte match, PDF 25 headings/520 table fragments and six slides/titles, vertical + horizontal slide overflow checks. Six audit failure-path tests pass. No seller/judge calls or new experiments; the independent Codex code review used one reviewer invocation. Code milestone 5952bdb pushed; final evidence/status/ledger update committed next.

- iter 28 started (2026-10-24 06:07 UTC): E42 extends director directive 5 from late-analysis/render reproduction to the primary frozen LLM evaluations. `verify_release.py --core-eval --recompute --export` runs in a disposable copy, using stored trajectories and labels (no generation/judging/tuning); core scores/prefix CIs and diagnostics must match seven saved files byte-for-byte. Eight audit tests pass, including new ordering/isolation/mismatch cases; independent Codex review (`results/reviews/codex_core_repro_iter28.md`) found no material issues. Runtime core verification is in progress; E41 evidence preserved in `results/release_audit_iter27.json`. REPORT §6 and README document the new option.
