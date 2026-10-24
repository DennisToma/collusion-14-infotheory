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

    def run_fixture(self, *, core_steps=None):
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
        with patch.object(verify_release, "ROOT", self.root), patch.object(verify_release, "git", fake_git), \
             patch.object(verify_release, "RENDER", steps), \
             patch.object(verify_release, "CORE_EVAL", core_steps or []), patch.object(sys, "argv", argv), \
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


if __name__ == "__main__":
    unittest.main()
