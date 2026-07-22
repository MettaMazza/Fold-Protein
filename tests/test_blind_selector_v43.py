import json
from pathlib import Path
import unittest

from tools.blind_24_lattice_selector_v43 import (
    graph_cycle_rank,
    select_state_frontier_v43,
)


ROOT = Path(__file__).resolve().parents[1]
V42 = ROOT / "verify/development_runs/ubiquitin_v42_backbone_contact_frontier_l76_20260721"


class BlindSelectorV43Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent = json.loads((V42 / "frontier.json").read_text())
        cls.result = select_state_frontier_v43(
            cls.parent["sequence"], cls.parent
        )

    def test_graph_cycle_rank_is_exact(self):
        self.assertEqual(graph_cycle_rank(20, 26, 7), 1)
        self.assertEqual(graph_cycle_rank(18, 26, 9), 1)
        with self.assertRaises(RuntimeError):
            graph_cycle_rank(0, 26, 1)

    def test_complete_cube_is_partitioned_without_target_or_score(self):
        self.assertEqual(self.result["component_cube_candidates"], 8192)
        self.assertEqual(sum(self.result["cycle_rank_census"].values()), 8192)
        self.assertEqual(self.result["one_cycle_frontier_count"], 1082)
        self.assertEqual(len(self.result["frontier"]), 1082)
        self.assertTrue(all(row["graph_cycle_rank"] == 1
                            for row in self.result["frontier"]))

    def test_complete_frontier_preserves_known_blind_masks_without_selecting(self):
        masks = [row["mask"] for row in self.result["frontier"]]
        self.assertIn(524, masks)
        self.assertIn(525, masks)
        self.assertEqual(len(masks), len(set(masks)))


if __name__ == "__main__":
    unittest.main()
