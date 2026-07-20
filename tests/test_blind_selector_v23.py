import unittest
from pathlib import Path

from tools.blind_24_lattice_selector_v23 import (
    DOMAIN_CAPACITY, DOMAIN_STATE_COUNT, FRONTIER_CAPACITY,
    select_state_path_v23)


ROOT = Path(__file__).resolve().parents[1]


class BlindSelectorV23Tests(unittest.TestCase):
    def test_complete_domains_and_bidirectional_assembly_execute(self):
        result = select_state_path_v23("MQIFVK", [0] * 6)
        self.assertEqual(len(result["states"]), 6)
        self.assertEqual(len(result["domain_trace"]), 5)
        self.assertTrue(all(
            row["expanded_state_count"] == DOMAIN_STATE_COUNT
            and row["retained_state_count"] == DOMAIN_CAPACITY
            for row in result["domain_trace"]))
        self.assertEqual(
            {row["direction"] for row in result["assembly_trace"]},
            {"forward", "reverse"})
        self.assertLessEqual(result["reconciliation"]["retained_paths"], FRONTIER_CAPACITY)

    def test_import_closure_is_target_incapable(self):
        for relative in (
                "tools/blind_24_lattice_selector_v23.py",
                "tools/global_sequence_constraint_graph_v1.py"):
            source = (ROOT / relative).read_text().lower()
            self.assertNotIn("1ubq", source)
            self.assertNotIn("calculate_tm", source)
            self.assertNotIn("biopython", source)


if __name__ == "__main__":
    unittest.main()
