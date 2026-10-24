"""Focused invariants for the new simulator modes and group null."""
import unittest
from unittest.mock import patch

import numpy as np

from detectors.infotheory import PAIR_NAMES, _design, _resid, score_groups, score_run
from experiments.p2_scripted import cusum_path, first_alarm, level_scores, surrogate_p
from sim.market import AGENTS, profits, run_game


def prices(rows):
    return np.array([[a['price'] for a in r['agents']] for r in rows])


class SimulatorTests(unittest.TestCase):
    def test_coalitions_share_signal_and_labels(self):
        for members in (['C', 'A', 'B'], AGENTS):
            rows, gt = run_game('coalition', 200, 30, 'B', coalition=members, strength=1)
            P = prices(rows)
            cols = [AGENTS.index(a) for a in members]
            self.assertTrue(np.all(P[:, cols] == P[:, cols[0], None]))
            self.assertIsNone(gt['assigned_pair'])
            self.assertEqual(gt['assigned_coalition'], sorted(members))
            self.assertTrue(gt['private_channel_enabled'])
        rows, gt = run_game('coalition', 200, 30, 'A', coalition=AGENTS, strength=1,
                            collusion_type='tft', hard_negative='shared_seed', hn_pair=['A', 'B'])
        self.assertTrue(np.all(prices(rows) == prices(rows)[:, :1]))
        self.assertEqual(gt['collusion_type'], 'signal')
        for coalition in (['A', 'B'], ['A', 'A', 'B'], ['A', 'B', 'E']):
            with self.assertRaises(ValueError):
                run_game('invalid', 200, 10, 'A', coalition=coalition)
        with self.assertRaises(ValueError):
            run_game('invalid', 200, 10, 'A', pair=['A', 'B'], coalition=['A', 'B', 'C'])

    def test_onset_prefix_is_control_for_every_collusion_type(self):
        control, _ = run_game('same', 201, 30, 'B')
        for typ in ('signal', 'fixed_high', 'tft'):
            rows, gt = run_game('same', 201, 30, 'B', pair=['A', 'C'], strength=1, collusion_type=typ, onset=15)
            self.assertEqual(rows[:15], control[:15])
            self.assertEqual(gt['onset'], 15)
        rows, gt = run_game('same', 201, 30, 'B', coalition=['A', 'B', 'C'], strength=1, onset=30)
        self.assertEqual(rows, control)
        self.assertFalse(gt['realized_collusion'])

    def test_private_cost_context_profit_and_public_state(self):
        seen = []

        def policy(ctx):
            seen.append((ctx.me, ctx.cost))
            return 12

        with patch('sim.market.quantal_br', policy):
            rows, gt = run_game('cost', 202, 4, 'A', cost_offsets={'A': 2, 'C': 2})
        self.assertEqual(seen, [(0, 8), (1, 6), (2, 8), (3, 6)] * 4)
        expected = profits([12] * 4, [8, 6, 8, 6], 'low')
        self.assertTrue(np.array_equal(expected, profits([12] * 4, dict(zip(AGENTS, [8, 6, 8, 6])), 'low')))
        for row in rows:
            self.assertEqual(row['market'], {'demand_shock': 'low', 'cost': 6})
            self.assertEqual([a['profit'] for a in row['agents']], [round(float(p), 3) for p in expected])
        self.assertEqual(gt['cost_offsets'], {'A': 2, 'C': 2})
        plain, _ = run_game('zero', 203, 10, 'B')
        zero, _ = run_game('zero', 203, 10, 'B', cost_offsets={a: 0 for a in AGENTS})
        self.assertEqual(plain, zero)


class DetectorTests(unittest.TestCase):
    def test_pair_equivalence_including_null_and_design(self):
        rng = np.random.default_rng(204)
        P = rng.choice([8, 10, 12, 14, 16], size=(80, 4)).astype(float)
        S = rng.integers(0, 4, size=80)
        P[:, 1] = P[:, 0]  # also check clipping at perfect pair correlation
        pair = score_run(P, S, B=25, seed=205)
        group = score_groups(P, S, B=25, seed=205)
        self.assertEqual(group['_run_p']['tc2'], pair['_run_p']['pcmi'])
        self.assertEqual(group['_n_null'], pair['_n_null'])
        for name in PAIR_NAMES:
            self.assertAlmostEqual(group[name]['score'], pair[name]['score']['pcmi'])
            self.assertEqual(group[name]['p'], pair[name]['p']['pcmi'])
        self.assertEqual(len([k for k in group if not k.startswith('_')]), 11)
        self.assertAlmostEqual(group['ABC']['synergy'], group['ABC']['score'] - sum(group[p]['score'] for p in ('AB', 'AC', 'BC')))

    def test_no_test_with_insufficient_draws_and_constant_columns(self):
        P = np.ones((10, 4)) * 12
        result = score_groups(P, np.zeros(10, int), B=25, seed=206)
        self.assertEqual(result['_n_null'], 0)  # four shifts cannot fit at min separation 3
        self.assertTrue(all(p == 1 for p in result['_run_p'].values()))
        self.assertTrue(all(np.isfinite(d['score']) and d['p'] == 1 for k, d in result.items() if not k.startswith('_')))

    def test_group_tc_matches_direct_correlation_determinant(self):
        rng = np.random.default_rng(207)
        P = rng.normal(size=(100, 4))
        P[:, 1] += 0.6 * P[:, 0]
        P[:, 2] -= 0.4 * P[:, 0]
        S = rng.integers(0, 4, 100)
        idx = np.arange(1, len(P))
        X = _design(S, P, idx)
        R = np.column_stack([_resid(P[idx, k], X) for k in range(4)])
        C = np.corrcoef(R, rowvar=False)
        result = score_groups(P, S, B=0)
        for name in ('ABC', 'ABD', 'ACD', 'BCD', 'ABCD'):
            cols = [AGENTS.index(a) for a in name]
            expected = -0.5 * np.linalg.slogdet(C[np.ix_(cols, cols)])[1]
            self.assertAlmostEqual(result[name]['score'], expected, places=9)

    def test_levels_cusum_and_control_leave_one_out(self):
        P = np.tile([14, 14, 10, 10], (4, 1))
        pair, market, mean = level_scores(P, [6, 8, 6, 8])
        self.assertEqual(pair['AB'], 4)
        self.assertEqual(market['AB'], 3)
        self.assertEqual(mean, 1)
        self.assertEqual(cusum_path(P), [3.5, 7, 10.5, 14])
        self.assertEqual(first_alarm(cusum_path(P), 7), 2)
        refs = [{'run_id': str(k), 'scores': {'pair_level': k}} for k in range(30)]
        self.assertEqual(surrogate_p(refs[-1], refs, 'pair_level'), 1 / 30)
        self.assertEqual(surrogate_p({'run_id': 'new', 'scores': {'pair_level': 31}}, refs, 'pair_level'), 1 / 31)


if __name__ == '__main__':
    unittest.main()
