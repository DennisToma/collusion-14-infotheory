#!/usr/bin/env python
"""Resumable runner for the external CDA market (3 LLM sellers + rule-based ZIP buyers, 30 rounds).

  uv run python external/cda/run_cda.py --cond {comms,nocomms} --seeds 0-14 --out data/ext_cda/

Writes <out>/rounds.jsonl (one row per run x round), <out>/ground_truth.jsonl (one row per COMPLETED run;
a run is skipped if its run_id is already there) and <out>/llm_cache.jsonl (per-call cache).
Starter prompts are used unchanged; comms = the starter's --seller_comms_enabled flag.
Runs are sequential; within a run <= 3 LLM calls are in flight (3 sellers).
"""
import argparse, json, random, sys, time, traceback
from typing import Any
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np

from src.continuous_double_auction.cda_types import ExperimentParams
from src.continuous_double_auction.identities import (get_random_agent_names, get_random_buyer_company_names,
                                                      get_random_seller_company_names)
from src.continuous_double_auction.market.agents import LMSeller, ZIPBuyer
from src.continuous_double_auction.market.market import Market
from src.continuous_double_auction.evaluation.metrics import competitive_equilibrium, jpm_price
from src.continuous_double_auction.util.misc import initialize_market
from src.resources.model_wrappers import LlmChatClient, set_cache_path

# Design v1 (2026-10-24 ~14:30 UTC, after the v0 smoke): the starter's ZIPBuyer has its adaptation commented out, so every
# buyer bids a fixed (1 - 0.2) * 100 = 80 = seller cost and no price above cost can ever trade (v0 smoke: asks ~80.6 in
# both conditions; data moved to data/ext_cda_smoke_v0, not analysed). v1: (i) AdaptiveZIPBuyer = the starter's own
# commented-out ZIP update rule, switched on; (ii) 3 sellers vs 2 buyers (excess supply), so competition pushes trade
# prices to cost 80 (CE) and only coordination can hold them toward the buyer value 100 (JPM).
N_SELLERS, N_BUYERS, ROUNDS = 3, 2, 30
SELLER_COST, BUYER_VALUE = 80.0, 100.0   # starter defaults


class AdaptiveZIPBuyer(ZIPBuyer):
    """Starter ZIPBuyer with its (commented-out) ZIP margin update enabled; reads the market it is attached to."""
    market: Any = None

    def generate_bid_response(self, **kwargs):
        rounds = self.market.rounds if self.market is not None else []
        if rounds:
            tr = rounds[-1].trades
            if tr:
                last = float(np.mean([t.price for t in tr]))
                current_bid = (1 - self.profit_margin) * self.valuation
                error = (last - current_bid) / self.valuation
                target = max(0.0, min(1.0, self.profit_margin - error))
            else:  # no trade: all buyers bid too low -> lower the margin (become more aggressive)
                target = max(0.0, self.profit_margin - 0.05)
            adj = (target - self.profit_margin) * self.learning_rate + self.momentum * self.last_adjustment
            self.profit_margin += adj
            self.last_adjustment = adj
        base = (1 - self.profit_margin) * self.valuation
        return {"bid": base * (1 + random.uniform(-self.random_noise, self.random_noise))}


def parse_seeds(s):
    out = []
    for part in s.split(","):
        if "-" in part:
            a, b = part.split("-"); out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def run_one(cond, seed, model, backend, temperature, rounds=ROUNDS):
    run_id = f"cda_{cond}_s{seed}"
    comms = cond == "comms"
    params = ExperimentParams(
        seller_valuations=[SELLER_COST] * N_SELLERS, buyer_valuations=[BUYER_VALUE] * N_BUYERS,
        seller_models=[model] * N_SELLERS, buyer_models=["zip"] * N_BUYERS, rounds=rounds,
        seller_comms_enabled=comms, temperature=temperature, tag=run_id, seed=seed)
    random.seed(seed); np.random.seed(seed)   # same as starter simulation.py
    names = get_random_agent_names(N_BUYERS + N_SELLERS)
    bn, sn = names[:N_BUYERS], names[N_BUYERS:]
    bc, sc = get_random_buyer_company_names(N_BUYERS), get_random_seller_company_names(N_SELLERS)
    buyers = [AdaptiveZIPBuyer(id=f"Buyer {bn[i]}", company=bc[i], valuation=BUYER_VALUE, expt_params=params)
              for i in range(N_BUYERS)]
    clients = [LlmChatClient(run_id, f"seller{i}", model=model, backend=backend, temperature=temperature)
               for i in range(N_SELLERS)]
    sellers = [LMSeller(id=f"Seller {sn[i]}", company=sc[i], valuation=SELLER_COST, expt_params=params,
                        client=clients[i]) for i in range(N_SELLERS)]
    market = Market(sellers=sellers, buyers=buyers)
    for b in buyers:
        b.market = market
    ia, ib = initialize_market(N_SELLERS, params.initial_seller_ask_center, params.initial_seller_ask_spread,
                               N_BUYERS, params.initial_buyer_bid_center, params.initial_buyer_bid_spread)
    market.set_initial_orders([(ia[i], s.id) for i, s in enumerate(sellers)],
                              [(ib[i], b.id) for i, b in enumerate(buyers)])
    for _ in range(rounds):
        market.run_round()
    ce, ce_q = competitive_equilibrium([BUYER_VALUE] * N_BUYERS, [SELLER_COST] * N_SELLERS)
    jpm, jpm_q = jpm_price([BUYER_VALUE] * N_BUYERS, [SELLER_COST] * N_SELLERS)
    sids = [s.id for s in sellers]
    rows = []
    for r in market.rounds:
        rows.append({
            "run_id": run_id, "condition": cond, "seed": seed, "round": r.round_number,
            "seller_ids": sids,
            "asks": {k: r.seller_asks.get(k) for k in sids},      # None = no ask this round (withdrawn)
            "bids": r.buyer_bids,
            "trades": [{"buyer": t.buyer_id, "seller": t.seller_id, "price": t.price} for t in r.trades],
            "messages": r.seller_messages,
            "ce_price": ce, "ce_qty": ce_q, "jpm_price": jpm, "jpm_qty": jpm_q,
        })
    gt = {"run_id": run_id, "condition": cond, "seed": seed, "seller_ids": sids, "buyer_ids": [b.id for b in buyers],
          "n_sellers": N_SELLERS, "n_buyers": N_BUYERS, "buyer_type": "adaptive zip (starter rule, enabled), design v1", "rounds": rounds,
          "seller_comms_enabled": comms, "model": model, "backend": backend, "temperature": temperature,
          "models_seen": sorted(set().union(*[c.models_seen for c in clients])),
          "llm_calls": sum(c.n_calls for c in clients), "llm_calls_cached": sum(c.n_cached for c in clients),
          "parse_failures": sum(c.parse_failures for c in clients),
          "ce_price": ce, "jpm_price": jpm, "colluding": None}
    return rows, gt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cond", required=True, choices=["comms", "nocomms"])
    ap.add_argument("--seeds", default="0-14")
    ap.add_argument("--out", default="data/ext_cda/")
    ap.add_argument("--model", default="qwen-3.6-35b")
    ap.add_argument("--backend", default="aqueduct")
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--rounds", type=int, default=ROUNDS)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    set_cache_path(out / "llm_cache.jsonl")
    gt_path, rounds_path = out / "ground_truth.jsonl", out / "rounds.jsonl"
    done = {json.loads(l)["run_id"] for l in gt_path.read_text().splitlines() if l.strip()} if gt_path.exists() else set()
    for seed in parse_seeds(a.seeds):
        run_id = f"cda_{a.cond}_s{seed}"
        if run_id in done:
            print(f"skip {run_id} (complete)"); continue
        t0 = time.time()
        try:
            rows, gt = run_one(a.cond, seed, a.model, a.backend, a.temperature, a.rounds)
        except Exception:
            print(f"FAILED {run_id}"); traceback.print_exc()
            with open(out / "errors.log", "a") as f:
                f.write(f"{run_id}\n{traceback.format_exc()}\n")
            continue
        gt["wall_s"] = round(time.time() - t0, 1)
        with open(rounds_path, "a") as f:        # rounds first, ground truth last => ground_truth marks completion
            for r in rows: f.write(json.dumps(r) + "\n")
        with open(gt_path, "a") as f:
            f.write(json.dumps(gt) + "\n")
        print(f"done {run_id}: {gt['wall_s']}s calls={gt['llm_calls']} cached={gt['llm_calls_cached']} "
              f"parse_fail={gt['parse_failures']}")


if __name__ == "__main__":
    main()
