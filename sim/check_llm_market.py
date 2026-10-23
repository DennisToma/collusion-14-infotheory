"""Tiny schema/invariant check: python -m sim.check_llm_market DATASET."""
import json
from pathlib import Path
import sys

from sim.market import AGENTS, PRICES, profits


def check(name):
    directory = Path('data') / name
    truths = [json.loads(s) for s in (directory / 'ground_truth.jsonl').read_text().splitlines()]
    rows = [json.loads(s) for s in (directory / 'trajectories.jsonl').read_text().splitlines()]
    assert len({g['run_id'] for g in truths}) == len(truths)
    assert {r['run_id'] for r in rows} == {g['run_id'] for g in truths}
    for gt in truths:
        assert {'condition', 'assigned_pair', 'private_channel_enabled', 'agreement_verified',
                'coordinated_actions_verified', 'realized_collusion', 'hard_negative', 'seed',
                'agent_policies', 'model', 'backend', 'sim_version', 'T', 'framing', 'private_chat'} <= gt.keys()
        assert all(gt[k] is None for k in ['agreement_verified', 'coordinated_actions_verified', 'realized_collusion'])
        pair = gt['assigned_pair'] or []
        assert len(pair) == (2 if gt['condition'] in 'CD' else 0)
        assert gt['private_channel_enabled'] == bool(pair)
        assert set(gt['model']) == set(gt['backend']) == set(AGENTS)
        game = [r for r in rows if r['run_id'] == gt['run_id']]
        assert [r['round'] for r in game] == list(range(gt['T']))
        for row in game:
            state = row['market']
            assert state['demand_shock'] in ['low', 'high'] and state['cost'] in [6, 8]
            if gt['condition'] in 'AC':
                assert state == {'demand_shock': 'low', 'cost': 6}
            assert [a['id'] for a in row['agents']] == AGENTS
            rewards = profits([a['price'] for a in row['agents']], state['cost'], state['demand_shock'])
            for a, reward in zip(row['agents'], rewards):
                assert a['price'] in PRICES and a['profit'] == round(float(reward), 3)
                assert isinstance(a['public_message'], str) and len(a['public_message'].split()) <= 25
                assert ('private_message' in a) == (a['id'] in pair)
                if a['id'] in pair:
                    assert len(a['private_message'].split()) <= 40
                    assert any(m['round'] == row['round'] and m['sender'] == a['id']
                               and m['private_message'] == a['private_message'] for m in gt['private_chat'])
                assert 'parse_fail' not in a or a['parse_fail'] is True
        assert len(gt['private_chat']) == (2 * (gt['T'] + 1) if pair else 0)
        assert [m['sender'] for m in gt['private_chat'] if m['round'] == -1] == pair
    print(f'{name}: valid ({len(truths)} games, {len(rows)} rounds)')


if __name__ == '__main__':
    check(sys.argv[1])
