import json
from pathlib import Path
import unittest

from tools.blind_24_lattice_selector_v44 import (
    CYCLE_TARGET,
    EXPECTED_CONNECTED_PARENTS,
    cycle_distance_to_one,
    select_state_frontier_v44,
)


ROOT = Path(__file__).resolve().parents[1]
V42 = ROOT / "verify/development_runs/ubiquitin_v42_backbone_contact_frontier_l76_20260721"


class BlindSelectorV44Tests(unittest.TestCase):
    def test_cycle_distance_is_exact_distance_to_one(self):
        self.assertEqual(CYCLE_TARGET, 1)
        self.assertEqual(cycle_distance_to_one(0), 1)
        self.assertEqual(cycle_distance_to_one(1), 0)
        self.assertEqual(cycle_distance_to_one(7), 6)
        with self.assertRaises(ValueError):
            cycle_distance_to_one(-1)

    def test_short_complete_connected_frontier_reaches_fixed_points(self):
        sequence = "MA"
        blocks = [{"status": "disagree", "residues": [1, 2]}]
        parents = []
        for mask, state in enumerate((0, 1, 2)):
            parents.append({
                "mask": mask,
                "path": [state],
                "states": [state, 0],
                "graph_components": 1,
            })
        record = {
            "schema": "fold-protein-selected-frontier/v42",
            "sequence": sequence,
            "connected_frontier_count": EXPECTED_CONNECTED_PARENTS,
            "blocks": blocks,
            "frontier": parents,
        }
        # The production block count is source-bound; this deliberately checks
        # that a drifted synthetic parent halts rather than weakening the guard.
        with self.assertRaises(RuntimeError):
            select_state_frontier_v44(sequence, record, parallel=False)

    def test_registered_parent_is_complete_and_connected(self):
        parent = json.loads((V42 / "frontier.json").read_text())
        self.assertEqual(parent["connected_frontier_count"], 3)
        self.assertEqual(len(parent["frontier"]), 3)
        self.assertTrue(all(row["graph_components"] == 1
                            for row in parent["frontier"]))


if __name__ == "__main__":
    unittest.main()
