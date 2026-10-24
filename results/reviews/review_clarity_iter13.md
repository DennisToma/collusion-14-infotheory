**Two-minute verdict: the central result is clear; the evaluation target is easier to miss.** From [README.md](/home/factory/collusion/collusion-14-infotheory/README.md) and [REPORT.md](/home/factory/collusion/collusion-14-infotheory/REPORT.md), I can state:

- **Question:** Can price dependence identify colluding pairs without mistaking shared information or policies for collusion?
- **Setup:** Four-seller markets, first with scripted agents, then LLM sellers with or without a private pair channel.
- **Finding:** Conditioned dependence works for scripted shared price variation. Price-level statistics distinguish channel-enabled LLM markets better.
- **Limits:** Channel assignment is not verified collusion; high prices also occur legitimately; short games, small samples and shared randomness limit interpretation.

I get lost in the abstract’s abbreviations and condition letters. Later, pilots and analysis history delay the main LLM result. The distinction between screening markets and naming pairs needs earlier emphasis.

The top eight fixes, in priority order:

1. **README, “Question”; REPORT, Abstract — “prices only.”** This conflicts with conditioning on public state. Replace with: “Detectors use seller prices and, for conditioned measures, public demand and cost state. They do not read private messages.”

2. **REPORT, opening claim — “Conditioned dependence (pCMI).”** Define it before using it: “Our pCMI score measures correlation between sellers’ price movements after accounting for public demand, costs and all sellers’ previous prices.” Keep the formula in §3.

3. **REPORT, Abstract — “a within-game circular-shift null and … a control-surrogate null.”** Replace with: “We compare scores with two baselines: the same game with sellers’ price histories shifted out of alignment, and comparable games without a private channel.”

4. **REPORT §2, Market — “4 sellers A–D … Conditions: A independent; B common shocks…”** Sellers and conditions share labels. Replace with: “Four sellers, numbered 1–4. Conditions: A = no channel, no shocks; B = no channel, public shocks; C = designated coordinating pair, no shocks; D = designated pair plus shocks. Compare C with A and D with B.” Call these “shock settings,” rather than unexplained “families.”

5. **README, Short answer — “a simple markup or pair-level statistic.”** Replace with: “Simple level scores perform better: markup measures price above the competitive Nash benchmark; pair premium measures a pair’s average price above its rivals.”

6. **REPORT, Abstract — “Level statistics separate channel from control runs (run AUROC…).”** Put the target before the scores: “The LLM evaluation primarily distinguishes channel-enabled games from controls, not verified collusion from non-collusion. AUROC measures ranking performance: 0.5 is chance and 1 is perfect. Naming the assigned pair is a separate task.”

7. **REPORT §4.3.1 — “Pilots: getting LLM sellers to vary prices.”** Move pilots after the main results and present `llm_v1` before the external set. Replace the opening with: “We first present the main LLM experiment, then the external market and robustness checks. Pilot design lessons follow.”

8. **REPORT §4.3.2 — “Analysis plan, declared before results (after the iteration-3 review…).”** Move the long mapping, timestamps and experiment IDs to an appendix. Replace with: “Before evaluation, we fixed tests of price levels, market screening, pair localisation and calibration. Longer-game and mixed-model checks follow; the appendix records decision timing.”

Claims that exceed their evidence:

- **§4.3.2, “rivals follow”:** causal direction is untested. Use “Channel-enabled games have higher market-wide prices.”
- **§4.3.5, “do not produce more price dependence”:** use “We detected no clear excess; uncertainty remains.”
- **Opening, “built to ignore”:** explains insensitivity to constant offsets, but does not establish why pCMI performs poorly. Add: “Limited power and conditioning away coordination remain possible explanations.”
