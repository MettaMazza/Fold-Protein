import unittest

from tools.verify_protein_selector_v44_admission import (
    verify_selector_v44_admission,
)


class ProteinSelectorV44AdmissionTests(unittest.TestCase):
    def test_complete_connected_cycle_descent_is_admitted(self):
        row = verify_selector_v44_admission()
        self.assertEqual(row["status"], "verified")
        self.assertEqual(row["connected_parent_count"], 3)
        self.assertEqual(row["paired_state_count"], 576)
        self.assertEqual(row["cycle_rank_target"], 1)


if __name__ == "__main__":
    unittest.main()
