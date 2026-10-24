"""Synthetic registered-analysis → manuscript integration; never open real E68/E70 outcomes.

uv run python scripts/test_p2_landing.py --evidence
"""
from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

import e70_grid
import e70_fig
import p2_landing
import p2_tables
from e1_grid import cells
from report_tables import parse_tables
import test_e68_pipeline as cda_tests
import test_e70_pipeline as grid_tests

ROOT = p2_landing.ROOT


class LandingChecks(unittest.TestCase):
    evidence = {}
    @classmethod
    def setUpClass(cls):
        # Reuse the pipeline fixtures, executing the actual analyses without API calls.
        cls.grid_fixture = grid_tests.StatisticsCompatibility()
        cls.grid_fixture.setUp()
        cls.cda_fixture = cda_tests.AnalysisCompatibility()
        cls.cda_fixture.setUp()
        for c in cells():
            cls.grid_fixture.fixture(c, f"fixture_{c['cell']}", 6)
        argv = ["e70_grid.py", "--prefix", "fixture", "--dry", "--B", "100"]
        with patch.object(e70_grid, "ROOT", cls.grid_fixture.root), patch.object(sys, "argv", argv), \
             contextlib.redirect_stdout(io.StringIO()):
            e70_grid.main()
        cls.grid_path = cls.grid_fixture.root / "results/eval/e70_grid.json"
        cls.grid = json.loads(cls.grid_path.read_text())
        cls.cda = cls.cda_fixture.run_current(permutations=0)
        cls.cda_path = cls.cda_fixture.root / "results/eval/e68_cda.json"
        cls.evidence["synthetic_inputs"] = dict(grid_sweeps=cls.grid["complete_sweeps"],
                                               grid_games=cls.grid["n_games"], cda_games=30,
                                               grid_sha256=hashlib.sha256(cls.grid_path.read_bytes()).hexdigest(),
                                               cda_sha256=hashlib.sha256(cls.cda_path.read_bytes()).hexdigest())

    @classmethod
    def tearDownClass(cls):
        cls.grid_fixture.tearDown()
        cls.cda_fixture.tearDown()

    def test_registered_analysis_tables_survive_renderer(self):
        for render, data, builder, path in ((p2_landing.e70, self.grid, p2_tables.p214, self.grid_path),
                                            (p2_landing.e68, self.cda, p2_tables.p212, self.cda_path)):
            with self.subTest(render=render.__name__):
                expected = parse_tables(builder(path), include_header=True)
                actual = parse_tables(render(data)["section"], include_header=True)
                self.assertEqual(expected, actual)

    def test_full_grid_denominators_and_claim_scope(self):
        r = p2_landing.e70(self.grid)
        self.assertIn("6 complete sweeps, 192 games (full declared set)", r["section"])
        self.assertEqual(r["completion"], "6 sweeps complete")
        self.assertIn(f"{self.grid['primary']['cells_d_pos']}/16", r["abstract"])
        self.assertIn("positive point estimate", r["section"])
        self.assertIn("not per-cell CI tests", r["section"])
        self.assertIn("do not append", r["denominators"])
        self.assertIn("Factor M includes model and its board use", r["section"])
        self.assertEqual(len(parse_tables(r["appendix"])[0]), 16)

    def test_unrounded_analysis_counts_are_authoritative(self):
        d = copy.deepcopy(self.grid)
        d["primary"]["cells_d_pos"] = 1
        d["level_vs_pcmi"].update(cells_level_gt_pcmi=1, ties=15)
        # Saved precision can erase tiny positive differences; do not recompute them.
        for v in d["per_cell"].values():
            v["d"] = 0.
            v["auroc"].update(market_level=.5, pcmi=.5)
        text = p2_landing.e70(d)["abstract"]
        self.assertIn("positive in 1/16", text)
        self.assertIn("exceeded pCMI in 1/16", text)

    def test_grid_all_ties_and_missing_labels_render_honestly(self):
        d = copy.deepcopy(self.grid)
        d["level_vs_pcmi"].update(cells_level_gt_pcmi=0, ties=16, sign_test_p_excl_ties=None)
        text = p2_landing.e70(d)["section"]
        self.assertIn("not evaluable (all ties)", text)
        self.assertIn("96 unlabelled", text)

    def test_partial_grid_never_announces_six_sweeps(self):
        d = copy.deepcopy(self.grid)
        d.update(complete_sweeps=2, n_games=64)
        for v in d["per_cell"].values():
            v["n"] = [2, 2]
        r = p2_landing.e70(d)
        self.assertIn("deadline-truncated balanced sample", r["section"])
        self.assertIn("2 complete sweeps", r["completion"])
        self.assertNotIn("6 sweeps complete", " ".join(r.values()))

    def test_grid_bad_counts_rejected(self):
        for key, value in (("complete_sweeps", 7), ("complete_sweeps", 0), ("n_games", 191)):
            d = copy.deepcopy(self.grid)
            d[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                p2_landing.e70(d)
        d = copy.deepcopy(self.grid)
        d["per_cell"]["c00"]["n"] = [5, 6]
        with self.assertRaises(ValueError):
            p2_landing.e70(d)
        d = copy.deepcopy(self.grid)
        d["per_cell"]["c00"]["labelled"] = 7
        with self.assertRaisesRegex(ValueError, "execution/label"):
            p2_landing.e70(d)

    def test_cda_keeps_gate_and_parse_failures_distinct(self):
        r = p2_landing.e68(self.cda)
        self.assertIn("15 comms / 15 nocomms games (full declared set)", r["section"])
        self.assertIn(self.cda["verdict"], r["section"])
        pf = self.cda["parse_failures"]
        self.assertIn(f"{pf['total']} parse failures in {pf['runs_with_any']}/30 runs", r["glance"])
        self.assertIn("would not verify an agreement", r["section"])

    def test_cda_all_saved_gate_verdicts_are_preserved(self):
        # The renderer must not replace the frozen gate with a detector-based decision.
        for status, verdict in (("CI includes zero", "no collusion elicited; detector comparison uninformative"),
                                ("negative ask effect", "communication lowers asks; detector comparison uninformative for collusion"),
                                ("positive ask effect", "dependence visible"),
                                ("positive ask effect", "inconclusive")):
            d = copy.deepcopy(self.cda)
            d["manipulation_check"]["status"], d["verdict"] = status, verdict
            with self.subTest(verdict=verdict):
                r = p2_landing.e68(d)
                self.assertIn(verdict, r["section"])
                self.assertIn(verdict, r["abstract"])

    def test_cda_no_trades_and_unmatched_interim_seeds(self):
        d = copy.deepcopy(self.cda)
        d.update(n_nocomms=14, complete=False)
        d["parse_failures"]["n_runs"] = 29
        d["pcmi_flags_alpha05"][3] = 14
        d["manipulation_check"].update(n_matched_seeds=14, n_unmatched_comms=1, n_unmatched_nocomms=0)
        d["auroc"]["trade"].update(auroc=None, ci=None, n=[0, 14])
        d["mean"]["trade"] = [None, 2.]
        text = p2_landing.e68(d)["section"]
        self.assertIn("deadline-truncated interim sample", text)
        self.assertIn("14 matched seeds, 1 / 0 unmatched", text)
        self.assertIn("not evaluable (no trades in an arm) (n 0 + 14)", text)

    def test_cda_bad_denominators_rejected(self):
        for key, value in (("complete", False), ("n_nocomms", 16)):
            d = copy.deepcopy(self.cda)
            d[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                p2_landing.e68(d)

    def test_nonfinite_results_rejected(self):
        for render, source in ((p2_landing.e70, self.grid), (p2_landing.e68, self.cda)):
            d = copy.deepcopy(source)
            d["bad"] = float("nan")
            with self.assertRaisesRegex(ValueError, "non-finite"):
                render(d)

    def test_line_limits_and_determinism(self):
        for render, source, limit in ((p2_landing.e70, self.grid, 15), (p2_landing.e68, self.cda, 10)):
            r = render(source)
            self.assertEqual(r, render(copy.deepcopy(source)))
            prose = [line for line in r["section"].splitlines() if not line.startswith("|")]
            self.assertLessEqual(len(prose), limit)
            self.evidence.setdefault("section_non_table_lines", {})[render.__name__] = len(prose)
            self.evidence.setdefault("fragment_sha256", {})[render.__name__] = hashlib.sha256(
                json.dumps(r, sort_keys=True).encode()).hexdigest()

    def test_actual_grid_figure_is_deterministic(self):
        import matplotlib.pyplot as plt
        output = self.grid_fixture.root / "figures/e70_grid.png"
        argv = ["e70_fig.py"]
        with patch.object(e70_fig, "ROOT", self.grid_fixture.root), patch.object(sys, "argv", argv), \
             contextlib.redirect_stdout(io.StringIO()):
            e70_fig.main()
            plt.close("all")
            first = output.read_bytes()
            e70_fig.main()
            plt.close("all")
        self.assertEqual(first, output.read_bytes())
        self.assertTrue(first.startswith(b"\x89PNG"))
        self.evidence["synthetic_grid_figure_sha256"] = hashlib.sha256(first).hexdigest()

    def test_actual_report_accepts_both_synthetic_sections(self):
        report = (ROOT / "REPORT.md").read_text()
        for start, end, rendered in (("**P2.12", "**P2.13", p2_landing.e68(self.cda)["section"]),
                                     ("**P2.14", "## 5. Limitations", p2_landing.e70(self.grid)["section"])):
            a, b = report.index(start), report.index(end)
            report = report[:a] + rendered + "\n\n" + report[b:]
        builders = {}
        for key, value in p2_tables.BUILDERS.items():
            if key == "P2.13":
                builders["P2.12"] = lambda: p2_tables.p212(data=self.cda)
            if key not in ("P2.12", "P2.14"):
                builders[key] = value
        builders["P2.14"] = lambda: p2_tables.p214(data=self.grid)
        diagnostics = io.StringIO()
        with patch.object(p2_tables, "BUILDERS", builders), contextlib.redirect_stdout(diagnostics):
            self.assertTrue(p2_tables.check(report))
        self.evidence["synthetic_report_table_check"] = diagnostics.getvalue().strip()

    def test_cli_reads_saved_results_only_and_does_not_write(self):
        for experiment, path in (("e70", self.grid_path), ("e68", self.cda_path)):
            root = path.parents[2]
            before = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in root.rglob("*") if p.is_file()}
            out = subprocess.check_output([sys.executable, str(ROOT / "scripts/p2_landing.py"),
                                           experiment, "--input", str(path), "--part", "all"], cwd=root, text=True)
            self.assertIn("### section", out)
            after = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in root.rglob("*") if p.is_file()}
            self.assertEqual(before, after)


if __name__ == "__main__":
    if "--evidence" in sys.argv:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(LandingChecks)
        result = unittest.TextTestRunner(verbosity=1).run(suite)
        evidence = dict(time_utc=datetime.now(timezone.utc).isoformat(),
                        command="uv run python scripts/test_p2_landing.py --evidence", synthetic_only=True,
                        tests_run=result.testsRun, failures=len(result.failures), errors=len(result.errors),
                        passed=result.wasSuccessful(),
                        scope="actual E70/E68 analyses on synthetic inputs → source-derived fragments → real REPORT table checker; no real outcomes",
                        verification=LandingChecks.evidence,
                        implementation_sha256={name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                                               for name in ("scripts/p2_landing.py", "scripts/p2_tables.py", "scripts/test_p2_landing.py")})
        (ROOT / "results/p2_landing_check.json").write_text(json.dumps(evidence, indent=2) + "\n")
        raise SystemExit(0 if result.wasSuccessful() else 1)
    unittest.main()
