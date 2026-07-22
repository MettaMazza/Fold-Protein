import unittest

from tools.verify_protein_selector_v45_admission import (
    verify_selector_v45_admission,
)


class ProteinSelectorV45AdmissionTests(unittest.TestCase):
    def test_complete_boundary_axis_frontier_is_admitted(self):
        row = verify_selector_v45_admission()
        self.assertEqual(row["status"], "verified")
        self.assertEqual(row["connected_parent_count"], 3)
        self.assertEqual(row["axis_value_count"], 24)
        self.assertEqual(row["descent_order_count"], 4)
        self.assertEqual(row["fixed_point_trace_count"], 12)
        self.assertEqual(row["cycle_rank_target"], 1)


if __name__ == "__main__":
    unittest.main()
