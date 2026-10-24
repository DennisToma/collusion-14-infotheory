"""Forest plot of per-run same-model minus cross-model pair score in llm_mixed2 (§4.3.5, PLAN req. 3).
uv run python scripts/mixed_fig.py  -> figures/llm_mixed2_same_vs_cross.png (reads results/eval/llm_mixed2_mixed.json)"""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = json.load(open("results/eval/llm_mixed2_mixed.json"))
dets = [("pcmi", "pCMI"), ("mi", "MI (= CMI|state)"), ("te", "TE"), ("pearson", "|Pearson|"), ("pearson_diff", "|Pearson| (diff)")]
fig, ax = plt.subplots(figsize=(6, 2.8))
for i, (k, name) in enumerate(dets):
    r = d[k]["per_run_same_minus_cross"]
    lo, hi = r["mean_ci"]
    ax.plot([lo, hi], [i, i], color="#2a6fbb", lw=2, solid_capstyle="round")
    ax.plot(r["mean"], i, "o", ms=8, color="#2a6fbb", mec="white", mew=2)
    ax.text(0.205, i, f'{r["mean"]:+.3f}  ({r["n_positive"]}/{r["n_runs"]} runs > 0)', va="center", fontsize=8, color="#333")
ax.axvline(0, color="#888", lw=1, ls="--")
ax.set_yticks(range(len(dets)), [n for _, n in dets])
ax.invert_yaxis()
ax.set_xlim(-0.12, 0.2)
ax.set_xlabel("same-model − cross-model pair score per game (mean, bootstrap 95% CI)", fontsize=8)
ax.set_title("llm_mixed2: 12 no-channel games, 2 gpt-6.1-sol + 2 gpt-6-luna sellers", fontsize=9)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.tick_params(labelsize=8)
fig.savefig("figures/llm_mixed2_same_vs_cross.png", dpi=150, bbox_inches="tight")
print("wrote figures/llm_mixed2_same_vs_cross.png")
