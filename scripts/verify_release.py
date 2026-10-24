"""Audit the release in a disposable copy without caches, sibling repos, or LLM calls.

uv run --group export python scripts/verify_release.py --recompute --export
uv run --group export python scripts/verify_release.py --core-eval --recompute --export
uv run python scripts/verify_release.py --phase2-recompute

Always checks REPORT tables and snapshot checksums, then regenerates presentation/figures
and LLM report tables. --recompute also re-runs E30/E32/E35/E39 and the small descriptive
analyses from committed data. It never reruns the locked scripted experiments or LLM
generation/judging. --core-eval additionally reruns the frozen main LLM evaluators
(including their prefix/CI calculations), mixed-model comparison and trend/incremental
diagnostics from saved trajectories and labels. This is slower than --recompute.
--export runs the PDF export's text/page/overflow checks.
All regenerated outputs except PDFs must match the source bytes exactly. The source
worktree is untouched except for results/release_audit.json (including failure evidence).
Uses the current Python environment; sync dependencies (plus the export group if needed)
and install Chromium first, as documented in REPORT §6.

--phase2-recompute regenerates finalized Phase 2 summaries, bootstrap intervals and
figures from saved trajectories, judge labels and detector scores. This is a fixed
allowlist: it never analyses the pending E68/E70 experiments or runs new scripted
test seeds. Phase 2 REPORT tables are checked on every audit when available.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Keep the original evaluation settings and order: these are verification reruns,
# never generation, judging, tuning, or a new evaluation of the locked scripted seeds.
CORE_EVAL = [
    (["-m", "experiments.llm_eval", "eval", "--name", "llm_v1", "--B", "200"], ["results/eval/llm_v1.json"]),
    (["-m", "experiments.llm_eval", "eval", "--name", "llm_long", "--B", "200"], ["results/eval/llm_long.json"]),
    (["-m", "experiments.llm_eval", "mixed", "--name", "llm_mixed2", "--B", "200"], ["results/eval/llm_mixed2_mixed.json"]),
    (["-m", "experiments.ext_llm_v3"], ["results/eval/llm_v3_ext.json", "results/eval/llm_v3_ext_report.md"]),
    (["-m", "experiments.diag_llm_v1"], ["results/eval/llm_v1_diag.json"]),
    (["-m", "experiments.diag_llm_v3"], ["results/eval/llm_v3_diag.json"]),
]

RECOMPUTE = [
    (["scripts/injection_mde.py"], ["results/eval/injection_mde.json"]),
    (["scripts/placebo_rep_ext.py"], ["results/eval/placebo_rep_ext.json", "results/eval/placebo_rep_ext_report.md"]),
    (["scripts/nonagreement_ext.py"], ["results/eval/nonagreement_ext.json", "results/eval/nonagreement_ext_report.md"]),
    (["scripts/preplay_offer.py"], ["results/eval/preplay_offer.json"]),
    (["scripts/mixed_price_by_model.py"], ["results/eval/llm_mixed2_price_by_model.json"]),
    (["scripts/market_mean_ranges.py"], ["results/eval/llm_v1_market_mean_ranges.json"]),
    (["-m", "experiments.premium_llm_v3"], ["results/eval/llm_v3_premium.json"]),
]
# Fixed, reviewed commands: no --label, --run-eval, --snapshot, generation, or
# discovery of unfinished datasets. Dependencies precede their consumers.
PHASE2_RECOMPUTE = [
    (["scripts/check_saved_scores.py"], []),
    (["scripts/prevalence.py"], ["results/eval/prevalence.json", "results/eval/prevalence.md"]),
    (["scripts/reimpl_compare.py"], ["results/reimpl/compare.json"]),
    (["scripts/same_model.py"], ["results/eval/same_model.json", "results/eval/same_model.md"]),
    (["scripts/matched_ref.py"], ["results/eval/matched_ref.json", "results/eval/matched_ref.md"]),
    (["scripts/p2_variants.py"], ["results/eval/p2_variants.json", "results/eval/p2_variants.md"]),
    (["scripts/p2_family.py"], ["results/eval/p2_family.json", "results/eval/p2_family.md"]),
    (["scripts/p2_public.py"], ["results/eval/p2_public_llm_ds_p2pub.json"]),
    (["scripts/p2cue_ext.py"], ["results/eval/p2cue_ext.json", "results/eval/p2cue_ext.md"]),
    (["scripts/strongF_ext.py"], ["results/eval/strongF_ext.json", "results/eval/strongF_ext.md"]),
    (["scripts/p2_partc.py"], ["results/eval/p2_partc.json", "results/eval/p2_partc.md"]),
    (["scripts/e67_sticky.py"], ["results/eval/e67_sticky.json", "results/eval/e67_sticky.md"]),
    (["scripts/e44_decline.py"], ["results/eval/e44_decline.json"]),
    (["scripts/long_power.py", "--name", "llm_long_p2_T60"],
     ["results/eval/long_power_llm_long_p2_T60.json", "results/eval/long_power_llm_long_p2_T60.md"]),
    *[(["scripts/spillover.py", "--name", name],
       [f"results/eval/spillover_{name}.json", f"results/eval/spillover_{name}.md"])
      for name in ["llm_v1", "llm_ds_p2", "llm_long_p2_T60", "llm_strong_qa"]],
    (["scripts/claims_denominators.py"], ["results/eval/claims_denominators.json", "results/eval/claims_denominators.md"]),
    (["scripts/premium_decay_fig.py", "--name", "llm_long_p2_T60"], ["figures/premium_decay_llm_long_p2_T60.png"]),
]

RENDER = [
    (["-m", "experiments.llm_report", "--name", "llm_v1"], ["results/eval/llm_v1_report.md", "figures/llm_v1_prices.png", "figures/llm_v1_auroc.png", "figures/llm_v1_power_vs_T.png"]),
    (["-m", "experiments.llm_report", "--name", "llm_long"], ["results/eval/llm_long_report.md", "figures/llm_long_prices.png", "figures/llm_long_auroc.png", "figures/llm_long_power_vs_T.png"]),
    (["scripts/mixed_fig.py"], ["figures/llm_mixed2_same_vs_cross.png"]),
    (["-m", "experiments.llm_fig"], ["figures/llm_auroc_both.png"]),
    (["scripts/headline_fig.py"], ["figures/headline.png"]),
    (["scripts/phase2_fig.py"], ["figures/phase2_headline.png"]),
    (["scripts/slides.py"], ["PRESENTATION.md"]),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT).decode()


def snapshot(dest):
    # Include in-progress source edits so this also works before a milestone commit.
    # Gitignored caches, environments, and the sibling's live files are never copied.
    paths = git("ls-files", "--cached", "--others", "--exclude-standard", "-z").split("\0")
    inputs = {}
    for name in sorted(set(paths) - {""}):
        src = ROOT / name
        if not src.is_file():
            continue
        out = dest / name
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out)
        if src.suffix in {".py", ".json", ".jsonl", ".gz", ".toml", ".lock"} or name in {"REPORT.md", "PRESENTATION.md", "README.md", "EXPERIMENTS.tsv"}:
            if not name.startswith("results/release_audit"):
                inputs[name] = sha(src)
    if (dest / "cache").exists():
        raise ValueError("Snapshot unexpectedly contains an LLM cache")
    return inputs


def static_checks(dest):
    checksums = 0
    manifests = {dest / "data" / f"ext_llm_v3{suffix}" / "SHA256SUMS" for suffix in ["", "rep", "plc", "mon", "fp"]}
    # Globbing alone would silently accept deletion of a required manifest.
    for result, dataset in [("p2cue_ext", "ext_llm_p2cue"), ("strongF_ext", "ext_llm_p2strongF")]:
        if (dest / "results/eval" / f"{result}.json").exists():
            manifests.add(dest / "data" / dataset / "SHA256SUMS")
    manifests.update((dest / "data").glob("*/SHA256SUMS"))
    for manifest in sorted(manifests):
        for line in manifest.read_text().splitlines():
            digest, name = line.split(maxsplit=1)
            p = manifest.parent / name.lstrip("*")
            if sha(p) != digest:
                raise ValueError(f"Checksum mismatch: {p.relative_to(dest)}")
            checksums += 1
    links = 0
    for name in ["README.md", "REPORT.md", "PRESENTATION.md"]:
        for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", (dest / name).read_text()):
            target = target.split("#", 1)[0]
            if not target or re.match(r"[a-z]+:", target):
                continue
            if not (dest / target).is_file():
                raise ValueError(f"Broken local link in {name}: {target}")
            links += 1
    return {"snapshot_checksums": checksums, "snapshot_manifests": len(manifests), "local_links": links, "cache_present": False}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--core-eval", action="store_true")
    ap.add_argument("--recompute", action="store_true")
    ap.add_argument("--phase2-recompute", action="store_true")
    ap.add_argument("--export", action="store_true")
    args = ap.parse_args()
    evidence = {"schema_version": 3, "started_utc": dt.datetime.now(dt.UTC).isoformat(),
                "source_revision": git("rev-parse", "HEAD").strip(),
                "source_worktree_dirty": bool(git("status", "--porcelain").strip()),
                "python_version": sys.version,
                "packages": {p: importlib.metadata.version(p) for p in ["numpy", "scipy", "matplotlib", "scikit-learn"]},
                "core_eval": args.core_eval, "recompute": args.recompute,
                "phase2_recompute": args.phase2_recompute, "export": args.export,
                "checks": [], "passed": False}
    try:
        with tempfile.TemporaryDirectory(prefix="c14-release-", dir="/var/tmp") as td:
            dest = Path(td)
            evidence["input_sha256"] = snapshot(dest)
            evidence["static_checks"] = static_checks(dest)
            print("PASS: snapshot checksums and local links; no LLM cache in disposable copy", flush=True)
            # Remove inherited Python import paths that could resolve modules in the live repo.
            env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}}
            env["MPLCONFIGDIR"] = str(dest / ".mplconfig")
            env["PYTHONUNBUFFERED"] = "1"
            table_checks = [(["scripts/tables.py", "--check"], [])]
            if (dest / "scripts/p2_tables.py").exists():
                table_checks.append((["scripts/p2_tables.py", "--check"], []))
            steps = ((CORE_EVAL if args.core_eval else []) + (RECOMPUTE if args.recompute else [])
                     + (PHASE2_RECOMPUTE if args.phase2_recompute else []) + RENDER + table_checks)
            if args.export:
                steps.append((["scripts/export_pdf.py"], ["REPORT.html"]))
            expected_outputs = {p: sha(dest / p) for _, outputs in steps for p in outputs}
            for command, outputs in steps:
                t0 = time.monotonic()
                print("RUN:", " ".join(command), flush=True)
                proc = subprocess.run([sys.executable, *command], cwd=dest, env=env,
                                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                changed = [p for p in outputs if not (dest / p).is_file() or sha(dest / p) != expected_outputs[p]]
                row = {"command": ["python", *command], "seconds": round(time.monotonic() - t0, 2),
                       "exit_code": proc.returncode, "outputs": {p: sha(dest / p) for p in outputs if (dest / p).is_file()},
                       "byte_mismatches": changed, "passed": proc.returncode == 0 and not changed}
                evidence["checks"].append(row)
                if not row["passed"]:
                    row["diagnostics"] = proc.stdout[-6000:]
                    raise ValueError(f"{' '.join(command)}: exit={proc.returncode}, changed={changed}\n{proc.stdout[-3000:]}")
                # Keep compact diagnostics for table/export evidence, avoid large analysis logs.
                if not outputs or command == ["scripts/export_pdf.py"]:
                    row["diagnostics"] = proc.stdout[-6000:]
                print(f"PASS: {len(outputs)} outputs byte-identical ({row['seconds']}s)" if outputs else proc.stdout.strip(), flush=True)
            evidence["passed"] = True
    except Exception as exc:
        evidence["error"] = str(exc)
        print("FAIL:", exc, flush=True)
    evidence["finished_utc"] = dt.datetime.now(dt.UTC).isoformat()
    (ROOT / "results/release_audit.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(f"{'PASS' if evidence['passed'] else 'FAIL'}: evidence in results/release_audit.json", flush=True)
    return 0 if evidence["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
