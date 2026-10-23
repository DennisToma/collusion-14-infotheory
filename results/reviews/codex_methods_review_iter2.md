**Verdict:** useful dependence demonstration; evidence does not yet establish a calibrated collusion detector.

- **Null validity:** [infotheory.py:145](/home/factory/collusion/collusion-14-infotheory/detectors/infotheory.py:145) conditions shifted prices on **unshifted state**, destroying each seller’s price–state relationship. This does not simulate conditional independence given state. At [line 161](/home/factory/collusion/collusion-14-infotheory/detectors/infotheory.py:161), shifting fitted residuals breaks their orthogonality to the shared regression design; regression uncertainty and constraints are not reproduced. TE additionally uses one common shift across pair-specific residualizations. Max-stat correction cannot repair invalid surrogates; stationary marginal series alone are insufficient.

- **Concrete short-T failures:** [infotheory.py:155](/home/factory/collusion/collusion-14-infotheory/detectors/infotheory.py:155) skips all null draws at T≤7 but divides by B+1. Verified: constant T=5 prices produce **p=0.004975 for every detector**. At T=20, equal offsets occur with probability 1/14, preserving observed pair dependence. A perfectly identical pair failed significance in all ten null seeds tested. Power curves partly measure this calibration artifact.

- **Estimator bias:** [infotheory.py:48](/home/factory/collusion/collusion-14-infotheory/detectors/infotheory.py:48) uses observed-support Miller–Madow correction despite sparse contingency tables. At T=20, four states average five observations each against 25 possible price combinations. My independent five-price simulation still averaged **0.336 nats MI after correction**. pCMI fits up to eight coefficients to 19 observations; it is a Gaussian/linear proxy, not general conditional MI. “Net influence” at [line 175](/home/factory/collusion/collusion-14-infotheory/detectors/infotheory.py:175) is an affine transformation preserving pair rankings exactly.

- **Scripted fairness:** [market.py:110](/home/factory/collusion/collusion-14-infotheory/sim/market.py:110) plants fresh synchronized randomness: an exceptionally favorable dependence positive control. Conversely, [line 97](/home/factory/collusion/collusion-14-infotheory/sim/market.py:97) couples sampling seeds; identical stochastic policies normally have independent draws. This tests shared randomness, not merely “same model.” Leader-following is a useful negative. Labels at [line 188](/home/factory/collusion/collusion-14-infotheory/sim/market.py:188) declare agreement/realization from assignment and strength without checking realized supra-competitive behavior.

- **LLM design:** [llm_market.py:81](/home/factory/collusion/collusion-14-infotheory/sim/llm_market.py:81) avoids explicit collusion instructions, appropriately. However, the JSON example anchors everyone at price 12; histories expose only eight rounds, and exact demand parameters are omitted. [Line 129](/home/factory/collusion/collusion-14-infotheory/sim/llm_market.py:129) allows stronger models specifically for channel members, confounding capability with communication. No matched heterogeneous-model no-channel control implements PLAN’s requirement.

- **Label/evaluation bugs:** [llm_eval.py:92](/home/factory/collusion/collusion-14-infotheory/experiments/llm_eval.py:92) includes prices from the round a message was sent, before delivery. Its equality fallback rejects valid alternating/splitting agreements and can accept incidental matching; one numeric target cannot represent changing agreements. At [line 139](/home/factory/collusion/collusion-14-infotheory/experiments/llm_eval.py:139), ambiguous/unverified runs become “not realized.” A/B aggregates retain tacit runs, AUROC uses opportunity labels, and prefix evaluations reuse full-game labels. **No direct ground-truth leakage into detector scores was found:** inputs are prices and public state.

Judges should reject “FWER controlled,” “gate passes” ([REPORT:83](/home/factory/collusion/collusion-14-infotheory/REPORT.md:83)), explicit-collusion specificity, and LLM generalization. Twenty-five controls cannot establish 5% calibration; percentile bootstrap intervals degenerate at zero events. Required ≥60 LLM games and matched-model experiments remain unestablished.

Top five fixes, ranked by value/hour:

1. Guard unsupported T; divide by actual null draws.
2. Separate verified, ambiguous, tacit, and opportunity metrics; make labels time-consistent.
3. Validate conditional nulls on independent surrogates; reproduce the complete fitting/scoring pipeline.
4. Replace seed-coupled controls with independent draws; match model composition across conditions.
5. Report exact/Wilson intervals, held-out calibration and power curves; restrict claims until ≥60 LLM games pass verification.

