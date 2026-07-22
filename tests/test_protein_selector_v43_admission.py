import unittest

from tools.verify_protein_selector_v43_admission import (
    verify_selector_v43_admission,
)


class ProteinSelectorV43AdmissionTests(unittest.TestCase):
    def test_complete_one_cycle_frontier_is_admitted(self):
        row = verify_selector_v43_admission()
        self.assertEqual(row["status"], "verified")
        self.assertEqual(row["parent_cube_count"], 8192)
        self.assertEqual(row["cycle_rank_target"], 1)
        self.assertEqual(row["one_cycle_frontier_count"], 1082)


if __name__ == "__main__":
    unittest.main()
