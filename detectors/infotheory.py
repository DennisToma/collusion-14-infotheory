"""Information-theoretic pairwise collusion detectors. Reads ONLY trajectories.jsonl.

Per run and per pair (i, j) computes:
  pearson      |corr(p_i, p_j)|
  pearson_diff |corr(dp_i, dp_j)|
  mi           plug-in MI(p_i; p_j) with Miller-Madow bias correction (nats)
  cmi_state    discrete CMI(p_i; p_j | market state), Miller-Madow per stratum
  pcmi         Gaussian CMI(p_i,t; p_j,t | state, all lagged prices) = -1/2 log(1 - pcorr^2)
  te           lagged Gaussian CMI, max over directions of
               I(p_i,t-1 ; p_j,t | state_t, p_j,t-1, other lagged prices)
  ni_<x>       pairwise net influence (Bonjour et al. style): score_x(pair) - mean over other pairs
Each score gets a within-run null via circular shifts of one agent's (residual) series;
p-value = (1 + #{null >= obs}) / (1 + B).
"""
from __future__ import annotations

import argparse
import itertools
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

AGENTS = ["A", "B", "C", "D"]
PAIRS = list(itertools.combinations(range(4), 2))
PAIR_NAMES = ["".join(AGENTS[k] for k in p) for p in PAIRS]


def load_runs(path):
    runs = defaultdict(list)
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            runs[r["run_id"]].append(r)
    out = {}
    for rid, rows in runs.items():
        rows.sort(key=lambda r: r["round"])
        ids = [a["id"] for a in rows[0]["agents"]]
        P = np.array([[a["price"] for a in r["agents"]] for r in rows], float)
        S = [json.dumps(r["market"], sort_keys=True) for r in rows]
        levels = sorted(set(S))
        out[rid] = {"P": P, "S": np.array([levels.index(s) for s in S]), "ids": ids}
    return out


# ---------------------------------------------------------------- estimators
def _entropy_mm(counts):
    counts = counts[counts > 0]
    n = counts.sum()
    if n == 0:
        return 0.0
    p = counts / n
    return float(-(p * np.log(p)).sum() + (len(counts) - 1) / (2 * n))


def mi_mm(x, y):
    """Miller-Madow corrected plug-in MI for small discrete alphabets."""
    _, xi = np.unique(x, return_inverse=True)
    _, yi = np.unique(y, return_inverse=True)
    joint = np.zeros((xi.max() + 1, yi.max() + 1))
    np.add.at(joint, (xi, yi), 1)
    return _entropy_mm(joint.sum(1)) + _entropy_mm(joint.sum(0)) - _entropy_mm(joint.ravel())


def cmi_mm(x, y, z):
    tot, n = 0.0, len(x)
    for s in np.unique(z):
        m = z == s
        tot += m.sum() / n * mi_mm(x[m], y[m])
    return tot


def _design(S, P, t_idx, exclude_lag=None):
    """Regressors: const, state dummies, lagged prices (optionally excluding one agent's lag)."""
    n_lev = S.max() + 1
    cols = [np.ones(len(t_idx))]
    cols += [(S[t_idx] == s).astype(float) for s in range(1, n_lev)]
    for k in range(P.shape[1]):
        if k != exclude_lag:
            cols.append(P[t_idx - 1, k])
    return np.column_stack(cols)


def _resid(y, X):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    r = y - X @ beta
    return (r - r.mean()) / (r.std() + 1e-12)


def gauss_cmi_from_resid(ri, rj):
    r = float(np.clip(np.mean(ri * rj), -0.999999, 0.999999))
    return -0.5 * np.log(1 - r * r)


def _shift_null(stat_fn, x, y, B, rng, min_shift=3):
    n = len(y)
    if n <= 2 * min_shift:
        return np.zeros(B)
    shifts = rng.integers(min_shift, n - min_shift + 1, size=B)
    return np.array([stat_fn(x, np.roll(y, s)) for s in shifts])


# ---------------------------------------------------------------- per-run scoring
def score_run(P, S, B=200, seed=0):
    rng = np.random.default_rng(seed)
    T = len(P)
    t_idx = np.arange(1, T)
    X = _design(S, P, t_idx)
    R = np.column_stack([_resid(P[t_idx, k], X) for k in range(4)])
    dP = np.diff(P, axis=0)
    out = {}
    for (i, j), name in zip(PAIRS, PAIR_NAMES):
        sc, pv = {}, {}

        def add(key, fn, x, y):
            obs = fn(x, y)
            null = _shift_null(fn, x, y, B, rng)
            sc[key] = float(obs)
            pv[key] = float((1 + (null >= obs - 1e-12).sum()) / (1 + B))

        def absr(x, y):
            if x.std() == 0 or y.std() == 0:
                return 0.0
            return abs(np.corrcoef(x, y)[0, 1])

        add("pearson", absr, P[:, i], P[:, j])
        add("pearson_diff", absr, dP[:, i], dP[:, j])
        add("mi", mi_mm, P[:, i], P[:, j])
        # CMI | state: shift y jointly with nothing -> keeps x,z aligned (conservative-ish null)
        add("cmi_state", lambda x, y: cmi_mm(x, y, S), P[:, i], P[:, j])
        add("pcmi", gauss_cmi_from_resid, R[:, i], R[:, j])
        # transfer entropy (both directions), lag-1, Gaussian
        te_vals = []
        for a, b in ((i, j), (j, i)):
            Xb = _design(S, P, t_idx, exclude_lag=a)
            rb = _resid(P[t_idx, b], Xb)
            ra = _resid(P[t_idx - 1, a], Xb)
            te_vals.append((ra, rb))
        def te_stat(_x, _y, te_vals=te_vals):
            return max(gauss_cmi_from_resid(ra, rb) for ra, rb in te_vals)
        obs = te_stat(None, None)
        null = []
        for _ in range(B):
            null.append(max(gauss_cmi_from_resid(ra, np.roll(rb, rng.integers(3, len(rb) - 2)))
                            for ra, rb in te_vals))
        sc["te"] = float(obs)
        pv["te"] = float((1 + (np.array(null) >= obs - 1e-12).sum()) / (1 + B))
        out[name] = {"score": sc, "p": pv}
    # net influence: excess over mean of other pairs
    for key in ["mi", "cmi_state", "pcmi"]:
        vals = np.array([out[n]["score"][key] for n in PAIR_NAMES])
        for k, n in enumerate(PAIR_NAMES):
            out[n]["score"][f"ni_{key}"] = float(vals[k] - np.delete(vals, k).mean())
    return out


def run_detectors(dataset_dir, B=200, out_root=None):
    dataset_dir = Path(dataset_dir)
    runs = load_runs(dataset_dir / "trajectories.jsonl")
    res = {}
    for k, (rid, d) in enumerate(sorted(runs.items())):
        res[rid] = score_run(d["P"], d["S"], B=B, seed=k)
    if out_root:
        out_root = Path(out_root)
        keys = next(iter(res.values()))[PAIR_NAMES[0]]["score"].keys()
        for key in keys:
            od = out_root / key
            od.mkdir(parents=True, exist_ok=True)
            with open(od / f"{dataset_dir.name}.jsonl", "w") as f:
                for rid, pr in res.items():
                    for n in PAIR_NAMES:
                        f.write(json.dumps({"run_id": rid, "pair": n, "score": pr[n]["score"][key],
                                            "p": pr[n]["p"].get(key)}) + "\n")
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset")
    ap.add_argument("--B", type=int, default=200)
    ap.add_argument("--out", default="results")
    a = ap.parse_args()
    run_detectors(a.dataset, a.B, a.out)
