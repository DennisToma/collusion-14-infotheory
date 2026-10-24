"""Failure-path checks for the release audit; no research results are changed.

uv run python scripts/test_release_audit.py
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import report_tables
import verify_release
import check_saved_scores


class ReportChecks(unittest.TestCase):
    def test_numeric_and_structural_corruption(self):
        original = (report_tables.ROOT / "REPORT.md").read_text()
        mutations = {
            "point estimate": original.replace("| 0.45 [0.32, 0.59] |", "| 0.46 [0.32, 0.59] |", 1),
            "CI sign": original.replace("+0.003 [−0.025, +0.032]", "+0.003 [+0.025, +0.032]"),
            "bound": original.replace("1.00 / ≤0.18", "1.00 / ≤0.17", 1),
            "header": original.replace("| AUROC private vs none | AUROC agreement vs none |",
                                       "| AUROC placebo vs none | AUROC agreement vs none |", 1),
            "missing table": original.replace("| T (same games, prefixes) | 10 | 20 | 30 | 40 | 50 |\n|---|---|---|---|---|---|",
                                              "table removed", 1),
        }
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(report_tables.check(original))
            for name, changed in mutations.items():
                with self.subTest(name=name):
                    self.assertNotEqual(original, changed, "mutation must actually alter the report")
                    try:
                        accepted = report_tables.check(changed)
                    except ValueError:
                        accepted = False
                    self.assertFalse(accepted)


class ReleaseChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="c14-audit-test-", dir="/var/tmp")
        self.root = Path(self.tmp.name)
        for name in ["README.md", "REPORT.md", "PRESENTATION.md"]:
            (self.root / name).write_text("# Fixture\n")
        for suffix in ["", "rep", "plc", "mon", "fp"]:
            dest = self.root / "data" / f"ext_llm_v3{suffix}"
            dest.mkdir(parents=True)
            content = b"{}\n"
            (dest / "ground_truth.jsonl").write_bytes(content)
            digest = hashlib.sha256(content).hexdigest()
            (dest / "SHA256SUMS").write_text(f"{digest}  ground_truth.jsonl\n")
        (self.root / "results/eval").mkdir(parents=True)
        (self.root / "results/eval/value.json").write_text("original\n")
        self.script = self.root / "render.py"
        self.script.write_text("from pathlib import Path\nPath('results/eval/value.json').write_text('original\\n')\n")

    def tearDown(self):
        self.tmp.cleanup()

    def run_fixture(self, *, core_steps=None, phase2_steps=None):
        def fake_git(*args):
            if args[0] == "rev-parse":
                return "fixture-revision\n"
            if args[0] == "status":
                return ""
            if args[0] == "ls-files":
                return "\0".join(str(p.relative_to(self.root)) for p in self.root.rglob("*") if p.is_file()) + "\0"
            raise AssertionError(args)
        steps = [(["render.py"], ["results/eval/value.json"])]
        argv = ["verify_release.py"] + (["--core-eval"] if core_steps is not None else [])
        if phase2_steps is not None:
            argv.append("--phase2-recompute")
        with patch.object(verify_release, "ROOT", self.root), patch.object(verify_release, "git", fake_git), \
             patch.object(verify_release, "RENDER", steps), \
             patch.object(verify_release, "CORE_EVAL", core_steps or []), \
             patch.object(verify_release, "PHASE2_RECOMPUTE", phase2_steps or []), patch.object(sys, "argv", argv), \
             contextlib.redirect_stdout(io.StringIO()):
            # Exercise the real command runner/snapshot/error handling, replacing only the
            # research table command with a small successful command for this fixture.
            original_run = verify_release.subprocess.run
            def run(command, **kwargs):
                if command[1:] == ["scripts/tables.py", "--check"]:
                    command = [command[0], "-c", "print('PASS fixture table')"]
                return original_run(command, **kwargs)
            with patch.object(verify_release.subprocess, "run", run):
                code = verify_release.main()
        return code, json.loads((self.root / "results/release_audit.json").read_text())

    def test_matching_outputs_pass(self):
        code, evidence = self.run_fixture()
        self.assertEqual(code, 0)
        self.assertTrue(evidence["passed"])
        self.assertEqual(evidence["static_checks"]["snapshot_checksums"], 5)
        self.assertFalse(evidence["static_checks"]["cache_present"])
        self.assertFalse(evidence["core_eval"])
        self.assertEqual((self.root / "results/eval/value.json").read_text(), "original\n")

    def test_changed_output_fails_and_preserves_source(self):
        self.script.write_text("from pathlib import Path\nPath('results/eval/value.json').write_text('changed\\n')\n")
        code, evidence = self.run_fixture()
        self.assertEqual(code, 1)
        self.assertFalse(evidence["passed"])
        self.assertEqual(evidence["checks"][0]["byte_mismatches"], ["results/eval/value.json"])
        self.assertEqual((self.root / "results/eval/value.json").read_text(), "original\n")

    def test_nonzero_command_fails_with_diagnostics(self):
        self.script.write_text("print('fixture failure')\nraise SystemExit(7)\n")
        code, evidence = self.run_fixture()
        self.assertEqual(code, 1)
        self.assertEqual(evidence["checks"][0]["exit_code"], 7)
        self.assertIn("fixture failure", evidence["checks"][0]["diagnostics"])

    def test_missing_snapshot_manifest_fails(self):
        (self.root / "data/ext_llm_v3plc/SHA256SUMS").unlink()
        code, evidence = self.run_fixture()
        self.assertEqual(code, 1)
        self.assertFalse(evidence["passed"])
        self.assertIn("SHA256SUMS", evidence["error"])

    def test_bad_snapshot_checksum_fails(self):
        (self.root / "data/ext_llm_v3plc/ground_truth.jsonl").write_text("altered\n")
        code, evidence = self.run_fixture()
        self.assertEqual(code, 1)
        self.assertIn("Checksum mismatch", evidence["error"])

    def test_finalized_phase2_result_requires_snapshot_manifest(self):
        (self.root / "results/eval/strongF_ext.json").write_text("{}\n")
        code, evidence = self.run_fixture()
        self.assertEqual(code, 1)
        self.assertIn("ext_llm_p2strongF/SHA256SUMS", evidence["error"])

    def test_phase2_snapshot_checksum_is_checked(self):
        (self.root / "results/eval/p2cue_ext.json").write_text("{}\n")
        dest = self.root / "data/ext_llm_p2cue"
        dest.mkdir()
        (dest / "labels.jsonl").write_bytes(b"changed\n")
        digest = hashlib.sha256(b"original\n").hexdigest()
        (dest / "SHA256SUMS").write_text(f"{digest}  labels.jsonl\n")
        code, evidence = self.run_fixture()
        self.assertEqual(code, 1)
        self.assertIn("Checksum mismatch", evidence["error"])
        self.assertIn("ext_llm_p2cue/labels.jsonl", evidence["error"])

    def test_phase2_table_failure_is_not_hidden_by_v1_pass(self):
        scripts = self.root / "scripts"
        scripts.mkdir()
        (scripts / "p2_tables.py").write_text("print('Phase 2 mismatch')\nraise SystemExit(1)\n")
        code, evidence = self.run_fixture()
        self.assertEqual(code, 1)
        self.assertEqual(evidence["checks"][-1]["command"][1:], ["scripts/p2_tables.py", "--check"])
        self.assertIn("Phase 2 mismatch", evidence["checks"][-1]["diagnostics"])

    def test_phase2_recomputation_mismatch_stops_before_render(self):
        (self.root / "results/eval/phase2.json").write_text("saved summary\n")
        (self.root / "phase2.py").write_text(
            "from pathlib import Path\nPath('results/eval/phase2.json').write_text('changed summary\\n')\n")
        code, evidence = self.run_fixture(phase2_steps=[(["phase2.py"], ["results/eval/phase2.json"])])
        self.assertEqual(code, 1)
        self.assertTrue(evidence["phase2_recompute"])
        self.assertEqual(len(evidence["checks"]), 1)
        self.assertEqual(evidence["checks"][0]["byte_mismatches"], ["results/eval/phase2.json"])
        self.assertEqual((self.root / "results/eval/phase2.json").read_text(), "saved summary\n")

    def test_core_eval_runs_before_render_without_changing_saved_inputs(self):
        # The renderer requires a marker created only by the evaluator. Both outputs
        # must independently match the committed baseline; data stays unchanged.
        (self.root / "data/labels.jsonl").write_text("saved labels\n")
        (self.root / "results/eval/core.json").write_text("saved scores\n")
        (self.root / "evaluate.py").write_text(
            "from pathlib import Path\n"
            "assert Path('data/labels.jsonl').read_text() == 'saved labels\\n'\n"
            "Path('results/eval/core.json').write_text('saved scores\\n')\n"
            "Path('evaluated').touch()\n")
        self.script.write_text(
            "from pathlib import Path\n"
            "assert Path('evaluated').exists()\n"
            "assert Path('results/eval/core.json').read_text() == 'saved scores\\n'\n"
            "Path('results/eval/value.json').write_text('original\\n')\n")
        code, evidence = self.run_fixture(core_steps=[(["evaluate.py"], ["results/eval/core.json"])])
        self.assertEqual(code, 0)
        self.assertTrue(evidence["core_eval"])
        self.assertEqual([c["command"][1] for c in evidence["checks"][:2]], ["evaluate.py", "render.py"])
        self.assertEqual((self.root / "data/labels.jsonl").read_text(), "saved labels\n")
        self.assertFalse((self.root / "evaluated").exists(), "evaluation must run in the disposable copy")

    def test_core_eval_mismatch_stops_before_render(self):
        (self.root / "results/eval/core.json").write_text("saved scores\n")
        (self.root / "evaluate.py").write_text(
            "from pathlib import Path\nPath('results/eval/core.json').write_text('different scores\\n')\n")
        code, evidence = self.run_fixture(core_steps=[(["evaluate.py"], ["results/eval/core.json"])])
        self.assertEqual(code, 1)
        self.assertEqual(len(evidence["checks"]), 1)
        self.assertEqual(evidence["checks"][0]["byte_mismatches"], ["results/eval/core.json"])
        self.assertEqual((self.root / "results/eval/core.json").read_text(), "saved scores\n")


class SavedScoreChecks(unittest.TestCase):
    def test_score_and_run_coverage_corruption(self):
        # A real frozen score calculation in a tiny saved-data fixture; then
        # corrupt the artifact in two ways the ordinary REPORT checks cannot see.
        with tempfile.TemporaryDirectory(prefix="c14-score-test-", dir="/var/tmp") as td:
            root = Path(td)
            dest = root / "data/fixture"
            dest.mkdir(parents=True)
            rows = [dict(run_id="A_000", round=t, market={"cost": 6, "demand": 1},
                         agents=[dict(id=a, price=8 + 2 * ((t + j * t * t) % 5)) for j, a in enumerate("ABCD")])
                    for t in range(12)]
            (dest / "trajectories.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
            P, S, _ = check_saved_scores.arrays(rows)
            result = check_saved_scores.score_run(P, S, B=0)
            check_saved_scores.add_level_scores(result, P, check_saved_scores.np.full(12, 10.))
            scores = {det: {"A_000": max(result[p]["score"][det] for p in check_saved_scores.PAIR_NAMES)}
                      for det in check_saved_scores.DETS}
            saved = root / "results/eval/fixture.json"
            saved.parent.mkdir(parents=True)
            write = lambda s: saved.write_text(json.dumps({"run_scores": {"12": s}}))
            write(scores)
            self.assertEqual(check_saved_scores.check("fixture", root)["score_cells"], len(scores))
            scores["pcmi"]["A_000"] += .01
            write(scores)
            with self.assertRaisesRegex(AssertionError, "pcmi"):
                check_saved_scores.check("fixture", root)
            del scores["pcmi"]["A_000"]
            write(scores)
            with self.assertRaisesRegex(AssertionError, "run coverage"):
                check_saved_scores.check("fixture", root)


if __name__ == "__main__":
    unittest.main()
