import json
from pathlib import Path
import unittest

from tools.blind_24_lattice_selector_v38 import DESCENT_ORDERS
from tools.blind_24_lattice_selector_v45 import (
    AXIS_VALUE_COUNT,
    EXPECTED_CONNECTED_PARENTS,
    EXPECTED_DESCENT_ORDERS,
    EXPECTED_FIXED_POINT_TRACES,
)


ROOT = Path(__file__).resolve().parents[1]
V42 = ROOT / "verify/development_runs/ubiquitin_v42_backbone_contact_frontier_l76_20260721"


class BlindSelectorV45Tests(unittest.TestCase):
    def test_complete_boundary_axis_grammar_counts(self):
        self.assertEqual(AXIS_VALUE_COUNT, 24)
        self.assertEqual(EXPECTED_CONNECTED_PARENTS, 3)
        self.assertEqual(EXPECTED_DESCENT_ORDERS, 4)
        self.assertEqual(len(DESCENT_ORDERS), 4)
        self.assertEqual(EXPECTED_FIXED_POINT_TRACES, 12)
        self.assertEqual(
            set(DESCENT_ORDERS),
            {
                ("n_to_c", (0, 1)),
                ("n_to_c", (1, 0)),
                ("c_to_n", (0, 1)),
                ("c_to_n", (1, 0)),
            },
        )

    def test_registered_parent_is_complete_and_connected(self):
        parent = json.loads((V42 / "frontier.json").read_text())
        self.assertEqual(parent["connected_frontier_count"], 3)
        self.assertEqual(len(parent["frontier"]), 3)
        self.assertTrue(all(row["graph_components"] == 1
                            for row in parent["frontier"]))


if __name__ == "__main__":
    unittest.main()
