"""Render and check the quantitative results tables in REPORT.md from committed inputs.

No experiments, LLM calls, or result files are written. The narrative overview and pilot
history are outside this check; their sources are the detailed results and pilot trajectories.
Run via ``uv run python scripts/tables.py --check`` or ``--report``.
"""
from __future__ import annotations

import contextlib
import io
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from experiments.scripted import wilson  # noqa: E402

DETS = ["pcmi", "mi", "te", "pearson", "pair_level", "market_level"]
NAMES = ["pCMI (state+lags)", "MI (raw prices)", "lagged CMI (TE)", r"\|Pearson\|",
         "pair_level (non-IT)", "markup over Nash (non-IT)"]
EXTRA_DETS = DETS[:4] + ["mi_diff", "pearson_diff1"] + DETS[4:]
EXTRA_NAMES = NAMES[:4] + ["MI first differences", r"\|Pearson\| first differences"] + NAMES[4:]


def load(name):
    return json.loads((ROOT / "results" / "eval" / f"{name}.json").read_text())


def ci(x, bounds, signed=False, digits=2):
    # REPORT uses unsigned bounds for price premiums, signed bounds for contrasts.
    spec = f"+.{digits}f" if signed else f".{digits}f"
    return f"{x:{spec}} [{bounds[0]:{spec}}, {bounds[1]:{spec}}]"


def auc(x):
    return ci(x["auroc"], x["ci"])


def table(header, rows):
    return "\n".join("| " + " | ".join(map(str, r)) + " |" for r in
                     [header, ["---"] * len(header), *rows])


def parse_tables(text, include_header=False):
    """Only fenced-by-header Markdown tables, splitting unescaped pipes."""
    lines = text.splitlines()
    out = []
    for i, line in enumerate(lines[:-1]):
        if not line.startswith("|") or not re.fullmatch(r"\|[\s:|\-]+\|", lines[i + 1]):
            continue
        rows = [[c.strip() for c in re.split(r"(?<!\\)\|", line.strip()[1:-1])]] if include_header else []
        for row in lines[i + 2:]:
            if not row.startswith("|"):
                break
            rows.append([c.strip() for c in re.split(r"(?<!\\)\|", row.strip()[1:-1])])
        out.append(rows)
    return out


def gate():
    # Retain the established formatter and its Wilson interval rounding.
    from scripts.tables import gate as legacy_gate
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        legacy_gate()
    return out.getvalue().split("\n\n", 1)[1].split("\n\n", 1)[0].replace("| group |", "| group (no collusion above the line) |", 1)


def sweep():
    data = json.loads((ROOT / "results/sweeps/power_test.json").read_text())["rows"]

    def select(kind, T, s):
        return next(r["metrics"] for r in data if (r["type"], r["T"], r["strength"]) == (kind, T, s))

    def rate(m, det, groups="CD", key="flag_rate"):
        return sum(m[det][c][key] for c in groups) / len(groups)

    def cells(kind, T, s):
        m = select(kind, T, s)
        return ([f"{rate(m, d):.2f} / {rate(m, d, 'AB'):.2f}" for d in ["mi", "cmi_state", "pcmi", "te"]]
                + [f"{rate(m, 'pcmi', key='top1'):.2f} / {rate(m, 'te', key='top1'):.2f}"])

    def upper(v):
        return f"≤{math.ceil((max(v) - 1e-12) * 100) / 100:.2f}"

    def lower(v):
        return f"≥{math.floor((min(v) + 1e-12) * 100) / 100:.2f}"

    rows = [["shared signal", "T=100, s=0.1", *cells("signal", 100, .1)]]
    ms = [r["metrics"] for r in data if r["type"] == "signal" and r["T"] == 100 and r["strength"] >= .2]
    # These compact cells assert that all selected points have the same value.
    def constant(d, groups="CD", key="flag_rate"):
        vals = [rate(m, d, groups, key) for m in ms]
        if max(vals) - min(vals) > 1e-12:
            raise ValueError(f"sweep summary is no longer constant: {d}, {groups}")
        return f"{vals[0]:.2f}"
    rows.append(["shared signal", "T=100, s≥0.2",
                 *[f"{constant(d)} / {constant(d, 'AB')}" for d in ["mi", "cmi_state", "pcmi"]],
                 f"{upper([rate(m, 'te') for m in ms])} / {constant('te', 'AB')}",
                 f"{constant('pcmi', key='top1')} / {upper([rate(m, 'te', key='top1') for m in ms])}"])
    for T in [10, 20, 50]:
        row = cells("signal", T, .3)
        if T == 10:
            row[:4] = ["0 / 0"] * 4
            row[2] += " (no test: <20 valid shifts)"
            # Verify the displayed zero tests rather than silently hardcoding them.
            if any(rate(select("signal", T, .3), d, g) != 0 for d in ["mi", "cmi_state", "pcmi", "te"] for g in ["CD", "AB"]):
                raise ValueError("T=10 sweep unexpectedly performs a nonzero test")
        rows.append(["shared signal", f"T={T}, s=0.3", *row])
    rows.append(["tit-for-tat", "T=100, s=0.2", *cells("tft", 100, .2)])
    ms = [r["metrics"] for r in data if r["type"] == "tft" and r["T"] == 100 and r["strength"] >= .45]
    mi = [rate(m, "mi") for m in ms]
    rows.append(["tit-for-tat", "T=100, s≥0.45", f"{min(mi):.2f}–{max(mi):.2f} / {constant('mi', 'AB')}",
                 *[f"{upper([rate(m, d) for m in ms])} / {constant(d, 'AB')}" for d in ["cmi_state", "pcmi"]],
                 f"{lower([rate(m, 'te') for m in ms])} / {constant('te', 'AB')}",
                 f"{upper([rate(m, 'pcmi', key='top1') for m in ms])} / {lower([rate(m, 'te', key='top1') for m in ms])}"])
    a, b = cells("tft", 20, .3), cells("tft", 50, .3)
    rows.append(["tit-for-tat", "T=20 / 50, s=0.3", a[0] + " ; " + b[0],
                 a[1].split(" / ")[0] + " ; " + b[1].split(" / ")[0],
                 a[2].split(" / ")[0] + " ; " + b[2].split(" / ")[0], a[3] + " ; " + b[3], a[4] + " ; " + b[4]])
    rows.append(["stay-high (no shared variation)", "T=100, s=0.8", *cells("fixed_high", 100, .8)])
    return table(["collusion type", "setting", "MI (coll./ctrl)", r"CMI\|state", "pCMI", "TE", "pair top-1 pCMI / TE"], rows)


def external():
    d = load("llm_v3_ext")["detectors"]
    rows = []
    for det, name in zip(DETS, NAMES):
        r = d[det]
        def top(k):
            x = r[k]
            return f"{x['k']}/{x['n']} (p={x['binom_p_vs_1/6']:.2g}, {x['n_tied_runs']} tied)"
        rows.append([name, *[auc(r["auroc_" + k]) for k in ["private_vs_none", "agreement_vs_none", "legit_vs_none"]],
                     top("top1_private"), top("top1_private_agreement")])
    return table(["detector", "AUROC private vs none", "AUROC agreement vs none", "AUROC legit vs none", "top-1, private", "top-1, agreement"], rows)


def labels():
    gt = [json.loads(l) for l in (ROOT / "data/llm_v1/ground_truth.jsonl").read_text().splitlines()]
    names = ["A no channel", "B no channel + shocks", "C pair channel", "D pair channel + shocks"]
    rows = []
    for c, name in zip("ABCD", names):
        gs = [g for g in gt if g["condition"] == c]
        def count(key, interval):
            v = [g[key] for g in gs if g.get(key) is not None]
            if not v:
                return "—"
            out = f"{sum(v)}/{len(v)}"
            if interval:
                lo, hi = wilson(v)
                out += f" [{lo:.2f}, {hi:.2f}]"
            if len(v) != len(gs):
                out += f" (+{len(gs) - len(v)} n/a)"
            return out
        # The report combines these two identical label columns.
        if any(g.get("coordinated_actions_verified") != g.get("realized_collusion") for g in gs):
            raise ValueError("realised and coordinated labels no longer agree")
        rows.append([name, len(gs), count("agreement_verified", c in "CD"),
                     count("coordinated_actions_verified", c in "CD"), count("tacit_supracompetitive", True)])
    return table(["condition", "n", "agreement verified", "coordinated actions (= realised)", "tacit supra-competitive"], rows)


def main_llm():
    d = load("llm_v1")["by_T"]["20"]
    names = ["pCMI (state+lags)", "MI (raw)", "lagged CMI (TE)", r"\|Pearson\|",
             "pair price level (non-IT)", "max-pair markup over Nash (non-IT)"]
    rows = []
    for det, name in zip(DETS, names):
        r = d[det]
        top = " / ".join(f"{round(r[c]['top1'] * r[c]['n'])}/{r[c]['n']}" for c in "CD") if det != "pearson" else "—"
        rows.append([name, ci(r["auroc_CD_vs_AB"], r["auroc_ci"]),
                     *[ci(r["auroc_" + k], r["auroc_ci_" + k]) for k in ["C_vs_A", "D_vs_B"]], top])
    return table(["detector", "C/D vs A/B", "C vs A", "D vs B", "top-1 assigned pair C / D (chance 1/6)"], rows)


def mixed():
    d = load("llm_mixed2_mixed")
    names = ["pCMI", r"MI (= CMI\|state here: one state)", "TE", r"\|Pearson\|"]
    rows = []
    for det, name in zip(DETS[:4], names):
        r = d[det]["per_run_same_minus_cross"]
        flag = ", ".join(f"{round(d[det][k]['pair_flag_rate'] * d[det][k]['n_pairs'])}/{d[det][k]['n_pairs']}"
                         for k in ["same_big", "same_base", "cross"])
        if det == "pearson":
            flag += r" (raw \|r\| is not calibrated on trending prices)"
        rows.append([name, ci(r["mean"], r["mean_ci"], True, 3), f"{r['n_positive']}/{r['n_runs']}",
                     f"{r['sign_test_p']:.2f}", flag])
    return table(["detector", "same − cross (mean) [95% CI]", "runs with same > cross", "sign p",
                  "pair flag rate, shift null: same-sol / same-luna / cross"], rows)


def longer():
    d = load("llm_long")["by_T"]
    rows = []
    for det, name in [("pcmi", "pCMI run AUROC C vs A"), ("mi", "MI"), ("te", "TE"),
                      ("pair_level", "pair_level (non-IT)"), ("market_level", "markup over Nash (non-IT)")]:
        cells = [f"{d[str(t)][det]['auroc_C_vs_A']:.2f}" for t in [10, 20, 30, 40]]
        r = d["50"][det]
        rows.append([name, *cells, ci(r["auroc_C_vs_A"], r["auroc_ci_C_vs_A"])])
    rows.append(["pCMI top-1 in C (of 8)", *[str(round(d[str(t)]["pcmi"]["C"]["top1"] * d[str(t)]["pcmi"]["C"]["n"])) for t in [10, 20, 30, 40, 50]]])
    return table(["T (same games, prefixes)", "10", "20", "30", "40", "50"], rows)


def injection():
    rows = []
    for r in load("injection_mde"):
        cells = []
        for q in [.1, .2, .3, .5]:
            x = r["by_q"][str(q)]
            a = ci(x["auroc_single_planting"], x["auroc_ci_game_cluster"]) if q <= .2 else f"{x['auroc_single_planting']:.2f}"
            cells.append(a + f" ({x['comove_excess_mean']:+.2f})")
        cond, obs = next(iter(r["observed"].items()))
        rows.append([f"`{r['dataset']}` {r['controls']} ({r['n_controls']})", str(r["T"]), *cells,
                     f"{cond}: " + ci(obs["comove_excess_mean"], obs["ci"], True, 3)])
    return table(["background (controls)", "T", "q = 0.1", "q = 0.2", "q = 0.3", "q = 0.5",
                  "observed co-move excess of assigned pair in channel games [95% CI]"], rows)


def placebo():
    d = load("placebo_rep_ext")["detectors"]
    rows = []
    for det, name in zip(EXTRA_DETS, EXTRA_NAMES):
        r = d[det]
        top = [f"{r[k]['hits']:.1f}/{r[k]['n']}" for k in ["top1_private", "top1_placebo"]]
        x = r["top1_private_minus_placebo"]
        rows.append([name, *top, ci(x["diff"], x["ci"], True) + f"; p={x['p_signflip_exact']:.2g}",
                     *[auc(r["auroc_" + k]) for k in ["private_vs_none", "placebo_vs_none", "private_vs_placebo"]]])
    return table(["detector", "top-1 private", "top-1 placebo", "private − placebo (matched)",
                  "AUROC private vs none", "AUROC placebo vs none", "AUROC private vs placebo"], rows)


def nonagreement():
    d = load("nonagreement_ext")["detectors"]
    rows = []
    for det, name in zip(EXTRA_DETS, EXTRA_NAMES):
        r = d[det]
        cells = [f"{r[k]['hits']:.1f}/{r[k]['n']} (p={r[k]['p_vs_1/6']:.2g})" for k in ["top1_mon", "top1_fp", "top1_pooled"]]
        rows.append([name, *cells, auc(r["auroc_mon_private_vs_none"])])
    return table(["detector", "top-1 `llm_v3mon` (monitor)", "top-1 `llm_v3fp` (firm)", "top-1 pooled",
                  "AUROC `llm_v3mon` private vs none"], rows)


def preplay():
    d = load("preplay_offer")
    labels = ["(a1) **first sender's** provisional price − rivals' round-0 price (no partner message read)",
              "(a) pair-mean provisional price − rivals' round-0 price (declared quantity)",
              "(b) pair round-0 price − rivals' round-0 price", "(c) pair − rivals, whole game (§4.3.4)"]
    keys = ["first_sender_provisional_minus_rivals_r0", "offer_premium_provisional_minus_rivals_r0",
            "round0_premium_pair_minus_rivals", "full_game_premium_pair_minus_rivals"]
    def premium(r):
        return f"{r[0]:+.2f} [{r[1][0]:.2f}, {r[1][1]:.2f}]"
    rows = [[lab, *[premium(d[n][k]) for n in ["llm_v1", "llm_long"]]] for lab, k in zip(labels, keys)]
    def au(n, k):
        r = d[n][f"round0_markup_auroc_{k}"]
        return ci(r[0], r[1])
    rows.append(["round-0 market markup over Nash, run AUROC C vs A / D vs B",
                 au("llm_v1", "C_vs_A") + " / " + au("llm_v1", "D_vs_B"), au("llm_long", "C_vs_A") + " (C vs A)"])
    return table(["", f"`llm_v1` C+D ({d['llm_v1']['n_runs']} games)", f"`llm_long` C ({d['llm_long']['n_runs']} games)"], rows)


BUILDERS = {"4.1": gate, "4.2": sweep, "4.3.3": external, "4.3.4-labels": labels,
            "4.3.4-detectors": main_llm, "4.3.5": mixed, "4.3.6": longer,
            "4.3.8": injection, "4.3.9": placebo, "4.3.10": nonagreement, "4.3.11": preplay}


def normalized(cell):
    # Ignore typography only. Keep numbers, signs, bounds, labels, and annotations.
    return re.sub(r"\s+", "", cell.replace("**", "").replace("`", "").replace("−", "-").replace("\\|", "|"))


def check(report):
    # Phase 2 tables (glance block and "## Phase 2 details") are checked by scripts/p2_tables.py, not here.
    for start, end in (("## Phase 2 at a glance", "## v1 (overnight) key findings"),
                       ("## Phase 2 details", "## 5. Limitations"), ("## Phase 2 results", "## Abstract")):
        if start in report and end in report:
            a, b = report.index(start), report.index(end)
            report = report[:a] + report[b:]
    blocks = parse_tables(report, include_header=True)
    # Overview and pilot-history tables are narrative summaries, not result tables.
    if len(blocks) != len(BUILDERS) + 2:
        raise ValueError(f"Expected {len(BUILDERS) + 2} REPORT tables, found {len(blocks)}; update coverage explicitly")
    blocks = blocks[1:3] + blocks[4:]
    errors, cells = [], 0
    for (section, build), actual in zip(BUILDERS.items(), blocks):
        expected = parse_tables(build(), include_header=True)[0]
        if len(actual) != len(expected):
            errors.append(f"§{section}: expected {len(expected)} rows, found {len(actual)}")
            continue
        for i, (a, e) in enumerate(zip(actual, expected), 1):
            if len(a) != len(e):
                errors.append(f"§{section}, row {i}: expected {len(e)} cells, found {len(a)}")
                continue
            for j, (av, ev) in enumerate(zip(a, e), 1):
                cells += int(i > 1)
                if normalized(av) != normalized(ev):
                    errors.append(f"§{section}, row {i}, cell {j}: {av!r} != generated {ev!r}")
    for error in errors:
        print("FAIL:", error)
    print(f"{'FAIL' if errors else 'PASS'}: {len(BUILDERS)} quantitative results tables (headers and {cells} body cells); "
          "overview and pilot history excluded")
    return not errors


def render():
    for section, build in BUILDERS.items():
        print(f"### REPORT §{section}\n\n{build()}\n")
