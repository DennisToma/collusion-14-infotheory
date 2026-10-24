"""Regenerate and check the Markdown tables in REPORT.md "## Phase 2 results" from committed JSON.

No experiments or LLM calls; nothing is written. Every number in a cell comes from JSON in results/;
only row labels / annotation words are literal text here.
    uv run python scripts/p2_tables.py          # print regenerated tables
    uv run python scripts/p2_tables.py --check  # compare cell by cell with REPORT.md (exit 1 on failure)
Tables: P2.1 prevalence, P2.3 same-model, P2.4 coalitions/cost asymmetry, P2.5 market robustness, P2.6 rotation, P2.7 prompt wording, P2.9 family, P2.10 sibling arms, P2.11 part C.
"""
from __future__ import annotations

import contextlib
import io
import json
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from report_tables import normalized, parse_tables, table  # noqa: E402

# Cells in the Phase 2 tables that cannot be derived from JSON (none at present).
UNCHECKED: list[str] = []
# Not tables: P2.4 onset (E50, results/p2/onset_test.json) is reported in prose only, so it is not checked here.


def jl(path):
    return json.loads((ROOT / path).read_text())


def k30(d):
    return round(d["rate"] * d["n"]) if "n" in d else round(d["rate"] * 30)


# ---------------------------------------------------------------- P2.1
def p21():
    rows = jl("results/eval/prevalence.json")

    def find(setting, det, null, neg):
        m = [r for r in rows if r["setting"].startswith(setting) and r["detector"] == det and r["null"] == null and r["neg"] == neg]
        assert len(m) == 1, (setting, det, null, neg, len(m))
        return m[0]

    def prec(r, with_ci=True):
        out = []
        for pi in ("0.01", "0.05", "0.2"):
            p, ci = r[f"precision@{pi}"], r[f"precision@{pi}_ci"]
            out.append(f"{p:.2f} [{ci[0]:.2f}, {ci[1]:.2f}]" if with_ci else f"{p:.2f}")
        return out

    spec = [  # (label setting, label detector, setting key, det, null, neg, neg label, ci?)
        ("scripted, T=100", "pCMI (shift)", "scripted gate_test", "pcmi", "shift", "A", "independent", True),
        ("scripted, T=100", "pCMI (shift)", "scripted gate_test", "pcmi", "shift", "B", "common shock", True),
        ("scripted, T=100", "pCMI (shift)", "scripted gate_test", "pcmi", "shift", "A+shared_seed", "shared-seed copies", True),
        ("scripted, T=100", "MI (shift)", "scripted gate_test", "mi", "shift", "B", "common shock", False),
        ("`llm_v1`, T=20", "pCMI (shift)", "LLM llm_v1", "pcmi", "shift", "A+B", "A+B controls", True),
        ("`llm_v1`, T=20", "pair_level (surrogate)", "LLM llm_v1", "pair_level", "surrogate", "A+B", "A+B)\\*", True),
        ("sibling `llm_v3`, T=12", "pair_level (surrogate)", "LLM sibling llm_v3", "pair_level", "surrogate", "legit", "legit partnership", True),
    ]
    out = []
    for ls, ld, sk, det, null, neg, nl, ci in spec:
        r = find(sk, det, null, neg)
        fp = f"{r['fp'][0]}/{r['fp'][1]} ({nl})" if not nl.endswith("\\*") else f"{r['fp'][0]}/{r['fp'][1]} ({nl}"
        out.append([ls, ld, f"{r['tp'][0]}/{r['tp'][1]}", fp, *prec(r, ci)])
    return table(["setting", "detector (null)", "TPR", "FPR (negative type)", "precision @ 1%", "@ 5%", "@ 20%"], out)


# ---------------------------------------------------------------- P2.3
def p23():
    a = jl("results/eval/same_model.json")["auroc"]
    cols = ["pcmi", "pcmi_ownlag", "mi", "pair_level", "pair_markup"]
    labels = [("channel_all|luna-luna", "luna–luna, no channel (same model as colluders)"),
              ("channel_all|sol-sol", "sol–sol, no channel"),
              ("channel_all|cross", "luna–sol cross, no channel"),
              ("channel_all|bystander", "same-market bystander pairs")]
    rows = [[lab, *[f"{a[key][c][0]:.2f} [{a[key][c][1][0]:.2f}, {a[key][c][1][1]:.2f}]" for c in cols]] for key, lab in labels]
    return table(["channel-assigned pair vs …", "pCMI", "pCMI, own lag only", "MI", "pair_level", "pair markup over Nash"], rows)


# ---------------------------------------------------------------- P2.4
def p24():
    co = jl("results/p2/coalition_test.json")["summaries"]
    ca = jl("results/p2/costasym_test.json")["summaries"]

    def ab(key, m, bold=False):
        s = f"{k30(co['A/' + key][m])}/30, {k30(co['B/' + key][m])}/30"
        return f"**{s}**" if bold else s

    def tc(key):
        s = ab(key, "tc4_flag")
        if ab(key, "tc3_flag") != s:  # the table shows one pair of counts for TC4 / TC3
            s += f" [TC3 {ab(key, 'tc3_flag')}]"
        return s

    def f(m, key="A/costasym"):
        return k30(ca[key][m])

    ctrl = (f"pCMI {ab('control', 'pcmi_flag')}; TC4 {ab('control', 'tc4_flag')}; "
            f"pair_level {ab('control', 'pair_level_surrogate_flag')}")
    au = [co[f"{fam}/coalition4"]["auroc_vs_control"]["pair_level"]["auc"] for fam in "AB"]
    rows = [
        ["3 of 4 collude (A / B)", ab("coalition3", "pair_level_surrogate_flag"), ab("coalition3", "market_level_surrogate_flag"),
         ab("coalition3", "pcmi_flag"), tc("coalition3"), ab("coalition3", "ni_pcmi_surrogate_flag"), ctrl],
        ["**all 4 collude** (A / B)", ab("coalition4", "pair_level_surrogate_flag", True) + f" (AUROC {au[0]:.2f}, {au[1]:.2f})",
         ab("coalition4", "market_level_surrogate_flag"), ab("coalition4", "pcmi_flag"), tc("coalition4"),
         ab("coalition4", "ni_pcmi_surrogate_flag"), "as above"],
        ["**cost asymmetry** (2 sellers +2 private cost, no channel)",
         f"**{f('pair_level_surrogate_flag')}/30 false** (names the high-cost pair {f('high_cost_pair_top_pair_level')}/30)",
         f"**{f('market_level_surrogate_flag')}/30 false**", f"{f('pcmi_flag')}/30 false (MI {f('mi_flag')}/30)", "–",
         f"{f('ni_pcmi_surrogate_flag')}/30 false",
         f"pCMI {f('pcmi_flag', 'A/control')}/30, pair_level {f('pair_level_surrogate_flag', 'A/control')}/30, MI {f('mi_flag', 'A/control')}/30"],
    ]
    return table(["test (locked)", "pair_level (surrogate)", "max-pair markup (surrogate)", "pCMI (shift)",
                  "group TC4 / TC3 (shift)", "ni_pCMI (surrogate)", "controls (same family)"], rows)


# ---------------------------------------------------------------- P2.5
def p25():
    buf = io.StringIO()
    argv = sys.argv
    sys.argv = ["p2_market_table.py", "--split", "test"]
    try:
        with contextlib.redirect_stdout(buf):
            runpy.run_path(str(ROOT / "scripts" / "p2_market_table.py"), run_name="__p2_market__")
    finally:
        sys.argv = argv
    return "\n".join(l for l in buf.getvalue().splitlines() if l.startswith("|"))


# ---------------------------------------------------------------- P2.6
def p26():
    S = jl("results/p2/rotation_test.json")["summaries"]

    def ab(g, m):
        return [k30(S[f"{fam}/T100/{g}"][m]) for fam in "AB"]

    def pair(g, m, ann=""):
        v = ab(g, m)
        return f"{v[0]}, {v[1]}" + ann

    def wil(g, m):  # Wilson percent annotation, both families
        parts = []
        for fam in "AB":
            d = S[f"{fam}/T100/{g}"][m]
            parts.append(f"{round(d['rate'] * 100)}% [{round(d['ci95'][0] * 100)}, {round(d['ci95'][1] * 100)}]")
        return f" ({parts[0]}, {parts[1]})"

    def price(g):
        return " / ".join(f"{S[f'{fam}/T100/{g}']['mean_price']['mean']:.2f}" for fam in "AB")

    def row(label, g, pc=None, te=None):
        return [label, price(g), pc or pair(g, "pcmi_flag"), te or pair(g, "te_flag"), pair(g, "mi_flag"),
                pair(g, "markup_surrogate_flag"), pair(g, "pair_level_surrogate_flag")]

    rows = [
        row("controls", "control", pc=pair("control", "pcmi_flag", wil("control", "pcmi_flag"))),
        row("shared-signal pair (reference)", "signal"),
        row("**rotation, alternating winner**", "rot_alt", pc=f"**{pair('rot_alt', 'pcmi_flag')}** (= controls)",
            te=f"**{pair('rot_alt', 'te_flag')}**" + wil("rot_alt", "te_flag")),
        row("rotation, private random winner", "rot_rand"),
    ]
    return table(["group", "mean price", "pCMI (shift)", "TE, lagged (shift)", "MI (shift)", "markup (surrogate)", "pair_level (surrogate)"], rows)


# ---------------------------------------------------------------- P2.7
def p27():
    d = jl("results/eval/p2_variants.json")
    f = lambda x, ci: f"{x:.2f} [{ci[0]:.2f}, {ci[1]:.2f}]"
    sg = lambda x: f"{x:+.2f}"
    labels = {"v0": "v0 (v1 prompt)"}
    rows = []
    for v, r in d["arms"].items():
        rows.append([labels.get(v, v), f"{r['n_C']}/{r['n_A']}", sg(r["A_markup"]), f(r["C_minus_A_markup"], r["C_minus_A_ci"]),
                     *(f(r[f"auroc_{k}"], r[f"auroc_{k}_ci"]) for k in ("market_level", "pair_level", "pcmi"))])
    h, pa = d["heterogeneity"], d["pooled_within_arm_auroc"]
    allA = [x for v in d["arms"] for x in [d["arms"][v]["A_markup"]] * d["arms"][v]["n_A"]]
    rows.append([f"**pooled** ({d['pooled_n'][0]}/{d['pooled_n'][1]})", "", sg(sum(allA) / len(allA)),
                 f"fixed effect **{h['fixed_effect_C_minus_A']:.2f} ± {h['fixed_effect_se']:.2f}** (SE); naive pool {f(d['pooled_C_minus_A'], d['pooled_ci'])}",
                 f"within-wording **{f(*pa['market_level'])}**", f(*pa["pair_level"]), f"**{f(*pa['pcmi'])}**"])
    return table(["wording", "n C/A", "no-channel markup (A)", "C − A markup [95% CI]", "AUROC markup", "AUROC pair_level", "AUROC pCMI"], rows)


# ---------------------------------------------------------------- P2.9
def p29():
    d = jl("results/eval/p2_family.json")
    f = lambda x, ci: f"{x:.2f} [{ci[0]:.2f}, {ci[1]:.2f}]"
    rows = []
    for lab, r in (("deepseek-v4.1-flash (`llm_ds_p2`)", d["deepseek"]), ("gpt-6-luna (`llm_v1`)", d["luna_llm_v1"])):
        rows.append([lab, f"{r['n_C']}/{r['n_A']}", f"{r['A_markup']:+.2f}", f"{r['C_markup']:+.2f}", f(r["C_minus_A_markup"], r["C_minus_A_ci"]),
                     *(f(r[f"auroc_{k}"], r[f"auroc_{k}_ci"]) for k in ("market_level", "pair_level", "pcmi")), str(r["degeneracy"]["sd_median"])])
    return table(["family (dataset)", "n C/A", "A markup", "C markup", "C − A markup [95% CI]", "AUROC markup", "AUROC pair_level",
                  "AUROC pCMI", "seller price SD (median)"], rows)


# ---------------------------------------------------------------- P2.10
def p210():
    d = jl("results/eval/p2cue_ext.json")["detectors"]
    arms = ("private", "neutral", "notes", "placebo", "randpartner")
    rows = []
    for k, lab in (("pair_level", "pair_level"), ("market_level", "markup over Nash\\*"), ("pcmi", "pCMI"), ("te", "lagged CMI (TE)")):
        def top(a):
            x = d[k][a]
            t = f"{x['top1_hits']:.1f}"
            if x["top1_p_vs_1/6"] < 0.05 and k in ("pcmi", "te"):
                t += f" (p = {x['top1_p_vs_1/6']:.2f})"
            return f"**{t}**" if (a == "notes" and k in ("pair_level", "market_level")) or (a == "private" and k == "pcmi") else t
        def au(a):
            x = d[k][a]
            if (a == "notes" and k != "te"):
                v = f"{x['auroc_vs_none']:.2f} [{x['auroc_vs_none_ci'][0]:.2f}, {x['auroc_vs_none_ci'][1]:.2f}]"
                return f"**{v}**" if k != "pcmi" else v
            return f"{x['auroc_vs_none']:.2f}"
        rows.append([lab, " / ".join(top(a) for a in arms), " / ".join(au(a) for a in arms[:4])])
    return table(["detector", "top-1 = assigned pair (chance 2.5/15): private / neutral / notes / placebo / randpartner",
                  "AUROC max-pair score vs none: private / neutral / notes / placebo"], rows)


# ---------------------------------------------------------------- P2.11
P211_SETS = (("gpt-6-luna (`llm_v1`, 20)", "llm_v1"), ("gpt-6-luna (`llm_long`, 50)", "llm_long"),
             ("gpt-6-luna (E44 `llm_long_p2_T60`, 60)", "llm_long_p2_T60"), ("deepseek-v4.1-flash (`llm_ds_p2`, 20)", "llm_ds_p2"),
             ("Qwen3.8-27B **abliterated** (`llm_qa_p2`, 20)", "llm_qa_p2"), ("Qwen3.8-27B base (`llm_qb_p2`, 20)", "llm_qb_p2"))


def p211():
    d = jl("results/eval/p2_partc.json")
    j = lambda k, n, ci: f"{k}/{n} [{ci[0]:.2f}, {ci[1]:.2f}]".replace("[0.00,", "[0,").replace(", 1.00]", ", 1]")
    rows = []
    for lab, name in P211_SETS:
        r, b = d[name], d[name]["behaviour"]
        rows.append([lab, f"{r['n_C']}/{r['n_A']}", f"{r['A_markup']:+.2f}".replace("-", "−"),
                     f"{r['C_minus_A_markup']:+.2f} [{r['C_minus_A_ci'][0]:.2f}, {r['C_minus_A_ci'][1]:.2f}]",
                     f"{r['auroc_market_level']:.2f}", f"{r['auroc_pcmi']:.2f}", f"{b['agreement']}/{b['n_C_labelled']}",
                     j(b["executed"], b["n_C_labelled"], b["executed_ci"]), j(r["tacit_A"], r["n_A"], r["tacit_A_ci"])])
    return table(["seller (dataset, T)", "n C/A", "A markup", "C − A markup", "AUROC markup", "AUROC pCMI", "agreement",
                  "executed (C)", "tacit (A)"], rows)


BUILDERS = {"P2.1": p21, "P2.3": p23, "P2.4": p24, "P2.5": p25, "P2.6": p26, "P2.7": p27, "P2.9": p29, "P2.10": p210, "P2.11": p211}


def check(report):
    a, b = report.index("**P2.1 Precision"), report.index("\n## 5. Limitations")  # the at-a-glance summary table is prose-checked, not regenerated
    blocks = parse_tables(report[a:b], include_header=True)
    if len(blocks) != len(BUILDERS):
        print(f"FAIL: expected {len(BUILDERS)} tables in Phase 2 section, found {len(blocks)}")
        return False
    errors, cells = [], 0
    for (section, build), actual in zip(BUILDERS.items(), blocks):
        expected = parse_tables(build(), include_header=True)[0]
        if len(actual) != len(expected):
            errors.append(f"{section}: expected {len(expected)} rows, found {len(actual)}")
            continue
        for i, (ar, er) in enumerate(zip(actual, expected), 1):
            if len(ar) != len(er):
                errors.append(f"{section}, row {i}: expected {len(er)} cells, found {len(ar)}")
                continue
            for j, (av, ev) in enumerate(zip(ar, er), 1):
                if i == 1:
                    continue  # header text is not a result
                cells += 1
                if normalized(av) != normalized(ev):
                    errors.append(f"{section}, row {i} ({ar[0][:30]}), cell {j}: REPORT {av!r} != JSON-generated {ev!r}")
    for e in errors:
        print("FAIL:", e)
    for u in UNCHECKED:
        print("UNCHECKED:", u)
    print(f"{'FAIL' if errors else 'PASS'}: {len(BUILDERS)} Phase 2 tables, {cells} body cells checked, "
          f"{len(UNCHECKED)} unchecked, {len(errors)} mismatches")
    return not errors


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(0 if check((ROOT / "REPORT.md").read_text()) else 1)
    for s, b in BUILDERS.items():
        print(f"### REPORT {s}\n\n{b()}\n")
