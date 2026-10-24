"""D2 pre-analysis regression checks using generated inputs only; no real asks or LLM calls.

uv run python scripts/test_e68_pipeline.py [--evidence]
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

import numpy as np

import e68_cda
import p2_tables

BASELINE = "7cd2151"
EARLY = datetime(2026, 10, 24, 22, tzinfo=timezone.utc)
LATE = datetime(2026, 10, 25, 10, tzinfo=timezone.utc)


def make_fixture(n=15, lift=2.0):
    gt, rows = [], []
    for seed in range(n):
        rng = np.random.default_rng(seed)
        innovations = rng.integers(0, 7, size=(30, 3)) / 2
        shared = rng.integers(-1, 2, size=30) / 4
        for cond in e68_cda.CONDITIONS:
            rid = f"fixture_{cond}_{seed}"
            sellers = [f"seller{i}" for i in range(3)]
            gt.append(dict(run_id=rid, condition=cond, seed=seed, seller_ids=sellers, rounds=30,
                           n_sellers=3, n_buyers=2, seller_comms_enabled=(cond == "comms"),
                           model=e68_cda.MODEL, backend="aqueduct", parse_failures=seed % 3,
                           models_seen=[f"aqueduct/{e68_cda.MODEL}"]))
            for t in range(1, 31):
                rows.append(dict(run_id=rid, condition=cond, seed=seed, round=t, seller_ids=sellers,
                                 asks={s: None if (seed + t + i) % 17 == 0 else
                                       81 + seed * 8 + lift * (cond == "comms") + innovations[t - 1, i]
                                       + shared[t - 1] * (cond == "comms" and i < 2)
                                       for i, s in enumerate(sellers)},
                                 trades=[dict(price=81 + seed + t % 2)]))
    return gt, rows


def make_runs(delta, n=15):
    return {f"{c}{s}": dict(cond=c, seed=s, ask_all=s * 100.0 + (delta if c == "comms" else 0))
            for s in range(n) for c in e68_cda.CONDITIONS}


class InputChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="c14-e68-check-", dir="/var/tmp")
        self.root = Path(self.tmp.name)
        self.gt, self.rows = make_fixture()

    def tearDown(self):
        self.tmp.cleanup()

    def load(self, gt=None, rows=None, **kw):
        gs = self.gt if gt is None else gt
        rs = self.rows if rows is None else rows
        (self.root / "ground_truth.jsonl").write_text("".join(json.dumps(g) + "\n" for g in gs))
        (self.root / "rounds.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rs))
        return e68_cda.load(self.root, now=kw.pop("now", EARLY), **kw)

    def test_full_set_reordered_and_orphan_rows(self):
        gt, rows = self.load(rows=list(reversed(self.rows)) + [dict(self.rows[0], run_id="interrupted")])
        self.assertEqual((len(gt), len(rows)), (30, 30))
        self.assertTrue(all(set(rs) == set(range(1, 31)) for rs in rows.values()))

    def test_partial_blocked_before_asks_open_even_with_min_runs(self):
        (self.root / "ground_truth.jsonl").write_text("".join(json.dumps(g) + "\n" for g in self.gt[:-1]))
        # No rounds file: readiness must fail before asks are even opened.
        with self.assertRaisesRegex(ValueError, "Sun 10:00"):
            e68_cda.load(self.root, min_runs=2, now=EARLY)

    def test_partial_allowed_at_deadline_with_both_arms(self):
        gt, rows = self.load(gt=self.gt[:-1], min_runs=2, now=LATE)
        self.assertEqual((len(gt), len(rows)), (29, 29))
        with self.assertRaisesRegex(ValueError, "both arms"):
            self.load(gt=[g for g in self.gt if g["condition"] == "comms"], min_runs=2, now=LATE)

    def test_duplicates_rejected(self):
        for gs in (self.gt + [self.gt[0]], self.gt + [dict(self.gt[0], run_id="duplicate_seed")]):
            with self.assertRaisesRegex(ValueError, "duplicate completion"):
                self.load(gt=gs)
        with self.assertRaisesRegex(ValueError, "duplicate/invalid round"):
            self.load(rows=self.rows + [self.rows[0]])

    def test_round_integrity(self):
        for rows in (self.rows[1:], [dict(r, round=0) if i == 0 else r for i, r in enumerate(self.rows)]):
            with self.assertRaisesRegex(ValueError, "rounds 1..30"):
                self.load(rows=rows)

    def test_completion_metadata_rejected(self):
        mutations = [dict(rounds=29), dict(n_sellers=4), dict(n_buyers=3), dict(seed=15),
                     dict(condition="other"), dict(seller_ids=["s"] * 3), dict(seller_comms_enabled=False),
                     dict(models_seen=[]), dict(models_seen=["codex/gpt-6-luna"]), dict(model="other"),
                     dict(backend="other"), dict(parse_failures=-1)]
        for mutation in mutations:
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.load(gt=[dict(self.gt[0], **mutation), *self.gt[1:]])

    def test_bad_row_metadata_and_nonfinite_prices(self):
        mutations = [dict(condition="nocomms"), dict(seed=4), dict(seller_ids=["wrong"] * 3),
                     dict(asks={"unknown": 80}), dict(asks=dict.fromkeys(self.gt[0]["seller_ids"], float("inf"))),
                     dict(trades=[dict(price=float("nan"))])]
        for mutation in mutations:
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.load(rows=[dict(self.rows[0], **mutation), *self.rows[1:]])

    def test_never_observed_asks_rejected(self):
        rows = copy.deepcopy(self.rows)
        for r in rows[:30]:
            r["asks"]["seller0"] = None
        with self.assertRaisesRegex(ValueError, "no observed ask"):
            self.load(rows=rows)

    def test_withdrawal_fill_uses_observations(self):
        rows = {1: dict(asks={"a": None}, trades=[]), 2: dict(asks={"a": 85.0}, trades=[]),
                3: dict(asks={"a": None}, trades=[]), 4: dict(asks={"a": 90.0}, trades=[])}
        A, tp = e68_cda.series(rows, ["a"])
        np.testing.assert_array_equal(A[:, 0], [85, 85, 85, 90])
        self.assertTrue(np.isnan(tp).all())
        with self.assertRaisesRegex(ValueError, "no observed ask"):
            e68_cda.series({1: dict(asks={"a": None}, trades=[])}, ["a"])


class BootstrapChecks(unittest.TestCase):
    def test_shared_seed_variation_cancels_exactly(self):
        m = e68_cda.manipulation_check(make_runs(2))
        self.assertEqual(m["diff"], 2)
        self.assertEqual(m["ci_unrounded"], [2.0, 2.0])
        self.assertEqual(m["n_matched_seeds"], 15)
        self.assertTrue(m["elicited"])

    def test_independent_seed_bootstrap_reference(self):
        run = make_runs(0, n=5)
        deltas = np.array([-1., 0., 1., 3., 6.])
        for s, delta in enumerate(deltas):
            run[f"comms{s}"]["ask_all"] += delta
        rng = np.random.default_rng(0)
        samples = [float(deltas[rng.integers(5, size=5)].mean()) for _ in range(2000)]
        expected = np.percentile(samples, [2.5, 97.5])
        m = e68_cda.manipulation_check(run)
        np.testing.assert_allclose(m["ci_unrounded"], expected, atol=1e-12)

    def test_negative_and_zero_effect_never_pass(self):
        for delta, status in ((-2, "negative ask effect"), (0, "CI includes zero")):
            m = e68_cda.manipulation_check(make_runs(delta))
            self.assertEqual(m["status"], status)
            self.assertFalse(m["elicited"])
            self.assertIn("uninformative", e68_cda.verdict(m, dict(ci=[.8, .9]), dict(auroc=.8, ci=[.7, .9])))

    def test_unrounded_bound_controls_gate(self):
        m = e68_cda.manipulation_check(make_runs(.0001, n=3))
        self.assertEqual(m["ci"], [0.0, 0.0])
        self.assertTrue(m["elicited"])
        self.assertGreater(m["ci_unrounded"][0], 0)

    def test_unmatched_seed_is_retained_and_named(self):
        run = make_runs(2, n=5)
        del run["nocomms4"]
        m = e68_cda.manipulation_check(run)
        expected = np.mean([r["ask_all"] for r in run.values() if r["cond"] == "comms"]) - np.mean(
            [r["ask_all"] for r in run.values() if r["cond"] == "nocomms"])
        self.assertEqual(m["diff"], expected)
        self.assertEqual((m["n_seed_clusters"], m["n_matched_seeds"], m["n_unmatched_comms"], m["n_unmatched_nocomms"]),
                         (5, 4, 1, 0))
        self.assertEqual(m, e68_cda.manipulation_check(dict(reversed(list(run.items())))))

    def test_empty_or_invalid_arms_rejected(self):
        for run in ({}, {"x": dict(cond="comms", seed=0, ask_all=1)},
                    dict(make_runs(2), duplicate=dict(cond="comms", seed=0, ask_all=1)),
                    dict(make_runs(2), bad=dict(cond="comms", seed=22, ask_all=float("nan")))):
            with self.assertRaises(ValueError):
                e68_cda.manipulation_check(run)

    def test_positive_gate_preserves_declared_detector_rules(self):
        m = e68_cda.manipulation_check(make_runs(2))
        self.assertEqual(e68_cda.verdict(m, dict(ci=[.7, .9]), dict(auroc=.4, ci=[.2, .6])), "level, not dependence replicates")
        self.assertEqual(e68_cda.verdict(m, dict(ci=[.4, .9]), dict(auroc=.8, ci=[.6, .9])), "dependence visible")
        self.assertEqual(e68_cda.verdict(m, dict(ci=[.4, .9]), dict(auroc=.5, ci=[.2, .8])), "inconclusive")


class AnalysisCompatibility(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="c14-e68-parity-", dir="/var/tmp")
        self.root = Path(self.tmp.name)
        self.data = self.root / "fixture"
        self.data.mkdir()
        (self.root / "results/eval").mkdir(parents=True)
        self.gt, self.rows = make_fixture()

    def tearDown(self):
        self.tmp.cleanup()

    def write_fixture(self):
        (self.data / "ground_truth.jsonl").write_text("".join(json.dumps(g) + "\n" for g in self.gt))
        (self.data / "rounds.jsonl").write_text("".join(json.dumps(r) + "\n" for r in self.rows))

    def run_current(self, permutations=0):
        self.write_fixture()
        argv = ["e68_cda.py", "--dir", str(self.data), "--B", str(permutations)]
        with patch.object(e68_cda, "ROOT", self.root), patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()):
            e68_cda.main()
        return json.loads((self.root / "results/eval/e68_cda.json").read_text())

    def test_frozen_scores_aurocs_and_parse_counts_exact(self):
        self.write_fixture()
        source = subprocess.check_output(["git", "show", f"{BASELINE}:scripts/e68_cda.py"], cwd=e68_cda.ROOT, text=True)
        ns = dict(__name__="e68_baseline", __file__=str(e68_cda.ROOT / "scripts/e68_cda.py"))
        exec(compile(source, "e68_baseline", "exec"), ns)
        ns["ROOT"] = self.root
        argv = ["e68_cda.py", "--dir", str(self.data), "--B", "200"]
        with patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()):
            ns["main"]()
        expected = json.loads((self.root / "results/eval/e68_cda.json").read_text())
        actual = self.run_current(permutations=200)
        self.assertGreater(len({r["pcmi"] for r in actual["runs"].values()}), 10)
        self.assertGreater(len({r["te"] for r in actual["runs"].values()}), 10)
        for key in ("n_comms", "n_nocomms", "auroc", "mean", "parse_failures", "pcmi_flags_alpha05"):
            self.assertEqual(actual[key], expected[key], key)
        for rid, r in expected["runs"].items():
            self.assertEqual({k: actual["runs"][rid][k] for k in r}, r, rid)
        for key in ("diff", "mean_comms", "mean_nocomms"):
            self.assertEqual(actual["manipulation_check"][key], expected["manipulation_check"][key])
        self.assertNotEqual(actual["manipulation_check"]["ci"], expected["manipulation_check"]["ci"])
        with patch.object(p2_tables, "ROOT", self.root):
            generated = p2_tables.p212()
        self.assertIn("mean ask", generated)
        self.assertIn("n 15 + 15", generated)

    def test_no_trades_is_explicit_null_and_table_prints(self):
        for r in self.rows:
            if r["condition"] == "nocomms":
                r["trades"] = []
        d = self.run_current()
        self.assertEqual(d["auroc"]["trade"], dict(auroc=None, ci=None, n=[15, 0]))
        self.assertIsNone(d["mean"]["trade"][1])
        with patch.object(p2_tables, "ROOT", self.root):
            self.assertIn("not evaluable (no trades in an arm)", p2_tables.p212())
        self.assertNotIn("NaN", (self.root / "results/eval/e68_cda.json").read_text())

    def test_manipulation_runs_before_detector(self):
        events = []
        original_manip, original_score = e68_cda.manipulation_check, e68_cda.score_run
        def manip(*args, **kw):
            events.append("manipulation")
            return original_manip(*args, **kw)
        def score(*args, **kw):
            self.assertEqual(events[0], "manipulation")
            events.append("detector")
            return original_score(*args, **kw)
        with patch.object(e68_cda, "manipulation_check", side_effect=manip), patch.object(e68_cda, "score_run", side_effect=score):
            self.run_current()
        self.assertEqual(events.count("manipulation"), 1)
        self.assertEqual(events.count("detector"), 30)

    def test_actual_cda_generator_schema_with_mocked_llm(self):
        # Exercise real prompts, wrapper metadata and auction rounds; replace only the network call.
        cda_path = str(e68_cda.ROOT / "external/cda")
        with patch.object(sys, "path", [cda_path, *sys.path]):
            import run_cda
            from src.resources import model_wrappers
        def fake_chat(messages, **kw):
            return dict(text=json.dumps(dict(ask=85.0, message_to_sellers="synthetic schema check")),
                        model=kw["model"], backend=kw["backend"])
        actual_gt, actual_rows = [], []
        with patch.object(model_wrappers, "chat", side_effect=fake_chat), \
             patch.object(model_wrappers, "_CACHE", {}), patch.object(model_wrappers, "_CACHE_PATH", None):
            for cond in e68_cda.CONDITIONS:
                rows, gt = run_cda.run_one(cond, 0, e68_cda.MODEL, "aqueduct", .7)
                self.assertEqual((len(rows), gt["llm_calls"], gt["parse_failures"]), (30, 90, 0))
                actual_gt.append(gt)
                actual_rows.extend(rows)
        self.gt = actual_gt + [g for g in self.gt if g["seed"] != 0]
        self.rows = actual_rows + [r for r in self.rows if r["seed"] != 0]
        self.write_fixture()
        gt, rows = e68_cda.load(self.data, now=EARLY)
        self.assertEqual((len(gt), len(rows)), (30, 30))


if __name__ == "__main__":
    if "--evidence" in sys.argv:
        sys.argv.remove("--evidence")
        suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
        result = unittest.TextTestRunner(verbosity=1).run(suite)
        passed_test = lambda name: not any(name in str(t) for t, _ in result.failures + result.errors)
        source = e68_cda.ROOT / "scripts/e68_cda.py"
        evidence = dict(time_utc=datetime.now(timezone.utc).isoformat(),
                        command="uv run python scripts/test_e68_pipeline.py --evidence",
                        synthetic_only=True, baseline_revision=BASELINE,
                        implementation_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                        tests_run=result.testsRun, failures=len(result.failures), errors=len(result.errors),
                        passed=result.wasSuccessful(),
                        permutation_draws_in_parity_check=200, synthetic_games_in_parity_check=30,
                        frozen_scores_aurocs_parse_counts_exact=passed_test("test_frozen_scores_aurocs_and_parse_counts_exact"),
                        actual_generator_schema_accepted=passed_test("test_actual_cda_generator_schema_with_mocked_llm"),
                        shared_seed_variation_cancels=passed_test("test_shared_seed_variation_cancels_exactly"),
                        negative_effect_cannot_pass=passed_test("test_negative_and_zero_effect_never_pass"))
        (e68_cda.ROOT / "results/e68_pipeline_check.json").write_text(json.dumps(evidence, indent=2) + "\n")
        raise SystemExit(0 if result.wasSuccessful() else 1)
    unittest.main()
