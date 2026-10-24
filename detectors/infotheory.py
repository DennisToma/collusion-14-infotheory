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


DESIGN = "lin"  # "lin": state dummies + lags; "inter": + state x lag interactions


def _design(S, P, t_idx, exclude_lag=None, design=None):
    """Regressors: const, state dummies, lagged prices (optionally excluding one agent's lag).
    design="inter" adds state-dummy x lagged-price interactions (each state level gets its own
    response to rivals' previous prices); used only when there are >= 4 rows per regressor."""
    design = design or DESIGN
    n_lev = S.max() + 1
    dums = [(S[t_idx] == s).astype(float) for s in range(1, n_lev)]
    lags = [P[t_idx - 1, k] for k in range(P.shape[1]) if k != exclude_lag]
    cols = [np.ones(len(t_idx))] + dums + lags
    if design == "inter" and len(t_idx) >= 4 * (len(cols) + len(dums) * len(lags)):
        cols += [d * l for d in dums for l in lags]
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
def _absr(x, y):
    if x.std() == 0 or y.std() == 0:
        return 0.0
    return abs(np.corrcoef(x, y)[0, 1])


def _te_pairs(P, S, t_idx, i, j):
    out = []
    for a, b in ((i, j), (j, i)):
        Xb = _design(S, P, t_idx, exclude_lag=a)
        out.append((_resid(P[t_idx - 1, a], Xb), _resid(P[t_idx, b], Xb)))
    return out


def _strat_roll(y, S, s):
    """Circularly shift y by s *within* each public-state stratum (keeps the y-state relationship)."""
    out = y.copy()
    for lev in np.unique(S):
        idx = np.flatnonzero(S == lev)
        out[idx] = np.roll(y[idx], s % len(idx))
    return out


def _draw_shifts(n, rng, min_shift, tries=50):
    """4 offsets whose pairwise relative offsets (mod n) all lie in [min_shift, n - min_shift]."""
    for _ in range(tries):
        sh = rng.integers(0, n, size=4)
        rel = (sh[:, None] - sh[None, :]) % n
        off = rel[np.triu_indices(4, 1)]
        if np.all((off >= min_shift) & (off <= n - min_shift)):
            return sh
    return None


def score_run(P, S, B=200, seed=0, min_shift=3, min_draws=20):
    """Scores for all 6 pairs + calibrated p-values.

    Null: B draws, each circularly shifting every agent's series by its own random offset, with all
    pairwise relative offsets >= min_shift (same draw for all pairs). Raw-price stats use plain shifts;
    CMI|state shifts within each state stratum; pCMI/TE re-residualise the shifted residuals on the
    design (keeps orthogonality to state + lags). Per-pair p = P(null pair stat >= obs); run-level p =
    P(max_pair null >= max_pair obs) (max-statistic correction over the 6 pairs).
    If fewer than `min_draws` valid draws exist (very short T) all p-values are 1 (no test)."""
    rng = np.random.default_rng(seed)
    T = len(P)
    t_idx = np.arange(1, T)
    X = _design(S, P, t_idx)
    R = np.column_stack([_resid(P[t_idx, k], X) for k in range(4)])
    dP = np.diff(P, axis=0)
    te_res = {name: _te_pairs(P, S, t_idx, i, j) for (i, j), name in zip(PAIRS, PAIR_NAMES)}
    Xte = {name: [_design(S, P, t_idx, exclude_lag=a) for a in (i, j)] for (i, j), name in zip(PAIRS, PAIR_NAMES)}

    def stats(Pm, dPm, Rm, Pst, sh=None):
        d = {}
        for (i, j), name in zip(PAIRS, PAIR_NAMES):
            ri, rj = Rm[:, i], Rm[:, j]
            r = float(np.clip(np.mean(ri * rj), -0.999999, 0.999999))
            if sh is None:
                te = max(gauss_cmi_from_resid(a, b) for a, b in te_res[name])
            else:
                rel = int(sh[j] - sh[i])
                te = max(gauss_cmi_from_resid(a, _resid(np.roll(b, rel), Xd))
                         for (a, b), Xd in zip(te_res[name], Xte[name]))
            d[name] = {"pearson": _absr(Pm[:, i], Pm[:, j]),
                       "pearson_diff": _absr(dPm[:, i], dPm[:, j]),
                       "mi": mi_mm(Pm[:, i], Pm[:, j]),
                       "cmi_state": cmi_mm(Pst[:, i], Pst[:, j], S),
                       "pcmi": -0.5 * np.log(1 - r * r),
                       "te": te}
        return d

    obs = stats(P, dP, R, P)
    keys = list(obs[PAIR_NAMES[0]].keys())
    ge = {n: {k: 0 for k in keys} for n in PAIR_NAMES}
    ge_max = {k: 0 for k in keys}
    obs_max = {k: max(obs[n][k] for n in PAIR_NAMES) for k in keys}
    n_draws = 0
    for _ in range(B):
        sh = _draw_shifts(T - 1, rng, min_shift)
        if sh is None:
            continue
        n_draws += 1
        Ps = np.column_stack([np.roll(P[:, k], sh[k]) for k in range(4)])
        Pst = np.column_stack([_strat_roll(P[:, k], S, sh[k]) for k in range(4)])
        Rs = np.column_stack([_resid(np.roll(R[:, k], sh[k]), X) for k in range(4)])
        nd = stats(Ps, np.diff(Ps, axis=0), Rs, Pst, sh)
        for k in keys:
            mx = max(nd[n][k] for n in PAIR_NAMES)
            ge_max[k] += mx >= obs_max[k] - 1e-12
            for n in PAIR_NAMES:
                ge[n][k] += nd[n][k] >= obs[n][k] - 1e-12
    ok = n_draws >= min_draws
    pv = lambda c: (1 + c) / (1 + n_draws) if ok else 1.0
    out = {n: {"score": {k: float(v) for k, v in obs[n].items()},
               "p": {k: pv(ge[n][k]) for k in keys}} for n in PAIR_NAMES}
    run_p = {k: pv(ge_max[k]) for k in keys}
    # net influence: excess over mean of other pairs
    for key in ["mi", "cmi_state", "pcmi"]:
        vals = np.array([out[n]["score"][key] for n in PAIR_NAMES])
        for k, n in enumerate(PAIR_NAMES):
            out[n]["score"][f"ni_{key}"] = float(vals[k] - np.delete(vals, k).mean())
    out["_run_p"] = run_p
    out["_n_null"] = n_draws
    return out


def score_groups(P, S, B=200, seed=0, min_shift=3, min_draws=20):
    """Gaussian residual total correlation for all 2-, 3-, and 4-agent subsets.

    Uses score_run's design, residuals, shift draws, re-residualisation and
    finite-draw convention. `_run_p` contains separate max tests for tc2,
    tc3 and tc4 (no correction across subset sizes). Three-agent entries also
    contain `synergy` = TC minus the sum of their three pairwise pCMIs;
    this descriptive quantity has no p-value. Near-singular correlation
    matrices have eigenvalues floored at 1e-12. Pair correlations use the
    same 0.999999 clipping as pCMI, including at perfect dependence.
    """
    rng = np.random.default_rng(seed)
    t_idx = np.arange(1, len(P))
    X = _design(S, P, t_idx)
    R = np.column_stack([_resid(P[t_idx, k], X) for k in range(4)])
    groups = [g for size in (2, 3, 4) for g in itertools.combinations(range(4), size)]
    names = ["".join(AGENTS[k] for k in g) for g in groups]

    def stats(residuals):
        # _resid is already centred and standardised. Unit diagonals also
        # give the pCMI convention for a constant (zero-residual) column.
        corr = np.clip(residuals.T @ residuals / len(residuals), -0.999999, 0.999999)
        np.fill_diagonal(corr, 1.0)
        vals = []
        for g in groups:
            sub = corr[np.ix_(g, g)]
            tc = max(0.0, float(-0.5 * np.log(np.maximum(np.linalg.eigvalsh(sub), 1e-12)).sum()))
            if len(g) == 2:
                pcmi = gauss_cmi_from_resid(residuals[:, g[0]], residuals[:, g[1]])
                assert np.isclose(tc, pcmi, atol=1e-9, rtol=1e-9), (tc, pcmi)
                tc = float(pcmi)
            vals.append(tc)
        return np.array(vals)

    obs = stats(R)
    masks = {f"tc{size}": np.array([len(g) == size for g in groups]) for size in (2, 3, 4)}
    ge, ge_max = np.zeros(len(groups), int), {key: 0 for key in masks}
    n_draws = 0
    for _ in range(B):
        sh = _draw_shifts(len(P) - 1, rng, min_shift)
        if sh is None:
            continue
        shifted = np.column_stack([_resid(np.roll(R[:, k], sh[k]), X) for k in range(4)])
        null = stats(shifted)
        n_draws += 1
        ge += null >= obs - 1e-12
        for key, mask in masks.items():
            ge_max[key] += null[mask].max() >= obs[mask].max() - 1e-12
    pv = lambda count: float((1 + count) / (1 + n_draws)) if n_draws >= min_draws else 1.0
    out = {name: {"score": float(obs[i]), "p": pv(ge[i])} for i, name in enumerate(names)}
    for g, name in zip(groups, names):
        if len(g) == 3:
            pair_sum = sum(out["".join(AGENTS[k] for k in p)]["score"] for p in itertools.combinations(g, 2))
            out[name]["synergy"] = out[name]["score"] - pair_sum
    out["_run_p"] = {key: pv(count) for key, count in ge_max.items()}
    out["_n_null"] = n_draws
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
                    for n in PAIR_NAMES:  # "run_p": max-statistic run-level p (same for all pairs)
                        f.write(json.dumps({"run_id": rid, "pair": n, "score": pr[n]["score"][key],
                                            "p": pr[n]["p"].get(key),
                                            "run_p": pr["_run_p"].get(key)}) + "\n")
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset")
    ap.add_argument("--B", type=int, default=200)
    ap.add_argument("--out", default="results")
    a = ap.parse_args()
    run_detectors(a.dataset, a.B, a.out)
