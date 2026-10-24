Read the full report; no files edited. The main sample counts and headline AUROCs match. E01–E32 comprise **32 unique IDs, 35 log rows** (three declaration/final pairs). §4.3.9’s table matches its JSON.

- **P0 — [§4.3.8](/home/factory/collusion/collusion-14-infotheory/REPORT.md:442):** “AUROC 0.64–0.66 at q=0.2” → **“AUROC 0.63–0.66 at q=0.2.”** `injection_mde.json` gives 0.6373, **0.6305**, and 0.6578; the table and Abstract already agree.

- **P1 — [Title](/home/factory/collusion/collusion-14-infotheory/REPORT.md:1):** “without accusing agents that merely share information or a policy” → **“with fewer false accusations under shared public shocks and independently sampled policies.”** Actual pCMI false-positive rates remain 10–14% under shifts; shared-seed copies remain heavily flagged.

- **P1 — [Abstract](/home/factory/collusion/collusion-14-infotheory/REPORT.md:30):** “A constant high price is not localised by any of these estimators.” → **“In the tested stay-high setting, dependence scores did not reliably localise the designated pair.”** The experiment supports a scoped empirical result, not a universal impossibility.

- **P1 — [§4.1](/home/factory/collusion/collusion-14-infotheory/REPORT.md:146):** “Action-only detectors cannot separate it from a private agreement channel” → **“The tested dependence scores do not establish whether shared randomness comes from policy copies or private agreement.”** Elevated flag rates alone do not prove impossibility for every action-based detector.

- **P1 — [§4.3.7](/home/factory/collusion/collusion-14-infotheory/REPORT.md:405):** “the private channel’s effect shows up mainly as a **price level**” → **“Channel assignment is better discriminated by price-level statistics than by pCMI; the contribution of delivered messages remains unresolved.”** AUROC comparisons establish discrimination, not the mechanism; §4.3.9 strengthens this distinction.

- **P1 — [§4.3.9](/home/factory/collusion/collusion-14-infotheory/REPORT.md:469):** “pCMI is at chance” → **“pCMI’s AUROC estimate is 0.50 [0.23, 0.76], leaving substantial discrimination unresolved.”** Likewise, “No detector separates private from placebo runs” → **“No tested detector resolves private-versus-placebo run discrimination at nominal 95% confidence.”**

- **P1 — [§4.3.9](/home/factory/collusion/collusion-14-infotheory/REPORT.md:470):** “a level screen responds largely to the *offer* of a private channel” → **“A level screen also discriminates placebo from no-channel runs (AUROC 0.89); the additional delivery effect is unresolved.”** “Largely” implies an estimated decomposition that was not established.

- **P1 — [§4.4](/home/factory/collusion/collusion-14-infotheory/REPORT.md:479):** “beating every zero-shot LLM auditor view (≤ 0.86)” → **“exceeding the six original zero-shot auditor views (maximum 0.86).”** The sibling’s later hinted `action_stats` view reaches 0.93; “every” is too broad.

- **P2 — [§5](/home/factory/collusion/collusion-14-infotheory/REPORT.md:502):** “We compare channel vs no-channel markets; without a placebo arm” → **“For `llm_v1`, which lacks a placebo arm, channel-versus-control comparisons cannot isolate message delivery. The sibling placebo analysis (§4.3.9) finds no resolved delivery effect.”** The current opening conflicts with the report’s own placebo analysis unless scoped.

- **P2 — [Abstract](/home/factory/collusion/collusion-14-infotheory/REPORT.md:32):** “raises markup over Nash by +1.8 versus no-channel markets” → **“In `llm_v1`, channel-assigned markets have approximately +1.8 higher mean markup than controls.”** The surrounding sentence names both datasets; +1.8 belongs specifically to `llm_v1`.

- **P2 — [§4.3.9](/home/factory/collusion/collusion-14-infotheory/REPORT.md:469):** “The level statistics stay high … placebo vs none 0.89, private vs placebo 0.46.” → **“For pair_level, placebo-versus-none AUROC is 0.89 and private-versus-placebo is 0.46; for markup, these are 0.78 and 0.47.”** The quoted AUROCs describe only one of the two level statistics.

- **P2 — [§3](/home/factory/collusion/collusion-14-infotheory/REPORT.md:102):** “Scripted seeds 1–99 are dev” → **“Scripted development analyses used seed0 values 0, 7, 11 and 100; locked evaluations used 1001/1002.”** E01/E02 and E03 fall outside the stated development range.

- **P2 — [§7](/home/factory/collusion/collusion-14-infotheory/REPORT.md:535):** “≥ 50 matched seeds” → **“A provisional target of ≥50 matched seeds, finalized by a power calculation for a prespecified delivery effect.”** No supplied JSON establishes 50 as sufficient.
