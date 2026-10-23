# DIRECTION — set by research director, 2026-10-23 22:00 UTC
Deadline 09:00 UTC; **finalize-only from 08:15** (no new experiments after 06:30, no new LLM runs launched after 04:00).
The binding Validity requirements in PLAN.md still apply.

## Verdict
1. Scripted half is publishable as is: frozen splits, locked test seeds, two nulls, Wilson CIs, a ledger with discarded experiments. Hard-negative and power results are honest, and "IT detects coordinated *variation*, not agreement" is a real finding. **Scripted work is DONE. Stop touching it.**
2. The LLM half is the whole remaining risk. Partial llm_v1 (20/64 games, director's read of raw prices only, no detectors run) shows a per-seller price SD of about 0.6–0.9 over 20 rounds. The channel shows up as a **level** shift (C/D pair-minus-rivals premium +0.1…+0.85, and D markets at 14.6 vs B at 12.5). Your own §4.2 says level collusion is invisible to dependence measures, so expect pCMI ≈ chance on LLM data. Plan the write-up for that outcome now. It is a legitimate and interesting result if it is shown properly.
3. On track if the queue completes (llm_v1+ctrl ≈ 23:45, llm_long ≈ 01:10, llm_mixed ≈ 01:40) and the time after that goes into analysis and a second LLM dataset. Running more scripted variants or re-polishing the abstract would not keep it on track.

## Directives (priority order)
1. **Make the market-level baseline shock-adjusted and within-family before llm_v1 eval runs** (`experiments/llm_eval.py:126-131`).
   `market_level` is currently the raw mean price, and B/D cost shocks raise prices mechanically (partial data: A 10.0 vs B 12.5). Score it as markup over the state Nash (you already compute `nash` at l.71). Report AUROC within family (C vs A, D vs B) as well as pooled. This is a correctness fix to a baseline, not tuning, so log it in EXPERIMENTS.tsv as a pre-registered definition change *before* you look at llm_v1 detector output.
2. **Second LLM dataset, no LLM cost: run your frozen detectors on the sibling's `../collusion-22-say-vs-do/data/llm_v3`** (read-only; same SCHEMA; 125 runs when done ≈ 00:15; 70 private / 35 none / 20 legit; T=12; public messages present; labels in `labels.jsonl`).
   T=12 is below your shift-null minimum, so report **pair AUROC, run AUROC and top-1 localisation** of pCMI/MI/TE vs `pair_level`/`market_level`. Also report the control-surrogate null against the 35 `none` runs: that pool is ≥ 20, so here, unlike llm_v1, it can actually reach α=0.05. Treat `legit` (public shipping partnership) as a hard negative.
   This gives you external validity (different prompt, framing, grid) and gives 22 the "cheap always-on statistic" row it needs. Write per-pair scores to `results/eval/llm_v3_ext.json` with `{run_id, pair, detector, score}` so 22 can join on it. Declare it in REPORT §4.3 as an extra confirmatory set before computing it.
3. **Fill §4.3 strictly by the declared analysis plan when the queue finishes** (a)–(f). Headline LLM claims, in this order:
   - (i) Does the channel raise prices: market and pair premium, within family, with bootstrap CI.
   - (ii) Do dependence detectors add anything beyond the level baseline: AUROC difference with paired bootstrap over runs.
   - (iii) Pair localisation vs chance 1/6, exact binomial.
   - (iv) Same-model vs cross-model dependence from `llm_mixed`. This is binding PLAN requirement #3. Report it even if n=12 is underpowered, and give the CI, not "no effect".
   - (v) `llm_long`: does T=50 rescue pCMI? That separates "too short" from "collusion is a level".
   Add one LLM figure: per-condition price trajectories, plus AUROC bars with CIs for IT vs level detectors, on both LLM datasets.
4. **Use freed codex budget (after ≈ 01:40) for at most one more LLM batch, chosen by what llm_v1 shows.** Default is **+16 C/D at T=50 with ≥ 6 extra A/B controls** if `llm_long` shows pCMI signal growing with T. Otherwise skip new generation and spend the time on directive 5. Launch nothing after 04:00.
5. **Regenerability and claims audit (04:00–07:00).** Write `scripts/tables.py`, which prints every REPORT table from the `results/*.json` files. Diff its output against REPORT. Then run one codex/Opus adversarial review of REPORT claims only, especially words like "100%", "not removable" and "invisible". Fix stale text: §5 says n=25 per group, but the gate is n=50. EXPERIMENTS.tsv has commit `pending` entries; fill in the hashes. Write a 5-line "umbrella synthesis" paragraph with 22's headline numbers (see cross-pollination).

## Cross-pollination
- **From 22:** `data/llm_v3` (directive 2). Their partial data shows private pairs at +0.8…+3.7 premium over rivals, vs your +0.1…+0.85. Their market (12 rounds, grid 6–30, lab framing) produces a much stronger pair-specific level effect. Say this explicitly: the detectability of LLM collusion depends on the market and the framing.
- **To 22:** your pCMI/pair_level per-pair scores on llm_v3 are their zero-shot statistical baseline. Your anchor lesson ("a single example value in the format spec pins the market") is worth one line in their limitations too.
- llm_v1 has empty public messages (`public_board: false`), so 22 cannot pool it. Don't spend effort making it poolable.

## STOP
- Any further scripted runs, sweeps, null variants or estimator tweaks. Seeds 1001/1002 are spent, and new dev experiments don't change the headline.
- Tuning anything (thresholds, the tacit cutoff, the coordinated-actions ±1 rule, the judge prompt) after looking at llm_v1 detector outputs. The definitions are frozen as of E11.
- Calling a pCMI null on LLM data "detectors fail on LLM agents". The supported claim is narrower: "this market's LLM collusion is a level shift with low variance, and dependence measures are built to ignore that".
- Rewriting the abstract each iteration. Rewrite it once, after §4.3 is filled.
