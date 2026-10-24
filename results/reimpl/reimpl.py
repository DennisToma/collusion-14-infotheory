"""Independent implementation of the four statistics requested in BRIEF.md.

Run with the Python interpreter specified in the brief. Only the supplied JSONL
data are read; labels are used exclusively for AUROCs and flag-rate summaries.
"""

from __future__ import annotations

import itertools
import json
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score


ROOT = Path(__file__).resolve().parent
SELLERS = ("A", "B", "C", "D")
PAIRS = tuple(itertools.combinations(range(4), 2))
STATISTICS = ("pCMI", "MI_MM", "market_level", "pair_level")
SEED = 0
N_NULL = 200
MIN_SEPARATION = 3
MIN_VALID_SHIFTS = 20
RHO2_CEILING = 1.0 - 1e-12


def read_jsonl(path: Path) -> list[dict]:
    with path.open() as stream:
        return [json.loads(line) for line in stream if line.strip()]


def load_dataset(name: str, rounds: int) -> tuple[dict, dict]:
    """Select only prices and market state from trajectories, and check alignment."""
    directory = ROOT / "data" / name
    runs = defaultdict(list)
    for row in read_jsonl(directory / "trajectories.jsonl"):
        by_id = {agent["id"]: agent["price"] for agent in row["agents"]}
        if set(by_id) != set(SELLERS) or len(row["agents"]) != 4:
            raise ValueError("Expected exactly four distinct sellers")
        prices = [by_id[seller] for seller in SELLERS]
        if any(not np.isfinite(p) or float(p) != int(p) for p in prices):
            raise ValueError("MI requires finite integer prices")
        state = (row["market"]["demand_shock"], row["market"]["cost"])
        if state[0] not in ("low", "high") or state[1] not in (6, 8):
            raise ValueError("Unexpected public state")
        runs[row["run_id"]].append((row["round"], prices, state))
    label_rows = read_jsonl(directory / "labels.jsonl")
    labels = {row["run_id"]: row["condition"] for row in label_rows}
    if len(labels) != len(label_rows) or set(labels) != set(runs):
        raise ValueError("Labels and trajectories must match one-to-one by run")
    result = {}
    for run_id, rows in sorted(runs.items()):
        rows.sort(key=lambda row: row[0])
        if len(rows) != rounds or [row[0] for row in rows] != list(range(rounds)):
            raise ValueError(f"Unexpected or missing rounds for {run_id}")
        result[run_id] = {
            "prices": np.asarray([row[1] for row in rows], dtype=float),
            "states": [row[2] for row in rows],
        }
    return result, labels


def entropy_mm(values: np.ndarray) -> float:
    """Plug-in entropy plus Miller--Madow's occupied-support correction, nats."""
    _, counts = np.unique(values, axis=0, return_counts=True)
    probabilities = counts / len(values)
    return float(-np.sum(probabilities * np.log(probabilities))
                 + (len(counts) - 1) / (2 * len(values)))


def mi_mm(x: np.ndarray, y: np.ndarray) -> float:
    return entropy_mm(x) + entropy_mm(y) - entropy_mm(np.column_stack((x, y)))


def regression_residuals(prices: np.ndarray, states: list) -> tuple[np.ndarray, np.ndarray]:
    """OLS on current joint-state indicators and all four prices at t-1."""
    current_states = states[1:]
    levels = sorted(set(current_states))
    design = np.column_stack(
        [np.ones(len(prices) - 1)]
        + [np.asarray([state == level for state in current_states], dtype=float)
           for level in levels[1:]]
        + [prices[:-1]]
    )
    # The SVD projection remains well defined for rank-deficient designs.
    u, singular_values, _ = np.linalg.svd(design, full_matrices=False)
    tolerance = singular_values[0] * max(design.shape) * np.finfo(float).eps
    basis = u[:, singular_values > tolerance]
    target = prices[1:]
    residuals = target - basis @ (basis.T @ target)
    # Exact fits leave floating-point roundoff; these are constant residuals.
    scales = np.maximum(1.0, np.linalg.norm(target, axis=0))
    residuals[:, np.linalg.norm(residuals, axis=0) <= 1e-10 * scales] = 0.0
    return residuals, basis


def pcmi_pairs(residuals: np.ndarray) -> np.ndarray:
    """Gaussian residual-correlation information; zero for a constant series."""
    centered = residuals - residuals.mean(axis=0)
    norms = np.linalg.norm(centered, axis=0)
    result = []
    for i, j in PAIRS:
        if norms[i] <= 1e-12 or norms[j] <= 1e-12:
            result.append(0.0)
            continue
        rho = np.dot(centered[:, i], centered[:, j]) / (norms[i] * norms[j])
        rho2 = np.clip(rho * rho, 0.0, RHO2_CEILING)
        result.append(float(-0.5 * np.log1p(-rho2)))
    return np.asarray(result)


@lru_cache(maxsize=None)
def relative_shift_configurations(length: int) -> np.ndarray:
    """All admissible relative offsets, with seller A fixed at offset zero."""
    def separated(a: int, b: int) -> bool:
        delta = abs(a - b)
        return min(delta, length - delta) >= MIN_SEPARATION

    candidates = [offset for offset in range(length) if separated(0, offset)]
    configurations = []
    for b, c, d in itertools.permutations(candidates, 3):
        if separated(b, c) and separated(b, d) and separated(c, d):
            configurations.append((0, b, c, d))
    return np.asarray(configurations, dtype=int).reshape((-1, 4))


def pcmi_null_pvalue(residuals: np.ndarray, basis: np.ndarray,
                    observed: float, rng: np.random.Generator) -> tuple[float, dict]:
    length = len(residuals)
    configurations = relative_shift_configurations(length)
    diagnostics = {
        "residual_rounds": length,
        "valid_relative_shift_configurations": len(configurations),
        "draws": 0,
    }
    if len(configurations) < MIN_VALID_SHIFTS:
        diagnostics["exceedances"] = None
        return 1.0, diagnostics
    exceedances = 0
    for _ in range(N_NULL):
        relative = configurations[rng.integers(len(configurations))]
        # Restoring an independent common offset gives a uniform draw over all
        # admissible absolute offset tuples, including offset zero.
        offsets = (relative + rng.integers(length)) % length
        shifted = np.column_stack([np.roll(residuals[:, i], offsets[i])
                                   for i in range(4)])
        rer = shifted - basis @ (basis.T @ shifted)
        null_score = float(np.max(pcmi_pairs(rer)))
        # Conservative treatment of numerical ties, including exact fits.
        if null_score >= observed - 1e-12:
            exceedances += 1
    diagnostics.update(draws=N_NULL, exceedances=exceedances)
    return (exceedances + 1) / (N_NULL + 1), diagnostics


def score_run(prices: np.ndarray, states: list) -> tuple[dict, np.ndarray, np.ndarray]:
    residuals, basis = regression_residuals(prices, states)
    nash = np.asarray([10.0 if state[1] == 6 else 12.0 for state in states])
    scores = {"pCMI": pcmi_pairs(residuals).tolist(),
              "MI_MM": [], "market_level": [], "pair_level": []}
    for i, j in PAIRS:
        others = [k for k in range(4) if k not in (i, j)]
        pair_prices = prices[:, [i, j]]
        scores["MI_MM"].append(mi_mm(prices[:, i], prices[:, j]))
        scores["market_level"].append(float(np.mean(pair_prices - nash[:, None])))
        scores["pair_level"].append(float(pair_prices.mean() - prices[:, others].mean()))
    return scores, residuals, basis


def calculate_aurocs(scores: dict, labels: dict) -> dict:
    comparisons = {"C_D_vs_A_B": ({"C", "D"}, {"A", "B"}),
                   "C_vs_A": ({"C"}, {"A"}),
                   "D_vs_B": ({"D"}, {"B"})}
    result = {}
    for name, (positive, negative) in comparisons.items():
        run_ids = [rid for rid in sorted(labels) if labels[rid] in positive | negative]
        y = [int(labels[rid] in positive) for rid in run_ids]
        if len(set(y)) != 2:
            continue
        # The long dataset has only A/C, so its pooled comparison is redundant.
        if name == "C_D_vs_A_B" and not {"A", "B", "C", "D"} <= set(labels.values()):
            continue
        result[name] = {
            stat: float(roc_auc_score(y, [scores[stat][rid] for rid in run_ids]))
            for stat in STATISTICS
        }
    return result


def main() -> None:
    rng = np.random.default_rng(SEED)
    v1, v1_labels = load_dataset("llm_v1", 20)
    long, long_labels = load_dataset("llm_long", 50)
    if Counter(v1_labels.values()) != Counter(A=21, B=21, C=16, D=16):
        raise ValueError("Unexpected llm_v1 labels")
    if Counter(long_labels.values()) != Counter(A=8, C=8):
        raise ValueError("Unexpected llm_long labels")
    first20 = {rid: {"prices": run["prices"][:20], "states": run["states"][:20]}
               for rid, run in long.items()}
    datasets = {"llm_v1": (v1, v1_labels), "llm_long": (long, long_labels),
                "llm_long_first20": (first20, long_labels)}
    output = {
        "metadata": {
            "seed": SEED, "null_draws": N_NULL, "information_units": "nats",
            "pair_order": ["".join(SELLERS[i] for i in pair) for pair in PAIRS],
            "dataset_rounds": {"llm_v1": 20, "llm_long": 50, "llm_long_first20": 20},
            "pvalue_estimator": "(1 + count(null_max >= observed_max)) / (B + 1)",
            "rho_squared_ceiling": RHO2_CEILING,
        },
        "pair_scores": {}, "aurocs": {}, "flag_rates": {},
        "pCMI_null_diagnostics": {},
    }
    for name, (runs, labels) in datasets.items():
        run_scores = {stat: {} for stat in STATISTICS}
        pair_scores = {stat: {} for stat in STATISTICS}
        pvalues = {}
        for rid, run in sorted(runs.items()):
            scores, residuals, basis = score_run(run["prices"], run["states"])
            for stat in STATISTICS:
                pair_scores[stat][rid] = dict(zip(output["metadata"]["pair_order"], scores[stat]))
                run_scores[stat][rid] = max(scores[stat])
            if name == "llm_v1":
                pvalue, diagnostics = pcmi_null_pvalue(
                    residuals, basis, run_scores["pCMI"][rid], rng)
                pvalues[rid] = pvalue
                output["pCMI_null_diagnostics"][rid] = diagnostics
        output["aurocs"][name] = calculate_aurocs(run_scores, labels)
        if name == "llm_v1":
            run_scores["pCMI_pvalue"] = pvalues
            output["flag_rates"][name] = {}
            for condition in ("A", "C"):
                selected = [p for rid, p in pvalues.items() if labels[rid] == condition]
                flagged = sum(p < 0.05 for p in selected)
                output["flag_rates"][name][condition] = {
                    "n_runs": len(selected), "n_flagged": flagged,
                    "fraction_p_lt_0_05": flagged / len(selected),
                }
        output[name] = run_scores
        output["pair_scores"][name] = pair_scores
    destination = ROOT / "results.json"
    destination.write_text(json.dumps(output, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"aurocs": output["aurocs"], "flag_rates": output["flag_rates"]}, indent=2))


if __name__ == "__main__":
    main()
