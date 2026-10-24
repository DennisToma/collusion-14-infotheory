# Opus judge-read, iteration 17 (2026-10-24 ~04:40 UTC), REPORT abstract/§4.3.8/§4.4/§5 + PRESENTATION.md
All abstract/deck numbers spot-checked against results/eval JSON: match.
Findings (applied unless noted):
1. Abstract: surrogate-null 4% on B is ≈α by construction -> reworded to held-out shared-policy+shock 4% [1,13]. APPLIED
2. Title over-promises for LLM -> NOT applied: title already says pCMI catches moves *not levels*; LLM result (level) is consistent with it; abstract scopes it.
3. "price-level offset" wording for injection clashes with thesis -> "per-round shared ±1 price shock (i.i.d.)" in REPORT §4.3.8, abstract, deck. APPLIED
4. Abstract reported only T=50 injection -> added T=20 0.63–0.66. APPLIED
5. "Level screens catch it" omits sibling placebo -> "separate channel assignment", placebo mentioned. APPLIED (abstract + deck)
6. Deck "no better than chance" -> "not distinguishable from chance (wide CIs)". APPLIED
7. Abstract 44–100% uses pearson_diff not in table -> 48–100% (Table 4.1). APPLIED (body keeps the 44% note)
8. Deck pCMI top-1 18/70 without caveat -> nominal p (computed via binomtest) + "not read as signal". APPLIED
Minor: CI-bound vs planted-mean comparison flagged as rough scale comparison, not a test. APPLIED
