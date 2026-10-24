"""Render E70/E68 manuscript fragments AFTER their registered analyses, from saved JSON only.

uv run python scripts/p2_landing.py e70 --part all
uv run python scripts/p2_landing.py e68 --part all

Nothing is analysed or written. This never opens trajectories, asks, judge caches, or a live
sibling repo. Missing result JSON fails; generation/completion gates belong to the analyses.
Use --input PATH for synthetic fixtures. Default output is the replacement P2 section;
--part all also prints separately labelled abstract/denominator/glance/appendix fragments.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from p2_tables import p212, p214
from report_tables import table

ROOT = Path(__file__).resolve().parent.parent


def finite(value):
    """Reject non-finite JSON numbers rather than publishing nan/inf in a manuscript."""
    if isinstance(value, dict):
        for v in value.values():
            finite(v)
    elif isinstance(value, list):
        for v in value:
            finite(v)
    elif isinstance(value, float) and not math.isfinite(value):
        raise ValueError("non-finite result number")


def interval(value, ci, signed=False):
    spec = "+.2f" if signed else ".2f"
    return f"{value:{spec}} [{ci[0]:{spec}}, {ci[1]:{spec}}]".replace("-", "−")


def pvalue(value):
    return "not evaluable (all ties)" if value is None else f"{value:.3g}"


def e70(d):
    finite(d)
    s, n = d["complete_sweeps"], d["n_games"]
    pc, p, lv = d["per_cell"], d["primary"], d["level_vs_pcmi"]
    if type(s) is not int or not 1 <= s <= 6:
        raise ValueError("expected 1–6 complete sweeps")
    if set(pc) != {f"c{i:02d}" for i in range(16)} or p["cells"] != 16 or lv["cells"] != 16:
        raise ValueError("expected the registered 16 cells")
    if n != 32 * s or any(v["n"] != [s, s] for v in pc.values()):
        raise ValueError("game counts do not match balanced complete sweeps")
    if any(not 0 <= v["executed"] <= v["labelled"] <= s for v in pc.values()):
        raise ValueError("invalid execution/label denominator")
    # Counts come from the analysis's UNROUNDED comparisons. Recounting rounded per-cell
    # d/AUROC fields could silently convert small positive effects or wins into ties.
    if not 0 <= p["cells_d_pos"] <= 16 or not 0 <= lv["cells_level_gt_pcmi"] <= 16 - lv["ties"] <= 16:
        raise ValueError("invalid cell denominator")
    if sum(v["labelled"] for v in pc.values()) != d["executed"]["labelled"]:
        raise ValueError("execution label denominator mismatch")
    if sum(v["executed"] for v in pc.values()) != d["executed"]["k"]:
        raise ValueError("execution count mismatch")
    state = "full declared set" if s == 6 else "deadline-truncated balanced sample"
    k, w = p["cells_d_pos"], lv["cells_level_gt_pcmi"]
    pooled = "; ".join(f"{key} {interval(v['auroc'], v['ci'])}" for key, v in d["pooled_auroc"].items())
    q = d["amend2_qwen_pcmi_replication"]
    model = "; ".join(f"{m} {interval(v['level_minus_pcmi'], v['level_minus_pcmi_ci'], True)}"
                      for m, v in d["amend2_by_model"].items())
    board = "; ".join(f"{m} {v['no_channel']:.1%} / {v['channel']:.1%}"
                      for m, v in d["amend2_board_share"].items())
    excluded = sum(d["excluded_model_mismatch"].values())
    # Five prose paragraphs, plus the existing checked table and figure.
    paragraphs = [
        f"**P2.14 Factorial grid (E70, Part E1; registered in `results/e1_registration.md`).** "
        f"{s} complete sweeps, {n} games ({state}), T = 20, 16 designs, four sellers, public board available. "
        "Resolution IV; main effects alias with interactions of three or more factors; private/public cost substitutes for firm count.",
        f"**Generality:** C − A markup has a positive point estimate in **{k}/16 cells** "
        f"(sign test p = {pvalue(p['sign_test_p'])}); pooled C − A "
        f"{interval(p['pooled_C_minus_A'], p['pooled_ci'], True)}. "
        f"Market level beats pCMI in **{w}/16 cells** ({lv['ties']} ties; sign test excluding ties "
        f"p = {pvalue(lv['sign_test_p_excl_ties'])}). These are counts of point estimates, not per-cell CI tests.",
        f"Within-cell pooled AUROCs [game-bootstrap 95% CI]: {pooled}. "
        f"Secondary TE hypothesis: **{d['te_confirmatory']['verdict']}**. "
        f"Qwen-cell pCMI replication of E69: {interval(q['auroc'], q['ci'])}, **{q['verdict']}**; "
        f"level − pCMI AUROC by model: {model}.",
        f"Public-board usage (non-empty agent-rounds, no-channel / channel): {board}. "
        "Factor M includes model and its board use. Read luna factor contrasts as board-available conditions "
        "with the measured usage above; availability alone does not establish use. Per-cell usage is in the E70 saved table.",
        f"Rival spillover {interval(d['spillover']['pooled'], d['spillover']['ci'], True)}; "
        f"executed {d['executed']['k']}/{d['executed']['labelled']} labelled channel games "
        f"({16 * s - d['executed']['labelled']} unlabelled); {excluded} fallback/model-mismatch games excluded. "
        "Seven main-effect contrasts below are descriptive, without multiplicity correction. "
        "The separately saved follow-up decision and fresh-sample result determine confirmation.",
    ]
    section = "\n\n".join(paragraphs) + "\n\n" + p214(data=d) + "\n\n![E70 factorial grid](figures/e70_grid.png)"
    appendix = table(["cell", "model", "n A/C", "C − A point estimate", "level / pCMI AUROC", "board A/C"], [
        [c, v["levels"]["model"], f"{v['n'][0]}/{v['n'][1]}", f"{v['d']:+.3f}",
         f"{v['auroc']['market_level']:.3f} / {v['auroc']['pcmi']:.3f}",
         f"{v['board_share']['no_channel']:.1%} / {v['board_share']['channel']:.1%}"] for c, v in pc.items()])
    abstract = (f"Across E70's 16 designs ({s} complete sweeps), channel markup was positive in {k}/16 "
                f"and market-level AUROC exceeded pCMI in {w}/16 cells (point estimates).")
    return dict(section=section, abstract=abstract,
                denominators=f"E70 adds (+ {k}/16 cells with positive C − A point estimates; "
                f"level > pCMI {w}/16). Its per-cell positive-CI and pCMI-above-chance counts were not computed; "
                "do not append the positive-point count to P2.13's positive-CI row.",
                appendix=appendix,
                completion="6 sweeps complete" if s == 6 else f"{s} complete sweeps analysed at the declared deadline")


def e68(d):
    finite(d)
    c, n = d["n_comms"], d["n_nocomms"]
    m, pf, flags = d["manipulation_check"], d["parse_failures"], d["pcmi_flags_alpha05"]
    if min(c, n) < 1 or c > 15 or n > 15 or d["complete"] != (c == n == 15):
        raise ValueError("invalid D2 full/interim sample counts")
    if pf["n_runs"] != c + n or flags[1::2] != [c, n]:
        raise ValueError("D2 denominator mismatch")
    counts = (m["n_matched_seeds"], m["n_unmatched_comms"], m["n_unmatched_nocomms"])
    if counts[0] + counts[1] != c or counts[0] + counts[2] != n:
        raise ValueError("D2 seed counts do not match arms")
    effect = interval(m["diff"], m["ci"], True)
    sample = "full declared set" if d["complete"] else "deadline-truncated interim sample"
    section = "\n\n".join([
        f"**P2.12 External continuous double auction (E68, Part D2).** qwen-3.6-35b; "
        f"{c} comms / {n} nocomms games ({sample}), three sellers and two buyers, 30 rounds. "
        "Frozen detectors; withdrawn asks forward-filled and leading gaps back-filled. "
        "Levels use second-half asks minus CE 80; trade uses actual transaction prices.",
        f"Declared manipulation check, all-round mean ask − 80: comms − nocomms **{effect}**, "
        f"{m['bootstrap_draws']}-draw {m['bootstrap']} bootstrap; {counts[0]} matched seeds, "
        f"{counts[1]} / {counts[2]} unmatched comms / nocomms. Gate: {m['status']}; "
        f"**{d['verdict']}**. A positive ask effect alone would not verify an agreement.",
        f"Parse failures: {pf['total']} in {pf['runs_with_any']}/{pf['n_runs']} runs. "
        f"pCMI max-pair shift-null flags at α = 0.05: comms {flags[0]}/{flags[1]}, "
        f"nocomms {flags[2]}/{flags[3]}. Trade AUROCs exclude games without second-half trades; "
        "the table reports their effective sample sizes.",
    ]) + "\n\n" + p212(data=d)
    row = (f"| D2 | external double auction | {c}/{n} comms/nocomms; ask effect {effect}; "
           f"{d['verdict']}; {pf['total']} parse failures in {pf['runs_with_any']}/{pf['n_runs']} runs "
           "| `eval/e68_cda.json` | P2.12 |")
    return dict(section=section, glance=row,
                abstract=f"In the external double auction ({c}/{n} games), the declared verdict was "
                f"“{d['verdict']}” (all-round ask effect {effect}).")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("experiment", choices=("e70", "e68"))
    ap.add_argument("--input", type=Path)
    ap.add_argument("--part", default="section", choices=("all", "section", "abstract", "denominators", "appendix", "completion", "glance"))
    a = ap.parse_args()
    source = a.input or ROOT / "results/eval" / ("e70_grid.json" if a.experiment == "e70" else "e68_cda.json")
    fragments = {"e70": e70, "e68": e68}[a.experiment](json.loads(source.read_text()))
    if a.part == "all":
        print("\n\n".join(f"### {key}\n\n{value}" for key, value in fragments.items()))
    elif a.part in fragments:
        print(fragments[a.part])
    else:
        ap.error(f"{a.part} is not available for {a.experiment}")


if __name__ == "__main__":
    main()
