"""E39 (exploratory, post-hoc): is the channel-pair premium already present BEFORE any partner message is read?

Uses data/<name>/preplay.jsonl (provisional pre-play prices, from scripts/preplay_extract.py) and the stored
trajectories. Declared quantities and rule: EXPERIMENTS.tsv E39-offer-cue-declared.
(a) pair provisional price (mean of both members) - mean rivals' round-0 price. NOTE (codex review): pre-play is
    sequential in sim/llm_market.py, so the SECOND sender has read the first sender's message; only the first sender
    (assigned_pair[0]) chose without any partner message. (a1)/(a2) split (a) by sender order (post-declaration addition).
(b) round-0 premium = mean pair round-0 price - mean rivals' round-0 price (pair has read the pre-play message)
(c) full-game premium = pair - rivals, all rounds
plus run AUROC of the round-0 market markup over Nash, C vs A and D vs B.

    uv run python scripts/preplay_offer.py     # -> results/eval/preplay_offer.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from experiments.llm_eval import NASH  # noqa: E402

AGENTS = ["A", "B", "C", "D"]
B = 10000


def boot(x, rng):
    x = np.asarray(x, float)
    m = x[rng.integers(0, len(x), (B, len(x)))].mean(1)
    return [round(float(x.mean()), 3), [round(float(np.percentile(m, 2.5)), 3), round(float(np.percentile(m, 97.5)), 3)]]


def auroc(pos, neg):
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    return float(((pos[:, None] > neg[None]) + 0.5 * (pos[:, None] == neg[None])).mean())


def auroc_ci(pos, neg, rng):
    bs = [auroc(rng.choice(pos, len(pos)), rng.choice(neg, len(neg))) for _ in range(B)]
    return [round(auroc(pos, neg), 3), [round(float(np.percentile(bs, 2.5)), 3), round(float(np.percentile(bs, 97.5)), 3)]]


def load(name):
    rows = {}
    for line in (ROOT / "data" / name / "trajectories.jsonl").read_text().splitlines():
        r = json.loads(line)
        rows.setdefault(r["run_id"], []).append(r)
    for v in rows.values():
        v.sort(key=lambda r: r["round"])
    pre = {json.loads(l)["run_id"]: json.loads(l) for l in (ROOT / "data" / name / "preplay.jsonl").read_text().splitlines()}
    return rows, pre


def main():
    rng = np.random.default_rng(39)
    out = {}
    for name in ["llm_v1", "llm_long"]:
        rows, pre = load(name)
        res, a, a1, a2, b, c = {}, [], [], [], [], []
        for rid, p in sorted(pre.items()):
            pair = p["assigned_pair"]
            idx = [AGENTS.index(x) for x in pair]
            riv = [i for i in range(4) if i not in idx]
            P = np.array([[ag["price"] for ag in r["agents"]] for r in rows[rid]], float)
            r0 = P[0, riv].mean()
            a.append(np.mean([p["provisional_price"][x] for x in pair]) - r0)
            a1.append(p["provisional_price"][pair[0]] - r0)
            a2.append(p["provisional_price"][pair[1]] - r0)
            b.append(P[0, idx].mean() - r0)
            c.append(P[:, idx].mean() - P[:, riv].mean())
        res["n_runs"] = len(a)
        res["offer_premium_provisional_minus_rivals_r0"] = boot(a, rng)
        res["first_sender_provisional_minus_rivals_r0"] = boot(a1, rng)
        res["second_sender_provisional_minus_rivals_r0"] = boot(a2, rng)
        res["round0_premium_pair_minus_rivals"] = boot(b, rng)
        res["full_game_premium_pair_minus_rivals"] = boot(c, rng)
        res["provisional_minus_own_round0"] = boot(np.array(a) - np.array(b), rng)
        # round-0 market markup over Nash, channel vs control (within family)
        mk = {}
        for rid, rs in rows.items():
            cond = rid.split("_")[-2]
            mk.setdefault(cond, []).append(float(np.mean([ag["price"] for ag in rs[0]["agents"]]) - NASH[rs[0]["market"]["cost"]]))
        # descriptive side numbers quoted in REPORT §4.3.11
        res["second_sender_matches_first_provisional"] = [sum(p["provisional_price"][p["assigned_pair"][0]] == p["provisional_price"][p["assigned_pair"][1]] for p in pre.values()), len(pre)]
        by = {}
        for rid, rs in rows.items():
            cond = rid.split("_")[-2]
            pp = pre.get(rid)
            for ag in rs[0]["agents"]:
                role = "control" if cond in "AB" else ("pair" if ag["id"] in pp["assigned_pair"] else "rival")
                by.setdefault(f"{cond}_{role}_round0", []).append(ag["price"])
            if pp:
                by.setdefault(f"{cond}_pair_provisional", []).extend(pp["provisional_price"].values())
        res["mean_price_by_role"] = {k: round(float(np.mean(v)), 2) for k, v in sorted(by.items())}
        res["count_ge14_by_role"] = {k: [int(sum(x >= 14 for x in v)), len(v)] for k, v in sorted(by.items())}
        res["games_with_pair_provisional_ge14"] = {c: [sum(max(p["provisional_price"].values()) >= 14 for p in pre.values() if p["condition"] == c),
                                                       sum(p["condition"] == c for p in pre.values())] for c in sorted({p["condition"] for p in pre.values()})}
        res["round0_market_markup_mean"] = {k: round(float(np.mean(v)), 3) for k, v in sorted(mk.items())}
        for pos, neg in [("C", "A"), ("D", "B")]:
            if pos in mk and neg in mk:
                res[f"round0_markup_auroc_{pos}_vs_{neg}"] = auroc_ci(mk[pos], mk[neg], rng) + [len(mk[pos]), len(mk[neg])]
        def verdict(x):  # declared rule, evaluated on unrounded estimates
            m = np.asarray(x, float)
            bm = m[np.random.default_rng(0).integers(0, len(m), (B, len(m)))].mean(1)
            lo, hi = np.percentile(bm, [2.5, 97.5])
            bb = np.asarray(b, float)[np.random.default_rng(1).integers(0, len(b), (B, len(b)))].mean(1)
            if (lo > 0 or hi < 0) and m.mean() >= 0.5 * np.mean(c):
                return "offer cue present in our market"
            if lo <= 0 <= hi and np.percentile(bb, 2.5) > 0:
                return "premium appears only after first exchange"
            return "inconclusive"
        res["declared_rule_verdict_pair_mean"] = verdict(a)
        res["declared_rule_verdict_first_sender"] = verdict(a1)
        out[name] = res
    path = ROOT / "results" / "eval" / "preplay_offer.json"
    path.write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
