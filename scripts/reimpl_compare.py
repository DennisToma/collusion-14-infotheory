"""Phase 2 (E47): compare the independent codex reimplementation (results/reimpl/, written from REPORT §3 text only)
with our frozen evaluations (results/eval/llm_v1.json, llm_long.json).
    uv run python scripts/reimpl_compare.py   # -> results/reimpl/compare.json
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAP = {"pCMI": "pcmi", "MI_MM": "mi", "market_level": "market_level", "pair_level": "pair_level"}


def main():
    re_ = json.load(open(ROOT / "results/reimpl/results.json"))
    out = {"scores": {}, "auroc": {}}
    for ds, T, key in (("llm_v1", "20", "llm_v1"), ("llm_long", "50", "llm_long"), ("llm_long", "20", "llm_long_first20")):
        ours = json.load(open(ROOT / f"results/eval/{ds}.json"))
        for a, b in MAP.items():
            if key in re_ and a in re_[key]:
                o, r = ours["run_scores"][T][b], re_[key][a]
                diff = {k: abs(o[k] - r[k]) for k in o}
                out["scores"][f"{key}:{a}"] = dict(n=len(o), n_agree_1e9=sum(d < 1e-9 for d in diff.values()),
                                                  disagree={k: [o[k], r[k]] for k, d in diff.items() if d >= 1e-9})
        for tag, (pc, nc) in {"C_D_vs_A_B": ("CD", "AB"), "C_vs_A": ("C", "A"), "D_vs_B": ("D", "B")}.items():
            if tag not in re_["aurocs"].get(key, {}):
                continue
            ours_m = ours["by_T"][T]
            for a, b in MAP.items():
                ok = "auroc_" + ("CD_vs_AB" if tag == "C_D_vs_A_B" else tag)
                out["auroc"][f"{key}:{tag}:{a}"] = [ours_m[b].get(ok), re_["aurocs"][key][tag][a]]
    v1 = json.load(open(ROOT / "results/eval/llm_v1.json"))["by_T"]["20"]["pcmi"]
    out["shift_flag_rate_pcmi_llm_v1"] = {c: dict(ours=v1[c]["flag_rate"], reimpl=re_["flag_rates"]["llm_v1"][c]["fraction_p_lt_0_05"],
                                                  n=v1[c]["n"]) for c in ("A", "C")}
    json.dump(out, open(ROOT / "results/reimpl/compare.json", "w"), indent=1)
    worst = max(abs(x - y) for x, y in out["auroc"].values())
    print("score agreement:", {k: f"{v['n_agree_1e9']}/{v['n']}" for k, v in out["scores"].items()})
    print("max AUROC |diff|:", worst, "over", len(out["auroc"]), "comparisons")
    print("pCMI shift-null flag rate:", out["shift_flag_rate_pcmi_llm_v1"])


if __name__ == "__main__":
    main()
