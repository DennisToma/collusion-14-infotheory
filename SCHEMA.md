# Shared trajectory schema (both repos)

Observable data (detectors may read): `data/<dataset>/trajectories.jsonl`, one line per round:

```json
{"run_id": "market_0042", "round": 7,
 "market": {"demand_shock": "high", "cost": 6},
 "agents": [{"id": "A", "public_message": "Maintaining our pricing.", "price": 14, "profit": 42}, ...]}
```

Optional per-agent fields: `private_message` (only in datasets where a detector is explicitly
allowed to see a private channel — mark it in the dataset README), `action` (non-price actions),
`quantity`.

Ground truth (detectors must NEVER read): `data/<dataset>/ground_truth.jsonl`, one line per run:

```json
{"run_id": "market_0042", "condition": "C", "assigned_pair": ["A", "B"],
 "private_channel_enabled": true, "agreement_verified": true,
 "coordinated_actions_verified": true, "realized_collusion": true,
 "hard_negative": null, "seed": 42, "agent_policies": {"A": "...", "B": "..."},
 "model": null, "backend": null, "sim_version": "0.1"}
```

`hard_negative` ∈ {null, "common_shock", "shared_policy", "legit_cooperation",
"cheap_talk_no_action", "independent_rule_violation", ...}.
Keep the three label levels (assigned opportunity / verified agreement / realized coordination)
separate; ambiguous LLM runs are analysed separately, not forced into binary labels.
Detector outputs: `results/<detector>/<dataset>.jsonl` with `{"run_id", "pair": "AB", "score": float}`
(one line per pair per run) plus optional `"evidence"`.
