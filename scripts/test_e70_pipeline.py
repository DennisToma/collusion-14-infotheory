"""Synthetic E70 integrity/stopping/declaration checks; no real experiment data or LLM calls.

uv run python scripts/test_e70_pipeline.py
"""
from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import e70_followup
import e70_followup_rule
import e70_grid
from e1_grid import FACTORS, cells, command, followup_cells
from e70_inputs import load_games, require_followup_ready, require_grid_ready

EARLY = datetime(2026, 10, 24, 22, tzinfo=timezone.utc)
LATE = datetime(2026, 10, 25, 8, tzinfo=timezone.utc)
BASELINE = "b87f5db"  # last commit before input-only hardening; fixed so reruns remain meaningful


class InputChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="c14-e70-test-", dir="/var/tmp")
        self.root = Path(self.tmp.name)
        self.gt = dict(run_id="fixture_A_000", T=20, condition="A", model=dict.fromkeys("ABCD", "fixture"))
        self.rows = [dict(run_id=self.gt["run_id"], round=t,
                          agents=[dict(id=a, price=10) for a in "ABCD"]) for t in range(20)]

    def tearDown(self):
        self.tmp.cleanup()

    def load(self, gt=None, rows=None):
        gs = [self.gt] if gt is None else gt
        rs = self.rows if rows is None else rows
        (self.root / "ground_truth.jsonl").write_text("".join(json.dumps(g) + "\n" for g in gs))
        (self.root / "trajectories.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rs))
        return load_games(self.root, "fixture", conditions=("A", "C"))

    def test_complete_and_reordered_rounds(self):
        gt, rows, bad = self.load(rows=list(reversed(self.rows)))
        self.assertEqual(len(gt), 1)
        self.assertEqual([r["round"] for r in rows[self.gt["run_id"]]], list(range(20)))
        self.assertEqual(bad, 0)

    def test_short_duplicate_and_missing_rounds_rejected(self):
        for rows in (self.rows[:19], self.rows + [self.rows[0]], self.rows[1:] + [self.rows[-1]], []):
            with self.subTest(length=len(rows)), self.assertRaisesRegex(ValueError, "rounds 0..19"):
                self.load(rows=rows)

    def test_duplicate_completion_marker_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate ground truth"):
            self.load(gt=[self.gt, self.gt])

    def test_wrong_horizon_and_condition_rejected(self):
        for g in (dict(self.gt, T=19), dict(self.gt, condition="B")):
            with self.assertRaises(ValueError):
                self.load(gt=[g])

    def test_missing_model_or_fallback_excluded(self):
        for models in ({}, None, {"A": "fixture"}, dict.fromkeys("ABCD", "other"),
                       dict(self.gt["model"], C="other")):
            with self.subTest(models=models):
                gt, rows, bad = self.load(gt=[dict(self.gt, model=models)])
                self.assertEqual((gt, rows, bad), ({}, {}, 1))

    def test_seller_order_and_nonfinite_prices_rejected(self):
        for kind in ("seller order", "non-finite"):
            rows = copy.deepcopy(self.rows)
            if kind == "seller order":
                rows[0]["agents"].reverse()
            else:
                rows[0]["agents"][0]["price"] = float("nan")
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                self.load(rows=rows)

    def test_orphan_trajectory_not_a_completed_game(self):
        orphan = dict(self.rows[0], run_id="interrupted_A_001")
        gt, rows, bad = self.load(rows=self.rows + [orphan])
        self.assertEqual(set(rows), set(gt))
        self.assertEqual(bad, 0)


class StoppingChecks(unittest.TestCase):
    def test_grid_complete_before_cutoff(self):
        require_grid_ready(6, now=EARLY)

    def test_grid_partial_only_at_cutoff_or_dry(self):
        for n in (1, 2, 5):
            with self.assertRaisesRegex(ValueError, "partial analysis"):
                require_grid_ready(n, now=EARLY)
            require_grid_ready(n, now=LATE)
            require_grid_ready(n, now=EARLY, dry=True)

    def test_grid_zero_or_extra_sweeps_rejected(self):
        for n in (0, 7):
            with self.assertRaises(ValueError):
                require_grid_ready(n, now=LATE)

    def test_followup_complete_or_declared_deadline(self):
        self.assertTrue(require_followup_ready([12] * 4, now=EARLY))
        with self.assertRaisesRegex(ValueError, "incomplete follow-up"):
            require_followup_ready([12, 12, 11, 10], now=EARLY)
        self.assertFalse(require_followup_ready([12, 12, 11, 10], now=LATE))
        self.assertFalse(require_followup_ready([1] * 4, now=EARLY, dry=True))
        for counts in ([12, 12, 0, 12], [13] * 4):
            with self.assertRaises(ValueError):
                require_followup_ready(counts, now=LATE)

    def test_partial_grid_stops_before_judging_or_evaluation(self):
        def cell_fixture(prefix, c, dry):
            gt = {f"fixture_{cond}_{k:03d}": dict(condition=cond) for cond in ("A", "C") for k in range(5)}
            return "fixture", gt, dict.fromkeys(gt, ["not read"]), 0
        with patch.object(e70_grid, "load_cell", side_effect=cell_fixture), \
             patch.object(e70_grid, "require_grid_ready", side_effect=lambda s, **kw: require_grid_ready(s, now=EARLY)), \
             patch.object(e70_grid.subprocess, "run", side_effect=AssertionError("must not call judge/evaluator")), \
             patch.object(sys, "argv", ["e70_grid.py", "--label", "--eval"]), \
             contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(ValueError, "partial analysis"):
            e70_grid.main()


class DeclarationChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="c14-e70-rule-", dir="/var/tmp")
        self.root = Path(self.tmp.name)
        (self.root / "results/eval").mkdir(parents=True)
        self.result = dict(complete_sweeps=6,
                           main_effects={"framing": dict(effect=-.8, ci=[-1.5, .1]),
                                         "model": dict(effect=.3, ci=[-.2, .8])})
        self.source = self.root / "results/eval/e70_grid.json"
        self.source.write_text(json.dumps(self.result))
        self.dest = self.root / "results/eval/e70_followup_declared.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_largest_effect_sign_and_skip_rules(self):
        self.assertEqual(e70_followup_rule.decide(self.result, EARLY)["decision"], "RUN framing -1")
        strong = copy.deepcopy(self.result)
        strong["main_effects"]["framing"] = dict(effect=-1.2, ci=[-2, -.4])
        self.assertTrue(e70_followup_rule.decide(strong, EARLY)["decision"].startswith("SKIP E70 effect"))
        after = datetime(2026, 10, 25, 0, 31, tzinfo=timezone.utc)
        self.assertTrue(e70_followup_rule.decide(self.result, after)["decision"].startswith("SKIP E70 analysis"))

    def test_incomplete_grid_cannot_declare_followup_early(self):
        with self.assertRaises(ValueError):
            e70_followup_rule.decide(dict(self.result, complete_sweeps=5), EARLY)

    def test_frozen_declaration_is_idempotent_and_detects_changed_source(self):
        with patch.object(e70_followup_rule, "ROOT", self.root), contextlib.redirect_stdout(io.StringIO()):
            e70_followup_rule.main()
            saved = self.dest.read_bytes()
            e70_followup_rule.main()
            self.assertEqual(self.dest.read_bytes(), saved)
            self.source.write_text(json.dumps(dict(self.result, changed=True)))
            with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                e70_followup_rule.main()
            self.assertEqual(self.dest.read_bytes(), saved)

    def test_analysis_must_match_declared_factor_sign_and_source(self):
        declaration = dict(decision="RUN framing -1", e70_sha256=hashlib.sha256(self.source.read_bytes()).hexdigest())
        self.dest.write_text(json.dumps(declaration))
        with patch.object(e70_followup, "ROOT", self.root):
            self.assertEqual(e70_followup.check_declaration("framing", -1), hashlib.sha256(self.dest.read_bytes()).hexdigest())
            for factor, sign in (("framing", 1), ("model", -1)):
                with self.assertRaises(ValueError):
                    e70_followup.check_declaration(factor, sign)
            self.source.write_text("{}")
            with self.assertRaises(ValueError):
                e70_followup.check_declaration("framing", -1)


class GenerationSwitches(unittest.TestCase):
    def test_followup_changes_only_selected_factor_and_routes_switches(self):
        for factor in FACTORS:
            lo, hi = followup_cells(factor)
            self.assertEqual([f for f in FACTORS if lo["levels"][f] != hi["levels"][f]], [factor])
            for c in (lo, hi):
                cmd = command(c, 0, "fixture", False, n=12)
                lv = c["levels"]
                self.assertEqual(cmd[cmd.index("--n") + 1], "12")
                self.assertEqual(cmd[cmd.index("--conds") + 1], "B,D" if lv["shocks"] == "random" else "A,C")
                for flag, present in (("--no-private-cost", lv["cost"] == "public"),
                                      ("--hide-rivals", lv["rivals"] == "hidden"),
                                      ("--memory", lv["memory"] == "full"),
                                      ("--short-memory", lv["memory"] == "short"),
                                      ("--longrun", lv["framing"] == "longrun")):
                    self.assertEqual(flag in cmd, present)
                self.assertEqual(cmd[cmd.index("--model") + 1], lv["model"])

    def test_followup_base_matches_c00(self):
        base = cells()[0]["levels"]
        for f in FACTORS:
            self.assertEqual(followup_cells(f)[0]["levels"], base)


class StatisticsCompatibility(unittest.TestCase):
    """Exercise the old and new analyses on identical generated fixtures, with no real E70 inputs."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="c14-e70-parity-", dir="/var/tmp")
        self.root = Path(self.tmp.name)
        (self.root / "results/eval").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def fixture(self, c, name, n):
        dest = self.root / "data" / name
        dest.mkdir(parents=True)
        gt, rows, scores = [], [], {d: {} for d in e70_grid.DETS}
        conds = ("B", "D") if c["levels"]["shocks"] == "random" else ("A", "C")
        for k in range(n):
            for chan, cond in enumerate(conds):
                rid = f"{name}_{cond}_{k:03d}"
                gt.append(dict(run_id=rid, condition=cond, T=20, model=dict.fromkeys("ABCD", "dry"),
                               assigned_pair=["A", "B"] if chan else None))
                # Vary both signs, game prices, shock states, messages and detector orderings.
                shift = c["signs"]["framing"] * chan + k % 3
                for t in range(20):
                    rows.append(dict(run_id=rid, round=t, market=dict(cost=6 if t % 2 else 8),
                                     agents=[dict(id=a, price=11 + shift + (t + i) % 2,
                                                  public_message="post" if (t + i + k) % 3 == 0 else "")
                                             for i, a in enumerate("ABCD")]))
                for j, d in enumerate(scores):
                    scores[d][rid] = ((k * (j + 1) + chan * c["signs"]["model"]) % 7) / 7
        (dest / "ground_truth.jsonl").write_text("".join(json.dumps(g) + "\n" for g in gt))
        (dest / "trajectories.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        (self.root / "results/eval" / f"{name}.json").write_text(json.dumps(dict(run_scores={"20": scores})))

    def original(self, script, argv):
        source = subprocess.check_output(["git", "show", f"{BASELINE}:scripts/{script}"],
                                         cwd=e70_grid.ROOT, text=True)
        # Compile under its real module name so top-level main does not run before ROOT is replaced.
        ns = dict(__file__=str(e70_grid.ROOT / "scripts" / script), __name__="baseline")
        exec(compile(source, ns["__file__"], "exec"), ns)
        ns["ROOT"] = self.root
        with patch.object(sys, "argv", [script, *argv]), contextlib.redirect_stdout(io.StringIO()):
            ns["main"]()

    def test_grid_every_existing_output_field_exact(self):
        for c in cells():
            self.fixture(c, f"fixture_{c['cell']}", 6)
        argv = ["--prefix", "fixture", "--dry", "--B", "100", "--out", "parity"]
        self.original("e70_grid.py", argv)
        output = self.root / "results/eval/parity.json"
        expected = output.read_bytes()
        with patch.object(e70_grid, "ROOT", self.root), patch.object(sys, "argv", ["e70_grid.py", *argv]), \
             contextlib.redirect_stdout(io.StringIO()):
            e70_grid.main()
        self.assertEqual(output.read_bytes(), expected)

    def test_followup_every_existing_output_field_exact(self):
        for c in followup_cells("framing"):
            self.fixture(c, f"fixture_{c['cell']}", 12)
        argv = ["--prefix", "fixture", "--factor", "framing", "--sign", "1", "--dry", "--B", "100"]
        self.original("e70_followup.py", argv)
        output = self.root / "results/eval/e70_followup_dry.json"
        expected = json.loads(output.read_text())
        with patch.object(e70_followup, "ROOT", self.root), \
             patch.object(sys, "argv", ["e70_followup.py", *argv]), contextlib.redirect_stdout(io.StringIO()):
            e70_followup.main()
        actual = json.loads(output.read_text())
        for key in ("declaration_sha256", "planned_games_per_level_arm", "complete", "sample_status"):
            actual.pop(key)
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    if "--evidence" in sys.argv:
        sys.argv.remove("--evidence")
        suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
        result = unittest.TextTestRunner(verbosity=1).run(suite)
        evidence = dict(time_utc=datetime.now(timezone.utc).isoformat(),
                        command="uv run python scripts/test_e70_pipeline.py --evidence",
                        synthetic_only=True, baseline_revision=BASELINE, tests_run=result.testsRun,
                        failures=len(result.failures), errors=len(result.errors), passed=result.wasSuccessful(),
                        grid_existing_json_bytes_exact=not any("test_grid_every_existing_output_field_exact" in str(t)
                                                              for t, _ in result.failures + result.errors),
                        followup_existing_json_fields_exact=not any("test_followup_every_existing_output_field_exact" in str(t)
                                                                   for t, _ in result.failures + result.errors))
        (e70_grid.ROOT / "results/e70_pipeline_check.json").write_text(json.dumps(evidence, indent=2) + "\n")
        raise SystemExit(0 if result.wasSuccessful() else 1)
    unittest.main()
