1. **P0 — Conflicting explanations of the level premium.** [REPORT.md:482](/home/factory/collusion/collusion-14-infotheory/REPORT.md:482): “responds to the mere *offer*”; [REPORT.md:516](/home/factory/collusion/collusion-14-infotheory/REPORT.md:516): “Offer alone does not.” E35 cannot resolve this because framing and agreement are confounded; §4.3.10 explicitly acknowledges that.
   **Replace both interpretations with:** “The level signal persists without message delivery in the lab-framed placebo. It was not detectably localised in the monitor/firm strata; framing and agreement are confounded, so whether attempted coordination is necessary remains unresolved.”

2. **P0 — Summary range omits a tested detector.** [REPORT.md:25](/home/factory/collusion/collusion-14-infotheory/REPORT.md:25): “policy copies sharing a random seed 48–100% flagged.” `gate_test.json` records **44%** for differenced Pearson under the surrogate null, consistent with §4.1’s prose.
   **Replace with:** “policy copies sharing a random seed: 44–100% flagged across the five contemporaneous detectors and both nulls.”

3. **P0 — MI does discriminate C from A, inversely.** [REPORT.md:324](/home/factory/collusion/collusion-14-infotheory/REPORT.md:324): “Raw MI and TE separate D from B but not C from A.” The table, §4.3.4’s later interpretation, and `llm_v1.json` give MI **0.20 [0.06, 0.37]**, clearly below chance.
   **Replace with:** “Raw MI and TE rank D above B. MI ranks C below A (0.20 [0.06, 0.37]); TE’s C-vs-A discrimination is unresolved.”

4. **P1 — False-alarm removal is overstated.** [REPORT.md:24](/home/factory/collusion/collusion-14-infotheory/REPORT.md:24): “Conditioning removes the common-shock false alarm.” The shift-null rate remains **14% [7, 26]**, above the 5% target; the surrogate comparison also changes the reference distribution.
   **Replace with:** “Conditioning reduces common-shock false alarms; the surrogate null flags 4% of held-out shared-policy-plus-shock markets.”

5. **P1 — README drops the shared-seed exception.** [README.md:9](/home/factory/collusion/collusion-14-infotheory/README.md:9): “pCMI separates coordinated price *variation* from shared shocks and shared policies.” Shared-seed policies remain strongly flagged.
   **Replace with:** “In the scripted market, pCMI detects planted shared-signal coordination while reducing false alarms from shared shocks and independently sampled shared policies. Shared-seed policy copies remain a confound.”

6. **P1 — Failure to detect becomes inability to discriminate.** [REPORT.md:483](/home/factory/collusion/collusion-14-infotheory/REPORT.md:483), also [PRESENTATION.md:73](/home/factory/collusion/collusion-14-infotheory/PRESENTATION.md:73): “No detector separates private from placebo runs.” Wide CIs establish neither equivalence nor inability.
   **Replace with:** “No detector’s private-vs-placebo AUROC CI excludes 0.5 at n=15; meaningful delivery effects remain possible.”

7. **P1 — Deck switches the target from assignment to collusion.** [PRESENTATION.md:67](/home/factory/collusion/collusion-14-infotheory/PRESENTATION.md:67): “LLM collusion shows up mainly as a level shift.” These headline AUROCs target channel assignment; only **17/32** `llm_v1` channel games meet the realised-collusion label.
   **Replace with:** “In these markets, level statistics discriminate channel assignment better than pCMI; this does not establish performance on realised collusion.”

8. **P2 — Agreement count uses an expanded definition.** [REPORT.md:257](/home/factory/collusion/collusion-14-infotheory/REPORT.md:257): “judge-verified agreement 70.” The preceding definition pools **67 explicit agreements and 3 information exchanges**.
   **Replace with:** “private 70: 67 judge-labelled explicit agreements and 3 information exchanges; none 35; legit 20.”
