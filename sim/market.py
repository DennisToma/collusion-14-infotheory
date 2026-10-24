"""Repeated differentiated-product (logit) pricing game with 4 sellers + scripted policies.

Writes datasets in SCHEMA.md format:
    data/<name>/trajectories.jsonl   (observable)
    data/<name>/ground_truth.jsonl   (labels; detectors must never read)

Demand: multinomial logit with an outside option.
    share_i = exp((Q - p_i)/MU) / (exp(Q0/MU) + sum_j exp((Q - p_j)/MU))
    profit_i = (p_i - cost) * M * share_i
Public market state per round: demand_shock in {low, high} (scales M), cost in {6, 8}.
In conditions without common shocks the state is constant (low/normal demand, cost 6).
"""
from __future__ import annotations

import itertools
import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

SIM_VERSION = "0.2"
AGENTS = ["A", "B", "C", "D"]
PRICES = np.array([8, 10, 12, 14, 16])
Q, Q0, MU = 16.0, 0.0, 3.0
M = {"low": 100.0, "high": 160.0}
COSTS = (6, 8)


def profits(prices, cost, demand, mu=MU):
    """Profits with a scalar cost, an aligned cost vector, or agent-keyed costs."""
    p = np.asarray(prices, float)
    if isinstance(cost, dict):
        cost = np.array([cost[a] for a in AGENTS])
    e = np.exp((Q - p) / mu)
    share = e / (np.exp(Q0 / MU) + e.sum())
    return (p - cost) * M[demand] * share


def expected_profit_grid(others, cost, demand, mu=MU):
    """Own profit for each candidate price given the other sellers' prices."""
    return np.array([profits([q, *others], cost, demand, mu)[0] for q in PRICES])


def benchmarks(cost=6, demand="low"):
    """Symmetric discrete Nash equilibria and joint-profit-maximising symmetric price."""
    nash = []
    for p in PRICES:
        br = PRICES[np.argmax(expected_profit_grid([p, p, p], cost, demand))]
        if br == p:
            nash.append(int(p))
    joint = {int(p): float(profits([p] * 4, cost, demand).sum()) for p in PRICES}
    # best joint (possibly asymmetric) for a pair while other two at Nash
    pn = nash[0] if nash else 10
    pair = {(int(a), int(b)): float(profits([a, b, pn, pn], cost, demand)[:2].sum())
            for a in PRICES for b in PRICES}
    return {"nash": nash, "joint_symmetric": joint, "best_joint": max(joint, key=joint.get),
            "pair_best_vs_nash": max(pair, key=pair.get), "nash_profit_each":
            float(profits([pn] * 4, cost, demand)[0])}


# ---------------------------------------------------------------- policies
@dataclass
class Ctx:
    t: int
    me: int
    last: np.ndarray | None  # last-round prices (4,)
    cost: int
    demand: str
    rng: np.random.Generator
    shared: dict = field(default_factory=dict)  # private shared state for colluding agents
    mu: float = MU  # logit demand scale of this market (Phase 2 gap 7)


def quantal_br(ctx: Ctx, temp=4.0, eps=0.15):
    """Noisy (logit/quantal) best response to rivals' last prices; eps uniform exploration."""
    if ctx.rng.random() < eps or ctx.last is None:
        return int(ctx.rng.choice(PRICES))
    others = np.delete(ctx.last, ctx.me)
    u = expected_profit_grid(others, ctx.cost, ctx.demand, ctx.mu)
    w = np.exp((u - u.max()) / temp)
    return int(ctx.rng.choice(PRICES, p=w / w.sum()))


def high_priced(ctx: Ctx):
    """Independent agent that happens to price high (hard negative)."""
    return int(ctx.rng.choice(PRICES, p=[0.0, 0.05, 0.15, 0.4, 0.4]))


def leader(ctx: Ctx):
    return quantal_br(ctx)


def follower(ctx: Ctx, leader_idx: int, p_match=0.7):
    """Legit public price-matching of a leader's *previous* price (no channel)."""
    if ctx.last is not None and ctx.rng.random() < p_match:
        return int(ctx.last[leader_idx])
    return quantal_br(ctx)


def shared_policy(ctx: Ctx, p_rule=0.6):
    """Two agents running the same 'model' with INDEPENDENT sampling noise (temperature > 0): with
    prob p_rule both apply the same nonlinear heuristic to the public history (follow the market up
    when last round's mean price >= 12, otherwise undercut), else noisy best response. No channel;
    dependence comes only from the shared deterministic response to common public information."""
    if ctx.last is None or ctx.rng.random() >= p_rule:
        return quantal_br(ctx)
    others = np.delete(ctx.last, ctx.me)
    return 14 if others.mean() >= 12 else 10


def shared_seed(ctx: Ctx):
    """Extreme shared-policy case: same model AND shared sampling randomness (e.g. temperature 0 or a
    common seed): the sample is a function of the public history. No private channel, but statistically
    this is a shared random signal."""
    pub = 0 if ctx.last is None else int(sum(int(x) * 17 ** k for k, x in enumerate(ctx.last)))
    r = np.random.default_rng([ctx.t, pub, ctx.cost, int(ctx.demand == "high")])
    sub = Ctx(ctx.t, ctx.me, ctx.last, ctx.cost, ctx.demand, r, mu=ctx.mu)
    # personal idiosyncrasy: with prob 0.3 use own rng instead
    if ctx.rng.random() < 0.3:
        sub.rng = ctx.rng
    return quantal_br(sub)


def colluder_signal(ctx: Ctx, strength: float):
    """Colluding agents coordinate via a private shared signal: each round, with prob `strength`
    all members play the agreed price for that round (drawn privately from {12,14,16});
    otherwise play independently (quantal BR)."""
    sh = ctx.shared
    if sh.get("t") != ctx.t:  # first member to act this round draws the shared decision
        sh["t"] = ctx.t
        sh["coord"] = sh["rng"].random() < strength
        sh["price"] = int(sh["rng"].choice([12, 14, 16], p=[0.2, 0.4, 0.4]))
    return sh["price"] if sh["coord"] else quantal_br(ctx)


def colluder_fixed_high(ctx: Ctx, strength: float):
    """Tacit-style constant collusion: with prob `strength` play 16, else quantal BR.
    No *shared* randomness -> no contemporaneous dependence beyond marginals (hard case)."""
    return 16 if ctx.rng.random() < strength else quantal_br(ctx)


def colluder_tft(ctx: Ctx, partner: int, strength: float):
    """Price-match partner's last price (reward/punish), else quantal BR."""
    if ctx.last is not None and ctx.rng.random() < strength:
        return int(ctx.last[partner])
    return quantal_br(ctx)


# ---------------------------------------------------------------- game runner
def run_game(run_id, seed, T, condition, pair=None, strength=0.0, collusion_type="signal",
             hard_negative=None, hn_pair=None, *, coalition=None, onset=0, cost_offsets=None,
             n_agents=4, mu=MU):
    """Run a market; coalition members share one signal, offsets stay private.

    n_agents / mu (Phase 2 gap 7) change the number of sellers (named A, B, ...) and the logit
    demand scale; the defaults reproduce the original 4-seller market exactly.

    Coalition is an alternative to pair and always uses the signal policy. Before
    onset, every assigned colluder uses its ordinary quantal best response.
    """
    agents = AGENTS if n_agents == 4 else [chr(65 + k) for k in range(n_agents)]
    if coalition is not None:
        if pair is not None:
            raise ValueError("pair and coalition are mutually exclusive")
        coalition = sorted(coalition)
        if len(coalition) < 3 or len(set(coalition)) != len(coalition) or not set(coalition) <= set(agents):
            raise ValueError("coalition must contain 3 or 4 distinct agents")
        collusion_type = "signal"
    if not isinstance(onset, (int, np.integer)) or onset < 0:
        raise ValueError("onset must be a nonnegative integer")
    if cost_offsets is not None:
        if not set(cost_offsets) <= set(agents) or any(not isinstance(v, (int, np.integer)) for v in cost_offsets.values()):
            raise ValueError("cost_offsets must map agent names to integer offsets")
        cost_offsets = {a: int(v) for a, v in cost_offsets.items()}
    rng = np.random.default_rng(seed)
    common = condition in ("B", "D")
    pair = list(pair) if pair else None
    members = coalition or pair
    shared = {"rng": np.random.default_rng(seed + 10_000_000)}
    policies = {a: "quantal_br" for a in agents}
    if pair:
        for a in pair:
            policies[a] = f"colluder_{collusion_type}(s={strength})"
    if hard_negative in ("shared_policy", "shared_seed"):
        for a in hn_pair:
            policies[a] = hard_negative
    elif hard_negative == "legit_cooperation":
        policies[hn_pair[0]] = "leader"; policies[hn_pair[1]] = f"follower({hn_pair[0]})"
    elif hard_negative == "independent_high_price":
        for a in hn_pair:
            policies[a] = "high_priced"
    if coalition:
        for a in coalition:
            policies[a] = f"colluder_signal(s={strength})"

    rows, last = [], None
    agent_rngs = [np.random.default_rng(seed * 10 + k + 1) for k in range(n_agents)]
    for t in range(T):
        demand = ("high" if rng.random() < 0.5 else "low") if common else "low"
        cost = int(rng.choice(COSTS)) if common else 6
        prices = np.zeros(n_agents, int)
        for k, a in enumerate(agents):
            own_cost = cost + cost_offsets.get(a, 0) if cost_offsets is not None else cost
            ctx = Ctx(t, k, last, own_cost, demand, agent_rngs[k], shared, mu)
            pol = policies[a]
            if pol.startswith("colluder_") and t < onset:
                p = quantal_br(ctx)
            elif pol.startswith("colluder_signal"):
                p = colluder_signal(ctx, strength)
            elif pol.startswith("colluder_fixed"):
                p = colluder_fixed_high(ctx, strength)
            elif pol.startswith("colluder_tft"):
                partner = agents.index(pair[1] if a == pair[0] else pair[0])
                p = colluder_tft(ctx, partner, strength)
            elif pol == "shared_policy":
                p = shared_policy(ctx)
            elif pol == "shared_seed":
                p = shared_seed(ctx)
            elif pol == "leader":
                p = leader(ctx)
            elif pol.startswith("follower"):
                p = follower(ctx, agents.index(hn_pair[0]))
            elif pol == "high_priced":
                p = high_priced(ctx)
            else:
                p = quantal_br(ctx)
            prices[k] = p
        private_costs = [cost + cost_offsets.get(a, 0) for a in agents] if cost_offsets is not None else cost
        pr = profits(prices, private_costs, demand, mu)
        rows.append({"run_id": run_id, "round": t, "market": {"demand_shock": demand, "cost": cost},
                     "agents": [{"id": a, "public_message": "", "price": int(prices[k]),
                                 "profit": round(float(pr[k]), 3)} for k, a in enumerate(agents)]})
        last = prices
    gt = {"run_id": run_id, "condition": condition, "assigned_pair": pair,
          "private_channel_enabled": bool(members), "agreement_verified": bool(members),
          "coordinated_actions_verified": bool(members) and strength > 0,
          "realized_collusion": bool(members) and strength > 0,
          "hard_negative": hard_negative if hard_negative else ("common_shock" if condition == "B" else None),
          "hn_pair": list(hn_pair) if hn_pair else None,
          "collusion_type": collusion_type if members else None, "strength": strength if members else 0.0,
          "T": T, "seed": seed, "agent_policies": policies, "model": None, "backend": None,
          "sim_version": SIM_VERSION}
    if coalition is not None:
        gt["assigned_coalition"] = coalition
    if onset > 0:
        gt["onset"] = int(onset)
        gt["coordinated_actions_verified"] = gt["realized_collusion"] = bool(members) and strength > 0 and onset < T
    if cost_offsets is not None:
        gt["cost_offsets"] = cost_offsets
    if n_agents != 4 or mu != MU:
        gt["n_agents"], gt["mu"] = int(n_agents), float(mu)
    return rows, gt


def write_dataset(name, games, root=Path(__file__).resolve().parent.parent / "data"):
    d = root / name
    d.mkdir(parents=True, exist_ok=True)
    with open(d / "trajectories.jsonl", "w") as ft, open(d / "ground_truth.jsonl", "w") as fg:
        for rows, gt in games:
            for r in rows:
                ft.write(json.dumps(r) + "\n")
            fg.write(json.dumps(gt) + "\n")
    return d


PAIRS = [p for p in itertools.combinations(AGENTS, 2)]

if __name__ == "__main__":
    for c, dm in [(6, "low"), (6, "high"), (8, "low"), (8, "high")]:
        print(c, dm, benchmarks(c, dm))
