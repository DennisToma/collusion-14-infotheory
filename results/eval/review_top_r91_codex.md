- **P0 | L62 | “abliterated − base (C − A)… Q2.2 −1.24 [−2.41, −0.03]”** — Wrong contrast. The sibling interval describes **pair premium**, not C − A market markup. Source: `data/ext_q22_partc/p2_qwen_cmp.json:P3_paired_premium.diff_boot95` = `[-1.24, -2.41, -0.03]`; the detailed table at L808 labels it “premium.”

- **P0 | L53, L68 | “pCMI 2/21”** — Matches the final JSON but conflicts with P2.3 at L644, which still says **0/21** and describes an interim pool. Source: `results/eval/matched_ref.json:rows.pcmi@0.05.v1A|fresh_all` = **2 flags / 21**, reference pool **50**, `interim=false`. Update the detailed section.

- **P0 | L72 | “change −0.18 [−0.41, +0.05]”** — Literal saved-JSON rounding discrepancy: `results/eval/e44_decline.json:pcmi.ci[0]` = **−0.40499999999999997**, which Python formats to **−0.40**, not −0.41. This is a rounding-boundary issue.

- **P1 | L7 | “every seller model we tested: 9/9 sets, 7 models”** — Overstates scope: those counts describe the **nine main sets**. Other tested conditions are excluded. Source: `claims_denominators.json` explicitly groups those sets as `main`; `strongF_ext.json` reports channel-versus-none market-level AUROC **0.4425**. Say “all nine main sets.”

- **P1 | L8–9, L19, L72 | “not prices moving together”; “show no co-movement”; “show no co-move excess”** — Failure to detect does not establish absence. Source values include E70 pCMI **0.51 [0.43, 0.59]**, executed-only **0.42 [0.33, 0.53]**, and observed excess **0.00356 [−0.00661, 0.01475]**. Use “no statistically detected…” consistently.

- **P1 | L12 | “it sits in channel games whose agreement was not executed”** — Implies an established subgroup difference. Source: `e72_te_diag.json:c_execution` gives **0.728 [0.638, 0.804]** non-executed versus **0.491 [0.381, 0.600]** executed; their difference was **not tested**. Restore that caveat from L14/L22.

- **P1 | L14 | “restricting to executed agreements does not raise pCMI”** — Only a point-estimate comparison is supported. Source: `p2_partc.json:E64_pooled.all sets.pcmi` gives executed **0.422 [0.328, 0.532]**, non-executed **0.524 [0.447, 0.598]**, without a difference interval/test.

- **P1 | L62 | “does not explain low pCMI”** — Lack of correlation does not rule out the mechanism. Source: `e67_sticky.json:llm_strong_qa.rho_sticky_pcmi` = **0.002 [−0.341, 0.372]**. Say “the proposed explanation was not supported.”

- **P1 | L70 | “deterministic bid rotation… is invisible to it”** — Too categorical. Source: `rotation_test.json:summaries` gives pCMI AUROCs **0.63 [0.47, 0.78]** and **0.61 [0.46, 0.75]**, with **6/30** and **2/30** flags. These support no reliable run-level detection here, not invisibility.

- **P1 | L72 | “The answer is the same… when sellers get memory”** — Conflicts with the declared **inconclusive** verdict. Source: `p2_partc.json:E65_verdict` gives executed-only pCMI **0.33 [0.02, 0.66]**; its upper bound crosses the **0.65** decision threshold.

- **P2 | L24, L52, L54, L62–63 | source pointers** — Incomplete provenance. Add `executed_sensitivity.json` for **13–78/149, 27, 0.343–0.531**; `p2_partc.json` for L52 execution counts; `behaviour_split.json` and `p2_public_llm_ds_p2pub.json` for L54; `strongF_ext.json`, `e67_sticky.json`, and the sibling snapshot for L62; `e70_followup.json` for L63’s **1.075 [−0.204, 2.407]**.

- **P2 | L68–69 | “+0.24 vs +1.75”; “0.65 [0.34, 1.32]”** — These five sibling values have no saved source in `results/`; they remain unverified under the requested source restriction. “Premium vanishes” also needs uncertainty evidence, not merely a smaller point estimate.

All other checked numerical claims match at two-decimal precision.

**Numbers checked: 685 occurrences—668 numeric literals and 17 written-out quantities, including repetitions; excluding identifiers, dates and list labels. Five lacked a saved source.**
