"""Read-only check of Q1.4 numbers quoted in the merged SUBMISSION.md (zero LLM calls, no writes
outside results/reviews/merge_check.json).

    uv run python scripts/check_merge_sources.py [path/to/SUBMISSION.md]

For each check: (1) the saved JSON value, rounded, must equal the number we hand to the merge;
(2) the quoted string must appear in the merge draft (whitespace-normalised). Also greps the draft
for open merge flags (results/reviews/merge_flags.md) and for the overclaims DIRECTION lists.
Pinned JSON (e68_cda.json, e70_grid.json) must keep their SHA256.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVAL = ROOT / "results/eval"
DEFAULT = Path.home() / "collusion/collusion-beyond-words/SUBMISSION.md"

PINNED = {
    "e68_cda.json": "12045ea744443965e9c24414f6f8422cb2e4c90e21b9343efdf5e34353207374",
    "e70_grid.json": "bf0c0adcc644352babc9089140cbf816539e986ed9b1c11790ac898d34aed857",
}

# (id, file, key path, digits, expected value, string expected in SUBMISSION)
CHECKS = [
    ("grid_pcmi", "e70_grid.json", ["pooled_auroc", "pcmi", "auroc"], 2, 0.51, "0.51 [0.43, 0.59]"),
    ("grid_pcmi_ci", "e70_grid.json", ["pooled_auroc", "pcmi", "ci"], 2, [0.43, 0.59], "0.51 [0.43, 0.59]"),
    ("grid_te", "e70_grid.json", ["pooled_auroc", "te", "auroc"], 2, 0.62, "0.62 [0.54, 0.70]"),
    ("grid_te_ci", "e70_grid.json", ["pooled_auroc", "te", "ci"], 2, [0.54, 0.70], "0.62 [0.54, 0.70]"),
    ("grid_level", "e70_grid.json", ["pooled_auroc", "market_level", "auroc"], 2, 0.74, "0.74 [0.66, 0.81]"),
    ("grid_level_ci", "e70_grid.json", ["pooled_auroc", "market_level", "ci"], 2, [0.66, 0.81], "0.74 [0.66, 0.81]"),
    ("grid_n", "e70_grid.json", ["n_games"], None, 192, "192"),
    ("grid_level_gt_pcmi", "e70_grid.json", ["level_vs_pcmi", "cells_level_gt_pcmi"], None, 12, "12/16"),
    ("grid_CminusA_pos", "e70_grid.json", ["primary", "cells_d_pos"], None, 13, None),
    ("e74_k", "e74_paired_diff.json", ["summary", "k_level_minus_pcmi_ci_above_0"], None, 8, "8/9"),
    ("e74_point", "e74_paired_diff.json", ["summary", "point_level_gt_pcmi"], None, 9, "9/9"),
    ("e74_g56l_delta", "e74_paired_diff.json", ["summary", "smallest_delta", "delta"], 2, 0.03, "+0.03 [−0.27, +0.33]"),
    ("e74_g56l_ci", "e74_paired_diff.json", ["summary", "smallest_delta", "ci"], 2, [-0.27, 0.33], "+0.03 [−0.27, +0.33]"),
    ("e74_level_te_k", "e74_paired_diff.json", ["summary", "k_level_minus_te_ci_above_0"], None, 6, None),
    ("e70_level_minus_te", "e74_paired_diff.json", ["E70_pooled", "level_minus_te", "delta"], 2, 0.12, None),
    ("T60_pcmi", "e73_nonlinear.json", ["E44_T60", "pcmi", "auroc"], 2, 0.34, "0.34 [0.18, 0.52]"),
    ("T60_pcmi_ci", "e73_nonlinear.json", ["E44_T60", "pcmi", "ci"], 2, [0.18, 0.52], "0.34 [0.18, 0.52]"),
    ("T60_level", "p2_partc.json", ["llm_long_p2_T60", "auroc_market_level"], 2, 0.94, "0.94 [0.86, 1.00]"),
    ("T60_level_ci", "p2_partc.json", ["llm_long_p2_T60", "auroc_market_level_ci"], 2, [0.86, 1.0], "0.94 [0.86, 1.00]"),
    ("exec_n", "e73_nonlinear.json", ["executed_only", "n_executed"], None, 48, "48/149"),
    ("exec_pcmi", "e73_nonlinear.json", ["executed_only", "pcmi", "auroc"], 2, 0.42, "0.42 [0.33, 0.53]"),
    ("exec_pcmi_ci", "e73_nonlinear.json", ["executed_only", "pcmi", "ci"], 2, [0.33, 0.53], "0.42 [0.33, 0.53]"),
    ("exec_pair_level", "p2_partc.json", ["E64_pooled", "all sets", "pair_level", "executed", "auroc"], 2, 0.87, "0.87 [0.80, 0.94]"),
    ("exec_pair_level_ci", "p2_partc.json", ["E64_pooled", "all sets", "pair_level", "executed", "ci"], 2, [0.80, 0.94], "0.87 [0.80, 0.94]"),
    ("exec_market_level", "p2_partc.json", ["E64_pooled", "all sets", "market_level", "executed", "auroc"], 2, 0.99, None),
    ("copula_E70", "e73_nonlinear.json", ["E70", "copula_pcmi", "auroc"], 2, 0.53, "0.53 [0.44, 0.61]"),
    ("copula_E70_ci", "e73_nonlinear.json", ["E70", "copula_pcmi", "ci"], 2, [0.44, 0.61], "0.53 [0.44, 0.61]"),
    ("sign_E70", "e73_nonlinear.json", ["E70", "sign_mi", "auroc"], 2, 0.44, "0.44 [0.36, 0.52]"),
    ("sign_E70_ci", "e73_nonlinear.json", ["E70", "sign_mi", "ci"], 2, [0.36, 0.52], "0.44 [0.36, 0.52]"),
    ("T60_comove_ci", "long_power_llm_long_p2_T60.json", ["mde", "60", "observed_C_comove_excess", "ci"], 3, [-0.007, 0.015], "+0.004 [−0.007, +0.015]"),
    ("T60_q01", "long_power_llm_long_p2_T60.json", ["mde", "60", "by_q", "0.1", "auroc"], 2, 0.79, "0.79 [0.70, 0.88]"),
    ("T60_q01_ci", "long_power_llm_long_p2_T60.json", ["mde", "60", "by_q", "0.1", "ci"], 2, [0.70, 0.88], "0.79 [0.70, 0.88]"),
    ("T20_q01", "long_power_llm_long_p2_T60.json", ["mde", "20", "by_q", "0.1", "auroc"], 2, 0.62, "0.62 [0.52, 0.71]"),
    ("T20_q01_ci", "long_power_llm_long_p2_T60.json", ["mde", "20", "by_q", "0.1", "ci"], 2, [0.52, 0.71], "0.62 [0.52, 0.71]"),
    ("qb36_pcmi", "e74_paired_diff.json", ["main_sets", "llm_qb36_p2", "pcmi"], 2, 0.71, "0.71 [0.51, 0.88]"),
]

# Open flags: the string that must disappear from SUBMISSION for the flag to count as applied.
FLAGS = {
    "F1 (P1)": "not a pure power failure",
    "F2 (P2)": None,  # abstract count wording: judged by hand
    "F3 (P2)": "(inflated by construction) | 0.42",
}
WATCH = ["pCMI cannot detect", "no co-movement exists", "TE detects collusion", "transfer entropy detects",
         "executed collusion is undetectable", "one shared market", "same market", "causes", "caused by"]


def norm(s):
    return re.sub(r"\s+", " ", s)


def rnd(x, d):
    if isinstance(x, list):
        return [rnd(v, d) for v in x]
    return x if d is None else round(x + 0.0, d)


def main():
    sub_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    sub = norm(sub_path.read_text())
    try:
        head = subprocess.run(["git", "-C", str(sub_path.parent), "log", "-1", "--format=%h"],
                              capture_output=True, text=True).stdout.strip()
    except OSError:
        head = "?"
    fails, missing = [], []
    for name, h in PINNED.items():
        if hashlib.sha256((EVAL / name).read_bytes()).hexdigest() != h:
            fails.append(f"pinned {name} changed")
    cache = {}
    for cid, f, path, d, exp, quote in CHECKS:
        doc = cache.setdefault(f, json.loads((EVAL / f).read_text()))
        v = doc
        for k in path:
            v = v[k]
        if rnd(v, d) != exp:
            fails.append(f"{cid}: json {rnd(v, d)} != {exp}")
        if quote and norm(quote) not in sub:
            missing.append(f"{cid}: '{quote}' not found in SUBMISSION")
    flags = {k: ("n/a (manual)" if s is None else ("open" if norm(s) in sub else "applied"))
             for k, s in FLAGS.items()}
    watch = [w for w in WATCH if w.lower() in sub.lower()]
    out = {"submission": str(sub_path), "merge_head": head, "n_checks": len(CHECKS),
           "json_mismatches": fails, "quotes_not_found": missing, "flags": flags, "watch_hits": watch}
    (ROOT / "results/reviews/merge_check.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps(out, indent=1, ensure_ascii=False))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
