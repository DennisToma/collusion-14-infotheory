codex
The main table cells match the JSONs. These are the prioritized issues; line numbers refer to [REPORT.md](/home/factory/collusion/collusion-14-infotheory/REPORT.md).

1. **P0 — L240:** “the judge found an explicit agreement … all 70 private runs.”  
   The snapshot contains **67 `explicit` and 3 `info_exchange`** labels; `ext_llm_v3.py` pools both.  
   **Replace:** “Our communication-positive category pools 67 explicit agreements and 3 information exchanges; all 70 private runs meet this broader criterion.”

2. **P0 — L67–69:** “`shared_policy` … sampling noise is a function of the public history … 30% idiosyncratic.”  
   This describes `shared_seed`. In `sim/market.py`, `shared_policy` independently selects a deterministic heuristic with probability 0.6, otherwise noisy best response. L431 repeats the misplaced 30% parameter.  
   **Replace:** “`shared_policy`: independently apply the same public-history heuristic with probability 0.6, otherwise noisy best response. `shared_seed`: history-seeded sampling, with 30% independent overrides.” Update L431 accordingly.

3. **P0 — L38, repeated L409–410:** “the private channel's effect is dominated by a low-variance price-level shift.”  
   Better level AUROC does not establish this mechanism or quantify variance. §4.3.3 finds substantial first-difference localisation, while short-T power remains unresolved.  
   **Replace:** “Level statistics discriminate channel assignment better than pCMI in these samples. Coordinated variation is also present; these analyses do not establish why pCMI discriminates poorly.” Apply the same qualification to Figure 1’s embedded title.

4. **P0 — L420–424:** “read 01:05 UTC” and “the private channel shows up first as a **price level**.”  
   The sibling report now includes opening-price and placebo results that materially qualify this synthesis. Messages withheld versus delivered produced similar premiums.  
   **Replace/add:** “The sibling’s later exploratory placebo study finds similar premiums with messages withheld versus delivered (rounds 2–12 difference +0.03 [−0.54, +0.49], 15 matched seeds). Its level signal therefore cannot be attributed specifically to delivered private coordination.”

5. **P1 — Figure 1 caption, L14–15:** “mostly does not, and still flags 100% of colluding markets.”  
   This conceals the shift-null false-positive rates and generalises beyond the easiest positive control.  
   **Replace:** “Under the shift null, pCMI flags 10–14% of shared-policy/common-shock controls and 50/50 shared-signal positives in each collusive group (95% CI [93%, 100%]; s=0.6).”

6. **P1 — L422:** “pCMI … is at chance here (0.45, 0.52).”  
   CI inclusion of 0.5 does not establish chance-level equivalence; §5 acknowledges wide intervals.  
   **Replace:** “pCMI does not resolve above-chance run discrimination: 0.45 [0.32, 0.59] and 0.52 [0.39, 0.64].”

7. **P1 — L35:** “added to markup it does not improve discrimination.”  
   This drops the exploratory/model-specific qualification present in §4.3.4.  
   **Replace:** “An exploratory leave-one-run-out logistic analysis detected no improvement from adding pCMI to markup and family (ΔAUROC −0.025 [−0.079, +0.006]).”

8. **P1 — L279:** “some pair in **every** control market co-moves about as strongly as the colluding pair does.”  
   Aggregate AUROCs and overlapping CIs do not support “every.”  
   **Replace:** “Control markets often contain strongly co-moving pairs; these max-pair scores did not resolve run-level discrimination.”

9. **P1 — L347:** “Scripted controls at T=20 were calibrated (0.05…).”  
   This is only 2/40 flags, with Wilson CI approximately [0.014, 0.165].  
   **Replace:** “Scripted controls at T=20 had an observed flag rate of 2/40 = 0.05 [0.014, 0.165], compatible with nominal calibration but imprecisely estimated.”

10. **P1 — L367, repeated L410:** “shows no same-model excess.”  
    This is stronger than §5’s explicit rejection of inferring absence from a null result.  
    **Replace:** “No pCMI same-model excess was detected: +0.003 [−0.025, +0.032] across 12 games.”

11. **P1 — L398:** “2.5× more rounds did not turn the channel's effect into detectable coordinated variation.”  
    Run discrimination does not establish whether coordinated variation became detectable; the interval also includes AUROC 0.65.  
    **Replace:** “Using 50 rather than 20 rounds did not meet the declared pCMI run-discrimination criterion; the small sample leaves moderate discrimination unresolved.”

12. **P2 — L281:** “7 regressors … on 11 usable rows.”  
    `_design_numeric` drops constant state columns. There are **6 columns in 19 runs and 7 in 106**, including 12 private runs with six.  
    **Replace:** “6–7 design columns on 11 usable rows, depending on whether a state variable is constant.”

13. **P2 — L242:** “6 detectors × several subgroups were tested.”  
    `ext_llm_v3.py` evaluates eight distinct scores, including differenced Pearson and CMI|state.  
    **Replace:** “Eight detectors were computed, six displayed here, across several subgroups; p-values are unadjusted and exploratory.”

14. **P2 — L191:** “all games T=20.”  
    The committed `llm_pilot3` trajectory and ground truth have T=15.  
    **Replace:** “Games have T=20, except the committed `llm_pilot3` game, which has T=15.”

15. **P2 — L197–198:** “still 12 everywhere”; “LLMs still 12 every round.”  
    Pilot2/3 contain exceptions; hybrid LLMs choose 12 in **148/160** decisions, with other choices 10, 11 and 13.  
    **Replace:** “Prices remain overwhelmingly concentrated at 12, with occasional deviations; hybrid LLM sellers choose 12 in 148/160 decisions.”

16. **P2 — L434:** “one shared set of 40 runs (A+B) reused in every row.”  
    Controls are reused across types/strengths **at each T**; different T rows use prefixes and have different statistics.  
    **Replace:** “At each T, the same 40 control trajectories are reused across collusion types and strengths; different T values use prefixes of those trajectories.”
tokens used
125,761
The main table cells match the JSONs. These are the prioritized issues; line numbers refer to [REPORT.md](/home/factory/collusion/collusion-14-infotheory/REPORT.md).

1. **P0 — L240:** “the judge found an explicit agreement … all 70 private runs.”  
   The snapshot contains **67 `explicit` and 3 `info_exchange`** labels; `ext_llm_v3.py` pools both.  
   **Replace:** “Our communication-positive category pools 67 explicit agreements and 3 information exchanges; all 70 private runs meet this broader criterion.”

2. **P0 — L67–69:** “`shared_policy` … sampling noise is a function of the public history … 30% idiosyncratic.”  
   This describes `shared_seed`. In `sim/market.py`, `shared_policy` independently selects a deterministic heuristic with probability 0.6, otherwise noisy best response. L431 repeats the misplaced 30% parameter.  
   **Replace:** “`shared_policy`: independently apply the same public-history heuristic with probability 0.6, otherwise noisy best response. `shared_seed`: history-seeded sampling, with 30% independent overrides.” Update L431 accordingly.

3. **P0 — L38, repeated L409–410:** “the private channel's effect is dominated by a low-variance price-level shift.”  
   Better level AUROC does not establish this mechanism or quantify variance. §4.3.3 finds substantial first-difference localisation, while short-T power remains unresolved.  
   **Replace:** “Level statistics discriminate channel assignment better than pCMI in these samples. Coordinated variation is also present; these analyses do not establish why pCMI discriminates poorly.” Apply the same qualification to Figure 1’s embedded title.

4. **P0 — L420–424:** “read 01:05 UTC” and “the private channel shows up first as a **price level**.”  
   The sibling report now includes opening-price and placebo results that materially qualify this synthesis. Messages withheld versus delivered produced similar premiums.  
   **Replace/add:** “The sibling’s later exploratory placebo study finds similar premiums with messages withheld versus delivered (rounds 2–12 difference +0.03 [−0.54, +0.49], 15 matched seeds). Its level signal therefore cannot be attributed specifically to delivered private coordination.”

5. **P1 — Figure 1 caption, L14–15:** “mostly does not, and still flags 100% of colluding markets.”  
   This conceals the shift-null false-positive rates and generalises beyond the easiest positive control.  
   **Replace:** “Under the shift null, pCMI flags 10–14% of shared-policy/common-shock controls and 50/50 shared-signal positives in each collusive group (95% CI [93%, 100%]; s=0.6).”

6. **P1 — L422:** “pCMI … is at chance here (0.45, 0.52).”  
   CI inclusion of 0.5 does not establish chance-level equivalence; §5 acknowledges wide intervals.  
   **Replace:** “pCMI does not resolve above-chance run discrimination: 0.45 [0.32, 0.59] and 0.52 [0.39, 0.64].”

7. **P1 — L35:** “added to markup it does not improve discrimination.”  
   This drops the exploratory/model-specific qualification present in §4.3.4.  
   **Replace:** “An exploratory leave-one-run-out logistic analysis detected no improvement from adding pCMI to markup and family (ΔAUROC −0.025 [−0.079, +0.006]).”

8. **P1 — L279:** “some pair in **every** control market co-moves about as strongly as the colluding pair does.”  
   Aggregate AUROCs and overlapping CIs do not support “every.”  
   **Replace:** “Control markets often contain strongly co-moving pairs; these max-pair scores did not resolve run-level discrimination.”

9. **P1 — L347:** “Scripted controls at T=20 were calibrated (0.05…).”  
   This is only 2/40 flags, with Wilson CI approximately [0.014, 0.165].  
   **Replace:** “Scripted controls at T=20 had an observed flag rate of 2/40 = 0.05 [0.014, 0.165], compatible with nominal calibration but imprecisely estimated.”

10. **P1 — L367, repeated L410:** “shows no same-model excess.”  
    This is stronger than §5’s explicit rejection of inferring absence from a null result.  
    **Replace:** “No pCMI same-model excess was detected: +0.003 [−0.025, +0.032] across 12 games.”

11. **P1 — L398:** “2.5× more rounds did not turn the channel's effect into detectable coordinated variation.”  
    Run discrimination does not establish whether coordinated variation became detectable; the interval also includes AUROC 0.65.  
    **Replace:** “Using 50 rather than 20 rounds did not meet the declared pCMI run-discrimination criterion; the small sample leaves moderate discrimination unresolved.”

12. **P2 — L281:** “7 regressors … on 11 usable rows.”  
    `_design_numeric` drops constant state columns. There are **6 columns in 19 runs and 7 in 106**, including 12 private runs with six.  
    **Replace:** “6–7 design columns on 11 usable rows, depending on whether a state variable is constant.”

13. **P2 — L242:** “6 detectors × several subgroups were tested.”  
    `ext_llm_v3.py` evaluates eight distinct scores, including differenced Pearson and CMI|state.  
    **Replace:** “Eight detectors were computed, six displayed here, across several subgroups; p-values are unadjusted and exploratory.”

14. **P2 — L191:** “all games T=20.”  
    The committed `llm_pilot3` trajectory and ground truth have T=15.  
    **Replace:** “Games have T=20, except the committed `llm_pilot3` game, which has T=15.”

15. **P2 — L197–198:** “still 12 everywhere”; “LLMs still 12 every round.”  
    Pilot2/3 contain exceptions; hybrid LLMs choose 12 in **148/160** decisions, with other choices 10, 11 and 13.  
    **Replace:** “Prices remain overwhelmingly concentrated at 12, with occasional deviations; hybrid LLM sellers choose 12 in 148/160 decisions.”

16. **P2 — L434:** “one shared set of 40 runs (A+B) reused in every row.”  
    Controls are reused across types/strengths **at each T**; different T rows use prefixes and have different statistics.  
    **Replace:** “At each T, the same 40 control trajectories are reused across collusion types and strengths; different T values use prefixes of those trajectories.”
