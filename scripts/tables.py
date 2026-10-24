"""Regenerate REPORT.md section 4.1/4.2/4.3 tables purely from results/*.json (no experiments run).

Usage: uv run python scripts/tables.py > out.md
CIs are the Wilson intervals already stored in the JSON by experiments.scripted.evaluate
(experiments.scripted.wilson); nothing is recomputed here.
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DETS = ["pearson", "mi", "cmi_state", "pcmi", "te"]


def f2(x):
    return f"{x:.2f}"


def fci(ci):
    def g(v):
        v = min(max(v, 0.0), 1.0)
        s = f"{v:.2f}"
        if s == "1.00":
            return "1"
        return s[1:] if s.startswith("0") else s
    return f"[{g(ci[0])},{g(ci[1])}]"


GROUPS = [
    ("A independent", "A"),
    ("B common shock", "B"),
    ("independent high-price pair", "A+independent_high_price"),
    ("legit leader-follower (public matching)", "A+legit_cooperation"),
    ("shared policy, independent noise", "A+shared_policy"),
    ("shared policy + common shock", "B+shared_policy"),
    ("shared policy **and shared seed**", "A+shared_seed"),
    ("shared seed + common shock", "B+shared_seed"),
    ("**C collusion** (pair ranked #1)", "C"),
    ("**D collusion + shock** (pair #1)", "D"),
]


def gate():
    m = json.load(open(os.path.join(ROOT, "results/eval/gate_test.json")))["metrics"]
    a = json.load(open(os.path.join(ROOT, "results/eval/gate_test.json")))["args"]
    print(f"### 4.1 (gate_test.json: seed {a['seed']}, n={a['n']}, T={a['T']}, s={a['strength']}, B={a['B']})\n")
    print("| group | \\|Pearson\\| | MI | CMI\\|state | **pCMI** shift [CI] / surrogate [CI] | TE |")
    print("|---|---|---|---|---|---|")
    for name, key in GROUPS:
        cells = []
        for d in DETS:
            r = m[d][key]
            coll = "top1" in r
            if d == "pcmi":
                if coll:
                    c = f"{f2(r['flag_rate'])} {fci(r['flag_ci'])} / {f2(r['surrogate_flag_rate'])} (top-1 {f2(r['top1'])})"
                else:
                    c = (f"{f2(r['flag_rate'])} {fci(r['flag_ci'])} / "
                         f"{f2(r['surrogate_flag_rate'])} {fci(r['surrogate_flag_ci'])}")
            else:
                c = f"{f2(r['flag_rate'])} / {f2(r['surrogate_flag_rate'])}"
                if coll:
                    c += f" ({f2(r['top1'])})"
            cells.append(c)
        print(f"| {name} | " + " | ".join(cells) + " |")
    print()
    print("AUROC (CD vs all negatives, from JSON): " + ", ".join(f"{d}={m[d]['auroc_CD_vs_all_neg']:.3f}" for d in DETS))
    print()


def sweep():
    p = json.load(open(os.path.join(ROOT, "results/sweeps/power_test.json")))
    a = p["args"]
    print(f"### 4.2 (power_test.json: seed {a['seed']}, n={a['n']} per condition, B={a['B']}; "
          "rate = shift-null flag rate, mean over C,D (coll.) / A,B (ctrl); top-1 = mean over C,D)\n")
    print("Per-point values for every (type, T, strength) in the sweep, so range summaries "
          "(s>=0.2, <=0.25, >=0.97 ...) can be checked.\n")
    print("| collusion type | T | s | MI (coll./ctrl) | CMI\\|state | pCMI | TE | pair top-1 pCMI / TE |")
    print("|---|---|---|---|---|---|---|---|")
    names = {"signal": "shared signal", "tft": "tit-for-tat", "fixed_high": "stay-high"}

    def cc(m, d):
        x = m[d]
        coll = (x["C"]["flag_rate"] + x["D"]["flag_rate"]) / 2
        ctrl = (x["A"]["flag_rate"] + x["B"]["flag_rate"]) / 2
        return coll, ctrl

    def t1(m, d):
        x = m[d]
        return (x["C"]["top1"] + x["D"]["top1"]) / 2

    order = {"signal": 0, "tft": 1, "fixed_high": 2}
    rows = sorted(p["rows"], key=lambda r: (order[r["type"]], r["T"], r["strength"]))
    for r in rows:
        m = r["metrics"]
        mi, cm, pc, te = (cc(m, d) for d in ("mi", "cmi_state", "pcmi", "te"))
        print(f"| {names[r['type']]} | {r['T']} | {r['strength']} | {f2(mi[0])} / {f2(mi[1])} | "
              f"{f2(cm[0])} / {f2(cm[1])} | **{f2(pc[0])} / {f2(pc[1])}** | {f2(te[0])} / {f2(te[1])} | "
              f"{f2(t1(m, 'pcmi'))} / {f2(t1(m, 'te'))} |")
    print()


def llm():
    print("### 4.3 LLM-agent evaluation tables (verbatim from results/eval/llm_*_report.md)\n")
    for fn in sorted(glob.glob(os.path.join(ROOT, "results/eval/llm_*_report.md"))):
        print(f"#### {os.path.relpath(fn, ROOT)}\n")
        print(open(fn).read().rstrip() + "\n")


def mixed(name="llm_mixed2"):
    fn = os.path.join(ROOT, f"results/eval/{name}_mixed.json")
    if not os.path.exists(fn):
        return
    d = json.load(open(fn))
    print(f"### 4.3 (iv) {name}: per-run mean same-model pair score minus mean cross-model pair score\n")
    print("| detector | same − cross (mean) [95% CI] | runs with same > cross | sign p | pair flag rate same-sol / same-luna / cross |")
    print("|---|---|---|---|---|")
    for det in ["pcmi", "mi", "te", "pearson"]:
        r = d[det]["per_run_same_minus_cross"]
        fl = " / ".join(f"{round(d[det][k]['pair_flag_rate'] * d[det][k]['n_pairs'])}/{d[det][k]['n_pairs']}"
                        for k in ["same_big", "same_base", "cross"])
        print(f"| {det} | {r['mean']:+.3f} [{r['mean_ci'][0]:+.3f}, {r['mean_ci'][1]:+.3f}] | "
              f"{r['n_positive']}/{r['n_runs']} | {r['sign_test_p']:.2f} | {fl} |")
    pm = os.path.join(ROOT, f"results/eval/{name}_price_by_model.json")
    if os.path.exists(pm):
        q = json.load(open(pm))["sol_minus_luna_per_run"]
        print(f"\nsol − luna mean price per run: {q['mean']:+.2f} [{q['ci'][0]:+.2f}, {q['ci'][1]:+.2f}]")
    print(f"excluded (model check): {len(d['excluded_not_mixed_model'])}\n")


if __name__ == "__main__":
    gate()
    sweep()
    llm()
    mixed()
