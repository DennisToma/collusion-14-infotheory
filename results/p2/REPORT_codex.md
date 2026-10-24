# Phase 2 scripted DEV experiments — Codex report

Implemented and ran all three experiments at the requested n=30 per group, T=100, B=100, signal strength 0.6, using multiprocessing Pool(3). No reductions were needed. Results are DEV observations, with no held-out evaluation or LLM calls. No git commit was made.

**Filesystem limitation:** `/var/tmp/c14/p2s` is mounted read-only by the execution sandbox. Both the initial uv-cache creation and the requested baseline dataset write failed there with `Errno 30: Read-only file system`. All scratch datasets and compatibility baselines are therefore in `/var/tmp/c14/wt_p2s/.p2_scratch/`, and this report is staged at `/var/tmp/c14/wt_p2s/REPORT_codex.md`. The requested `/var/tmp/c14/p2s/REPORT_codex.md` could not be written. All new files are inside the two user-authorized directories. Scratch/cache/environment paths are gitignored.

**Changes.** `sim/market.py` adds keyword-only coalition, onset, and private cost-offset options. Three or four coalition members share the same signal; before onset colluders use quantal best response. Context costs and profits use each agent’s private cost, while public market state retains public costs. Ground-truth additions are conditional so default serialization is preserved. Scalar, vector, and agent-keyed profit costs are supported. `detectors/infotheory.py` adds `score_groups` without changing `score_run`: 11 subset TCs, per-subset p-values, separate tc2/tc3/tc4 maximum-statistic tests, and descriptive three-agent TC minus summed pairwise pCMI. Pair equivalence is asserted for observations and null draws. Near-singular correlation eigenvalues are floored at 1e-12; correlation clipping agrees with the existing pCMI convention.

`experiments/p2_scripted.py` supplies coalition, onset, and costasym subcommands, enforces seed0 in 200..299, writes raw per-run datasets outside data/, prints compact tables, and saves all scores and evaluation summaries under results/p2/. `experiments/test_p2_scripted.py` contains seven focused tests: shared coalition signals/labels and invalid assignments, onset prefixes for all existing collusion types, private cost contexts/profits/public states, pairwise TC/pCMI null equivalence, direct determinant TC, insufficient-draw handling, and level/CUSUM/surrogate calibration invariants.

**Compatibility.** Before edits, generated `gen("compat_before", 3, 30, 0.6, "signal", 7, hard_negatives=True, root=...)`; after edits generated compat_after with the same arguments. Both files are byte-identical after changing only compat_before to compat_after. Full score_run output for compat_before_00000 at B=100, seed=17 is exactly equal before and after, including all scores and p-values. The score_run source is also unchanged. The only departure from the prescribed compatibility call is the scratch-root fallback described above. Hashes and check parameters are saved in `results/p2/compatibility.json`; the before/after JSONL files and original score output remain in .p2_scratch/.

| Check | Result |
| --- | --- |
| trajectories.jsonl, normalized run prefix | PASS |
| ground_truth.jsonl, normalized run prefix | PASS |
| Complete score_run dictionary | PASS |
| score_run source unchanged | PASS |
| Focused unit tests | 7 passed |
| Integration audit | 420 games, 100 rounds each; final simulator reproduces one run per group |
| git diff --check | PASS |

**Run settings and runtime.** A has constant public cost 6 and low demand; B has common public cost/demand shocks. Actual run seeds use the existing scripted convention seed0 × 1,000,000 + run index. Controls and treatments have distinct run seeds. Numeric libraries were restricted to one thread per worker. Timings include simulation, scoring, calibration, and summary construction; output-file serialization is outside the timed interval.

| Experiment | seed0 | Groups × n | T | B | Seconds | Dataset directory |
| --- | --- | --- | --- | --- | --- | --- |
| coalition | 200 | 8 × 30 | 100 | 100 | 51.1 | p2_coalition_dev_s200_n30_B100 |
| onset | 210 | 3 × 30 | 100 | 100 | 117.4 | p2_onset_dev_s210_n30_B100 |
| costasym | 220 | 3 × 30 | 100 | 100 | 19.1 | p2_costasym_dev_s220_n30_B100 |

Total experiment runtime: 187.5 seconds. Each experiment is well under 20 minutes on three worker processes.

Rates below are percentages with Wilson 95% intervals. Mean scores use 1,000-draw bootstrap 95% intervals, and AUROCs use a stratified 1,000-draw bootstrap over positive and control runs. Flagging is strictly p < 0.05. Surrogate ranks use same-family controls and leave a control itself out. Per-run records in the JSON files retain all pair scores, subset scores/p-values, and sequential look p-values.

**Coalition detection.** Shift-null tc3 corrects over four triples; tc4 tests the full four-agent set. Each is calibrated separately from the max-pair pCMI test. Relative pair level is the maximum, over pairs, of time-mean pair price minus the other two sellers’ mean price; its flag uses the control-surrogate rank.

| Family/group | pCMI flag % | TC3 flag % | TC4 flag % | Pair-level flag % |
| --- | --- | --- | --- | --- |
| A/coalition3 | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] |
| A/coalition4 | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | 0.0 [0.0, 11.4] |
| A/control | 3.3 [0.6, 16.7] | 0.0 [0.0, 11.4] | 3.3 [0.6, 16.7] | 3.3 [0.6, 16.7] |
| A/pair | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] |
| B/coalition3 | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] |
| B/coalition4 | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | 0.0 [0.0, 11.4] |
| B/control | 10.0 [3.5, 25.6] | 10.0 [3.5, 25.6] | 6.7 [1.8, 21.3] | 3.3 [0.6, 16.7] |
| B/pair | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] |

For a pair, “inside” means exactly the assigned pair. For three agents it means both members of the named pair belong to the coalition. Inside-coalition localization is tautologically 100% for four colluders; it is not evidence of useful pair localization.

| Family/group | Top pCMI pair inside % | Top level pair inside % | Top TC3 exact % |
| --- | --- | --- | --- |
| A/coalition3 | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] |
| A/coalition4 | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | — |
| A/pair | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | — |
| B/coalition3 | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] |
| B/coalition4 | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | — |
| B/pair | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | — |

Market-level score is the maximum time-mean pair markup; market-wide markup averages all four sellers. Both subtract Nash 10 at public cost 6 and Nash 12 at public cost 8 round by round. Net influence uses the existing score_run definition, with the maximum over its six pair scores.

| Family/group | Max pair relative level | Max pair markup | Market mean markup | Max ni_pcmi |
| --- | --- | --- | --- | --- |
| A/coalition3 | 0.977 [0.939, 1.014] | 2.979 [2.897, 3.064] | 2.491 [2.421, 2.559] | 0.568 [0.517, 0.629] |
| A/coalition4 | 0.120 [0.103, 0.139] | 3.174 [3.079, 3.260] | 3.114 [3.016, 3.204] | 0.246 [0.207, 0.283] |
| A/control | 0.163 [0.136, 0.189] | 0.482 [0.457, 0.512] | 0.400 [0.381, 0.424] | 0.012 [0.009, 0.016] |
| A/pair | 2.233 [2.148, 2.312] | 2.800 [2.726, 2.875] | 1.684 [1.641, 1.727] | 0.732 [0.671, 0.798] |
| B/coalition3 | 0.823 [0.776, 0.873] | 2.251 [2.171, 2.333] | 1.840 [1.778, 1.905] | 0.538 [0.495, 0.588] |
| B/coalition4 | 0.099 [0.083, 0.115] | 2.436 [2.366, 2.499] | 2.387 [2.317, 2.452] | 0.225 [0.194, 0.259] |
| B/control | 0.175 [0.150, 0.202] | 0.294 [0.267, 0.321] | 0.206 [0.183, 0.230] | 0.016 [0.011, 0.022] |
| B/pair | 1.752 [1.697, 1.812] | 2.171 [2.112, 2.230] | 1.295 [1.258, 1.334] | 0.679 [0.620, 0.748] |

| Family/group | ni_pcmi flag % | Max-pair-markup flag % | Market-mean-markup flag % |
| --- | --- | --- | --- |
| A/coalition3 | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] |
| A/coalition4 | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] |
| A/control | 3.3 [0.6, 16.7] | 3.3 [0.6, 16.7] | 3.3 [0.6, 16.7] |
| A/pair | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] |
| B/coalition3 | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] |
| B/coalition4 | 96.7 [83.3, 99.4] | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] |
| B/control | 3.3 [0.6, 16.7] | 3.3 [0.6, 16.7] | 3.3 [0.6, 16.7] |
| B/pair | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] |

Run AUROC versus the controls of the same shock family (point estimate [bootstrap 95% CI]):

| Family/group | Max pCMI | TC3 | TC4 | Market markup | Pair level | Max ni_pcmi |
| --- | --- | --- | --- | --- | --- | --- |
| A/coalition3 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] |
| A/coalition4 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 0.333 [0.203, 0.476] | 1.000 [1.000, 1.000] |
| A/pair | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] |
| B/coalition3 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] |
| B/coalition4 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 0.213 [0.107, 0.336] | 0.998 [0.990, 1.000] |
| B/pair | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] |

Three-agent synergy is a descriptive score with no p-value. Means for all named triples are included here; the JSON additionally retains every per-run value. Negative values are allowed and do not represent a negative total correlation.

| Family/group | ABC | ABD | ACD | BCD |
| --- | --- | --- | --- | --- |
| A/coalition3 | -0.170 [-0.278, -0.080] | -0.204 [-0.319, -0.108] | -0.097 [-0.175, -0.031] | -0.075 [-0.151, -0.011] |
| A/coalition4 | -0.569 [-0.617, -0.520] | -0.571 [-0.613, -0.522] | -0.577 [-0.627, -0.529] | -0.561 [-0.606, -0.514] |
| A/control | -0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| A/pair | 0.000 [-0.002, 0.002] | 0.000 [-0.002, 0.002] | -0.000 [-0.001, 0.001] | 0.003 [-0.000, 0.007] |
| B/coalition3 | -0.123 [-0.211, -0.045] | -0.147 [-0.243, -0.064] | -0.133 [-0.223, -0.051] | -0.146 [-0.240, -0.054] |
| B/coalition4 | -0.475 [-0.527, -0.426] | -0.477 [-0.524, -0.435] | -0.462 [-0.507, -0.420] | -0.468 [-0.517, -0.425] |
| B/control | -0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.001] | -0.000 [-0.001, 0.000] | -0.000 [-0.000, 0.000] |
| B/pair | 0.002 [-0.000, 0.004] | -0.001 [-0.003, 0.000] | -0.001 [-0.003, 0.001] | -0.000 [-0.004, 0.004] |

The four-agent setting breaks the relative pair-level detector here: its flag rate is 0% in both families and its AUROCs are 0.333 (A) and 0.213 (B). TC4 and market markup still detect all such runs. The proposed net-influence failure is **not observed** at this strength and horizon: maximum ni_pcmi still flags 100% (A) and 96.7% (B), with AUROCs 1.000 and 0.998. Even when all six population pair effects are similar, taking their finite-sample maximum can leave a positive contrast; it should not be interpreted as recovering a unique colluding pair. pCMI already detects all these positives, so these experiments do not establish incremental power from TC4. TC3/TC4 also flag pair-only collusion: a significant group TC is not evidence that every member colludes.

**Onset.** Six separate CUSUM accumulators use S_t=max(0,S_(t-1)+d_t−0.5), alarming when their maximum strictly exceeds h=14.500. h is the higher empirical 95th percentile of the 30 control-run maximum paths, using only this experiment’s controls. Exact 5% in-sample FPR is unavailable at n=30; this conservative nonrandomized rule permits at most one strict exceedance (3.3%). This is an in-sample calibration result, not an independent FPR estimate.

pCMI uses expanding windows of 20,30,…,100 rounds with B=100 at every look, and alarms at the first run-level p < 0.05 without repeated-testing correction. Both methods stop at their first alarm. Detection requires that first alarm occur at or after onset; earlier alarms are reported separately and excluded from delay summaries. Delay equals zero-based alarm-round index minus onset, so detection on the first collusive round has delay zero. Delays are conditional on detected runs; undetected runs are not assigned artificial delays.

| Group | Method | Any alarm/control FPR % | Post-onset detection % | Pre-onset alarm % | Delay median [IQR], rounds |
| --- | --- | --- | --- | --- | --- |
| control | cusum | 3.3 [0.6, 16.7] | — | — | — |
| control | pcmi | 33.3 [19.2, 51.2] | — | — | — |
| onset25 | cusum | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | 0.0 [0.0, 11.4] | 6.5 [5.0, 9.0] (n=30) |
| onset25 | pcmi | 100.0 [88.6, 100.0] | 83.3 [66.4, 92.7] | 16.7 [7.3, 33.6] | 14.0 [4.0, 14.0] (n=25) |
| onset50 | cusum | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | 0.0 [0.0, 11.4] | 7.0 [6.0, 9.0] (n=30) |
| onset50 | pcmi | 100.0 [88.6, 100.0] | 86.7 [70.3, 94.7] | 13.3 [5.3, 29.7] | 9.0 [9.0, 19.0] (n=26) |

CUSUM detected every positive run after onset, with median delays of 6.5 rounds (onset 25) and 7 rounds (onset 50). Its calibrated control alarm rate was 3.3%. Expanding-window pCMI alarmed on 33.3% of controls; 16.7% and 13.3% of positive runs alarmed before their respective onsets. The repeated-look pCMI alarm rule therefore needs calibration before it could be treated as a 5% sequential test.

**Cost asymmetry.** All sellers in the hard-negative group use quantal best response with no channel. Two randomly selected sellers privately pay +2 per unit. Shift-null rates use max-pair pCMI or MI; relative pair levels use a rank against plain controls at alpha 0.05. Rates in the costasym and control rows are false flags; the pair row is a positive-control detection rate. High-cost top-1 statistics count naming the exact innocent high-cost pair even when the run is not flagged.

| Group | pCMI flag % | MI flag % | Pair-level flag % | High-cost pair top level % | High-cost pair top pCMI % |
| --- | --- | --- | --- | --- | --- |
| A/control | 6.7 [1.8, 21.3] | 10.0 [3.5, 25.6] | 3.3 [0.6, 16.7] | — | — |
| A/costasym | 6.7 [1.8, 21.3] | 3.3 [0.6, 16.7] | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | 10.0 [3.5, 25.6] |
| A/pair | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | 100.0 [88.6, 100.0] | — | — |

| Group | Mean max relative pair level |
| --- | --- |
| A/control | 0.160 [0.136, 0.184] |
| A/costasym | 1.537 [1.482, 1.588] |
| A/pair | 2.352 [2.272, 2.424] |

Cost asymmetry completely confounds relative pair levels in this sample: all 30 hard negatives are falsely flagged, and all 30 name the high-cost pair. pCMI falsely flags 2/30 hard negatives (the same 2/30 rate as its separate plain controls); MI flags 1/30. pCMI names the high-cost pair top-1 in 3/30 runs, so neither its run flags nor pair naming show a large systematic effect here, subject to the wide intervals.

**Reproduction.** With an installed project environment, run the following from `/var/tmp/c14/wt_p2s`. Omit --scratch when the requested /var/tmp/c14/p2s path is writable. The CLI defaults to that requested directory and fails explicitly if it cannot write there; it does not silently relocate datasets.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 uv run python -m experiments.p2_scripted coalition --scratch /var/tmp/c14/wt_p2s/.p2_scratch
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 uv run python -m experiments.p2_scripted onset --scratch /var/tmp/c14/wt_p2s/.p2_scratch
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 uv run python -m experiments.p2_scripted costasym --scratch /var/tmp/c14/wt_p2s/.p2_scratch
uv run python -m unittest experiments.test_p2_scripted -v
```

The sandbox could not fetch dependencies (DNS/network restriction), so execution reused the preinstalled Python environment read-only. The actual command prefix was `UV_CACHE_DIR=/var/tmp/c14/wt_p2s/.p2_cache OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 uv run --no-project --python /home/factory/collusion/collusion-14-infotheory/.venv/bin/python python`. All project modules were imported from the worktree, and no sibling-repository files were modified. Logs are in .p2_scratch/{coalition,onset,costasym,tests}.log. Result artifacts are results/p2/{coalition,onset,costasym}_dev.json and results/p2/{compatibility,validation}.json.

**Doubts and limits.** These are 30-run DEV estimates, not population guarantees or held-out claims. Intervals are broad for rare flags, and bootstrap AUROC intervals can collapse to [1,1] under complete sample separation. The common-shock control false-flag rates should be read with their intervals, rather than assumed to equal 5%. Each subset-size max test is separate; there is no correction across tc2/tc3/tc4. Circular shifts assume a suitable residual null; onset is nonstationary and expanding-window results are descriptive. CUSUM uses the same controls for threshold selection and reported calibration; 30 controls cannot establish out-of-sample 5% error control. Sequential pCMI repeatedly tests without correction and its empirical control alarm rate must be reported. Surrogate-rank p-values are coarse with 30 controls (minimum 1/31 for a treatment and 1/30 for a control), with no multiplicity correction across experiments. Private costs are deliberately omitted from detector state and can confound relative price levels. Group TC measures dependence and does not independently prove communication or the coalition’s exact size. No simulator/detector tuning was performed based on the observed DEV outcomes.
