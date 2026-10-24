# Opus adversarial review (Phase 2 iteration 15, 2026-10-24 ~15:50 UTC): main claim, abstract, joint statement, glance, P2.8, P2.11
15 items (3 P0, 9 P1, 3 P2). Each was re-verified against the results files before it was applied (commit e550f57).
- P0 E64 declared prediction only partly met: pair_level executed 0.84 [0.75, 0.92] < declared 0.9 (p2_partc.md) -> P2.11(c).
- P0 "level AUROCs ≈ 1 by construction" wrong for pair_level -> only market_level inflated (glance row C, P2.11(c)).
- P0 "max-pair markup 0.94/0.95/0.99" is market_level (scripts/p2_variants.py DETS) -> "market-level markup"; P2.11 header annotated.
- P1 joint statement: E65 qualifier (0/20 tacit); pair_level loses power rather than failing (0.75-0.80).
- P1 "rarely executed" -> "minority" (38/119; 13/20 in Q2.2 strong framing); glance tacit 1/114 qualified.
- P1 executed-selection caveat on pCMI (E67 rho +0.00) in P2.11(c).
- P1 T20->T60 decline not significant (e44_decline.json −0.18 [−0.41, +0.05]) in abstract.
- P1 "all confirmatory" -> per-section labels; E43–E60 -> E43–E69; status line.
- P1 E61 CI wording (asymmetric [−2.09, +1.36]).
- P1 T=80 secondary declared 06:39, cancelled 13:05 before E44 result -> P2.8 header.
- P1 glance E44 spillover wording (rivals flat, no-channel markets fall).
- P2 E65 populations (executed vs all) in main claim; P2.8(d) Nash is cost-dependent (NASH = {6: 10, 8: 12}).
Not applied: E66 timestamp wording (already covered by the stamp-correction ledger row).
